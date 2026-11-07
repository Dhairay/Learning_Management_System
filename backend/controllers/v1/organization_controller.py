from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.organization_service import OrganizationService
from apps.accounts.models import Organization, OrganizationMembership
from apps.accounts.serializers import OrganizationSerializer, OrganizationMembershipSerializer, InvitationSerializer

@extend_schema(tags=['Organization Controller'])
class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Organization.objects.filter(status='ACTIVE')

    def perform_create(self, serializer):
        org = serializer.save()
        if self.request.user.is_authenticated:
            OrganizationMembership.objects.create(
                organization=org,
                user=self.request.user,
                role='ORG_ADMIN'
            )

class OrganizationMembersController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationMembershipSerializer

    def __init__(self, org_service: OrganizationService = None, **kwargs):
        super().__init__(**kwargs)
        self.org_service = org_service or OrganizationService()

    @extend_schema(summary="List Organization Members", tags=['Organization Controller'])
    def get(self, request, org_slug: str):
        members = self.org_service.get_organization_members(org_slug, request.user)
        return Response(self.serializer_class(members, many=True).data)

    @extend_schema(summary="Update Member Role", tags=['Organization Controller'])
    def patch(self, request, org_slug: str, membership_id: str):
        new_role = request.data.get('role')
        membership = self.org_service.update_member_role(org_slug, membership_id, new_role, request.user)
        return Response(self.serializer_class(membership).data)

class OrganizationInvitationController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer

    def __init__(self, org_service: OrganizationService = None, **kwargs):
        super().__init__(**kwargs)
        self.org_service = org_service or OrganizationService()

    @extend_schema(summary="List Pending Invitations", tags=['Organization Controller'])
    def get(self, request, org_slug: str):
        org = Organization.objects.filter(slug=org_slug).first()
        from repositories.organization_repository import OrganizationRepository
        invites = OrganizationRepository().get_invitations(org_slug)
        return Response(self.serializer_class(invites, many=True).data)

    @extend_schema(summary="Invite Member", tags=['Organization Controller'])
    def post(self, request, org_slug: str):
        email = request.data.get('email')
        role = request.data.get('role', 'STUDENT')
        invite = self.org_service.invite_member(org_slug, email, role, request.user)
        return Response(self.serializer_class(invite).data, status=status.HTTP_201_CREATED)

class AcceptInvitationController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer

    def __init__(self, org_service: OrganizationService = None, **kwargs):
        super().__init__(**kwargs)
        self.org_service = org_service or OrganizationService()

    @extend_schema(summary="Accept Invitation Token", tags=['Organization Controller'])
    def post(self, request):
        token = request.data.get('token')
        message, membership = self.org_service.accept_invitation(token, request.user)
        return Response({
            'detail': message,
            'membership': OrganizationMembershipSerializer(membership).data
        })
