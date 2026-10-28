from rest_framework import status, views, viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import User, Organization, OrganizationMembership, Invitation
from .serializers import (
    UserSerializer, RegisterSerializer,
    OrganizationSerializer, OrganizationMembershipSerializer,
    InvitationSerializer
)

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_data = UserSerializer(request.user).data
        memberships = OrganizationMembership.objects.filter(
            user=request.user, status='ACTIVE'
        ).select_related('organization')
        memberships_data = OrganizationMembershipSerializer(memberships, many=True).data

        return Response({
            'user': user_data,
            'memberships': memberships_data,
        })

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyOrganizationsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        memberships = OrganizationMembership.objects.filter(
            user=request.user, status='ACTIVE'
        ).select_related('organization')
        return Response(OrganizationMembershipSerializer(memberships, many=True).data)

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        # Platform admin sees all, others see organizations where they are members or public active ones
        return Organization.objects.filter(status='ACTIVE')

    def perform_create(self, serializer):
        org = serializer.save()
        if self.request.user.is_authenticated:
            OrganizationMembership.objects.create(
                organization=org,
                user=self.request.user,
                role='ORG_ADMIN'
            )

class OrganizationMembersView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_slug):
        org = get_object_or_404(Organization, slug=org_slug)
        members = OrganizationMembership.objects.filter(organization=org).select_related('user')
        return Response(OrganizationMembershipSerializer(members, many=True).data)

    def patch(self, request, org_slug, membership_id):
        org = get_object_or_404(Organization, slug=org_slug)
        # Verify requester is OrgAdmin
        is_admin = OrganizationMembership.objects.filter(
            organization=org, user=request.user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN']
        ).exists()
        if not is_admin and not request.user.is_staff:
            return Response({'detail': 'Only Organization Admins can manage roles.'}, status=status.HTTP_403_FORBIDDEN)

        membership = get_object_or_404(OrganizationMembership, id=membership_id, organization=org)
        new_role = request.data.get('role')
        if new_role in dict(OrganizationMembership.ROLE_CHOICES):
            membership.role = new_role
            membership.save()
            return Response(OrganizationMembershipSerializer(membership).data)
        return Response({'detail': 'Invalid role choice.'}, status=status.HTTP_400_BAD_REQUEST)

class OrganizationInvitationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_slug):
        org = get_object_or_404(Organization, slug=org_slug)
        invites = Invitation.objects.filter(organization=org)
        return Response(InvitationSerializer(invites, many=True).data)

    def post(self, request, org_slug):
        org = get_object_or_404(Organization, slug=org_slug)
        is_admin = OrganizationMembership.objects.filter(
            organization=org, user=request.user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN']
        ).exists()
        if not is_admin and not request.user.is_staff:
            return Response({'detail': 'Only Organization Admins can send invitations.'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        role = request.data.get('role', 'STUDENT')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already a member
        existing_user = User.objects.filter(email=email).first()
        if existing_user and OrganizationMembership.objects.filter(organization=org, user=existing_user).exists():
            return Response({'detail': 'User is already a member of this organization.'}, status=status.HTTP_400_BAD_REQUEST)

        invite = Invitation.objects.create(
            organization=org,
            email=email,
            role=role,
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        return Response(InvitationSerializer(invite).data, status=status.HTTP_201_CREATED)

class AcceptInvitationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'detail': 'Invitation token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        invite = get_object_or_404(Invitation, token=token)
        if not invite.is_valid():
            return Response({'detail': 'This invitation is no longer valid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        membership, created = OrganizationMembership.objects.get_or_create(
            organization=invite.organization,
            user=request.user,
            defaults={'role': invite.role, 'status': 'ACTIVE'}
        )
        if not created:
            membership.role = invite.role
            membership.status = 'ACTIVE'
            membership.save()

        invite.status = 'ACCEPTED'
        invite.save()

        return Response({
            'detail': f'Successfully joined {invite.organization.name}!',
            'membership': OrganizationMembershipSerializer(membership).data
        })
