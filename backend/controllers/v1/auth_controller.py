from django.db import models
from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.auth_service import AuthService
from apps.accounts.models import User, Role, OrganizationMembership
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import (
    RegisterSerializer,
    UserSerializer,
    OrganizationSerializer,
    OrganizationMembershipSerializer,
    RoleSerializer,
    ProvisionAdminUserSerializer,
    LoginTokenSerializer,
)

class LoginController(TokenObtainPairView):
    serializer_class = LoginTokenSerializer

    @extend_schema(
        summary="Obtain JWT Bearer Token (Login)",
        description="Authenticates user by email and password to receive JWT access (Bearer) and refresh tokens with user role.",
        tags=['Auth Controller']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class IsSuperAdminOrBootstrap(permissions.BasePermission):
    """
    Super Admin required to create Admin and SuperAdmin users.
    If no superadmin exists yet in database, bootstrapping the first SuperAdmin is allowed.
    """
    def has_permission(self, request, view):
        has_super_admin = User.objects.filter(is_superuser=True).exists()
        if not has_super_admin:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        return bool(
            request.user.is_superuser or 
            request.user.is_staff or 
            (request.user.role and request.user.role.name == 'SUPER_ADMIN')
        )

class RolesListController(BaseController):
    permission_classes = [permissions.AllowAny]
    serializer_class = RoleSerializer

    @extend_schema(summary="List Roles", description="Fetches all predefined system roles from the static roles table.", tags=['Auth Controller'])
    def get(self, request):
        roles = Role.objects.all().order_by('name')
        return Response(self.serializer_class(roles, many=True).data)

class RegisterController(BaseController):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def __init__(self, auth_service: AuthService = None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or AuthService()

    @extend_schema(summary="Register User (Student or Teacher)", description="Registers a new student or teacher account and returns JWT tokens. Institute Admin creation is restricted to Super Admins.", tags=['Auth Controller'])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user, tokens = self.auth_service.register_user(serializer.validated_data)
            _, memberships = self.auth_service.get_user_profile(user)
            return Response({
                'user': UserSerializer(user).data,
                'memberships': OrganizationMembershipSerializer(memberships, many=True).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProvisionAdminUserController(BaseController):
    permission_classes = [IsSuperAdminOrBootstrap]
    serializer_class = ProvisionAdminUserSerializer

    def __init__(self, auth_service: AuthService = None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or AuthService()

    @extend_schema(summary="Provision SuperAdmin or Institute Admin User", description="POST API callable by Super Admin to create new SuperAdmin or Institute Admin (owner) users along with their institute.", tags=['Auth Controller'])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user, org, tokens = self.auth_service.provision_admin_user(serializer.validated_data, request.user)
            _, memberships = self.auth_service.get_user_profile(user)
            return Response({
                'detail': f"Successfully provisioned {user.role.display_name if user.role else 'user'} account.",
                'user': UserSerializer(user).data,
                'organization': OrganizationSerializer(org).data if org else None,
                'memberships': OrganizationMembershipSerializer(memberships, many=True).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDirectoryController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(summary="List Users Directory", description="Super Admin can view Admins, Teachers, and Students across the platform. Institute Admins can only view Students and Teachers under their institute.", tags=['Auth Controller'])
    def get(self, request):
        user = request.user
        is_super_admin = (
            user.is_superuser or 
            user.is_staff or 
            (user.role and user.role.name == 'SUPER_ADMIN')
        )

        role_filter = request.query_params.get('role', '').upper()

        if is_super_admin:
            queryset = User.objects.all().select_related('role').prefetch_related('memberships__organization')
            if role_filter:
                if role_filter in ['TEACHER', 'INSTRUCTOR']:
                    queryset = queryset.filter(models.Q(role__name='TEACHER') | models.Q(memberships__role__in=['INSTRUCTOR', 'TEACHER'])).distinct()
                elif role_filter in ['ADMIN', 'ORG_ADMIN']:
                    queryset = queryset.filter(models.Q(role__name='ADMIN') | models.Q(memberships__role__in=['ORG_ADMIN', 'ADMIN'])).distinct()
                elif role_filter == 'STUDENT':
                    queryset = queryset.filter(models.Q(role__name='STUDENT') | models.Q(memberships__role='STUDENT')).distinct()
                elif role_filter in ['SUPER_ADMIN', 'PLATFORM_ADMIN']:
                    queryset = queryset.filter(models.Q(role__name='SUPER_ADMIN') | models.Q(is_superuser=True)).distinct()
            return Response(self.serializer_class(queryset, many=True).data)

        # Check if user is an Institute Admin
        admin_memberships = user.memberships.filter(role__in=['ORG_ADMIN', 'ADMIN', 'PLATFORM_ADMIN'], status='ACTIVE')
        if not admin_memberships.exists():
            return Response({'detail': 'Access denied. Only Super Admins and Institute Admins can view the user directory.'}, status=status.HTTP_403_FORBIDDEN)

        admin_org_ids = admin_memberships.values_list('organization_id', flat=True)
        # Institute Admin can ONLY see Students and Teachers under their institute
        sub_memberships = OrganizationMembership.objects.filter(
            organization_id__in=admin_org_ids,
            role__in=['STUDENT', 'INSTRUCTOR', 'TEACHER'],
            status='ACTIVE'
        ).select_related('user', 'user__role')

        visible_user_ids = sub_memberships.values_list('user_id', flat=True).distinct()
        queryset = User.objects.filter(id__in=visible_user_ids).select_related('role')
        if role_filter:
            if role_filter in ['TEACHER', 'INSTRUCTOR']:
                queryset = queryset.filter(models.Q(role__name='TEACHER') | models.Q(memberships__role__in=['INSTRUCTOR', 'TEACHER'])).distinct()
            elif role_filter == 'STUDENT':
                queryset = queryset.filter(models.Q(role__name='STUDENT') | models.Q(memberships__role='STUDENT')).distinct()

        return Response(self.serializer_class(queryset, many=True).data)

class MeController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def __init__(self, auth_service: AuthService = None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or AuthService()

    @extend_schema(summary="Get Current User Profile", tags=['Auth Controller'])
    def get(self, request):
        user, memberships = self.auth_service.get_user_profile(request.user)
        return Response({
            'user': UserSerializer(user).data,
            'memberships': OrganizationMembershipSerializer(memberships, many=True).data
        })

    @extend_schema(summary="Update Current User Profile", tags=['Auth Controller'])
    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyOrganizationsController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationMembershipSerializer

    def __init__(self, auth_service: AuthService = None, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service or AuthService()

    @extend_schema(summary="List User Organizations", tags=['Auth Controller'])
    def get(self, request):
        _, memberships = self.auth_service.get_user_profile(request.user)
        return Response(self.serializer_class(memberships, many=True).data)
