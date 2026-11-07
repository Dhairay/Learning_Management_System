from typing import Optional
from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.accounts.models import Organization, OrganizationMembership, Invitation

class OrganizationRepository(BaseRepository[Organization]):
    model = Organization

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        return self.model.objects.filter(slug=slug).first()

    def get_active_organizations(self) -> QuerySet[Organization]:
        return self.model.objects.filter(status='ACTIVE')

    def get_user_memberships(self, user_id: str) -> QuerySet[OrganizationMembership]:
        return OrganizationMembership.objects.filter(
            user_id=user_id, status='ACTIVE'
        ).select_related('organization')

    def get_membership(self, org_id: str, user_id: str) -> Optional[OrganizationMembership]:
        return OrganizationMembership.objects.filter(
            organization_id=org_id, user_id=user_id
        ).select_related('organization', 'user').first()

    def get_members(self, org_slug: str) -> QuerySet[OrganizationMembership]:
        return OrganizationMembership.objects.filter(
            organization__slug=org_slug
        ).select_related('user')

    def get_invitations(self, org_slug: str) -> QuerySet[Invitation]:
        return Invitation.objects.filter(organization__slug=org_slug)

    def find_invitation_by_token(self, token: str) -> Optional[Invitation]:
        return Invitation.objects.filter(token=token).select_related('organization').first()
