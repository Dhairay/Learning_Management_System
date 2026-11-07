from typing import Optional
from datetime import timedelta
from django.utils import timezone
from core.exceptions import EntityNotFoundError, BusinessRuleViolation, UnauthorizedDomainAction
from repositories.organization_repository import OrganizationRepository
from repositories.user_repository import UserRepository
from apps.accounts.models import Organization, OrganizationMembership, Invitation

class OrganizationService:
    def __init__(
        self,
        org_repo: Optional[OrganizationRepository] = None,
        user_repo: Optional[UserRepository] = None
    ):
        self.org_repo = org_repo or OrganizationRepository()
        self.user_repo = user_repo or UserRepository()

    def get_organization_members(self, org_slug: str, actor_user=None):
        org = self.org_repo.get_by_slug(org_slug)
        if not org:
            raise EntityNotFoundError(f"Organization '{org_slug}' not found.")

        members = self.org_repo.get_members(org_slug)

        if not actor_user or not actor_user.is_authenticated:
            raise UnauthorizedDomainAction("Authentication required to view organization members.")

        is_super_admin = (
            actor_user.is_superuser or 
            actor_user.is_staff or 
            (actor_user.role and actor_user.role.name == 'SUPER_ADMIN')
        )

        if is_super_admin:
            # Super Admin can see everyone: Admins, Teachers, Students
            return members

        # Check if actor is an Admin in this specific organization
        actor_membership = self.org_repo.get_membership(str(org.id), str(actor_user.id))
        is_org_admin = actor_membership and actor_membership.role in ['PLATFORM_ADMIN', 'ORG_ADMIN', 'ADMIN']

        if not is_org_admin:
            raise UnauthorizedDomainAction("Access denied. You can only view members of your own institute.")

        # Institute Admin can ONLY see Students and Teachers under him
        return members.filter(role__in=['STUDENT', 'INSTRUCTOR', 'TEACHER'])

    def update_member_role(self, org_slug: str, membership_id: str, new_role: str, actor_user) -> OrganizationMembership:
        org = self.org_repo.get_by_slug(org_slug)
        if not org:
            raise EntityNotFoundError(f"Organization '{org_slug}' not found.")

        is_super_admin = (
            actor_user.is_superuser or 
            actor_user.is_staff or 
            (actor_user.role and actor_user.role.name == 'SUPER_ADMIN')
        )

        actor_membership = self.org_repo.get_membership(str(org.id), str(actor_user.id))
        is_org_admin = actor_membership and actor_membership.role in ['PLATFORM_ADMIN', 'ORG_ADMIN', 'ADMIN']

        if not is_super_admin and not is_org_admin:
            raise UnauthorizedDomainAction("Only Institute Admins or Super Admins can manage member roles.")

        normalized_role = new_role.upper()
        if normalized_role == 'TEACHER':
            normalized_role = 'INSTRUCTOR'
        elif normalized_role == 'ADMIN':
            normalized_role = 'ORG_ADMIN'

        # Institute Admins can only assign Student or Teacher roles
        if not is_super_admin:
            if normalized_role not in ['STUDENT', 'INSTRUCTOR']:
                raise UnauthorizedDomainAction("Institute Admins can only assign Student or Teacher roles. Only Super Admins can provision Admin accounts.")

        membership = OrganizationMembership.objects.filter(id=membership_id, organization=org).first()
        if not membership:
            raise EntityNotFoundError(f"Membership '{membership_id}' not found.")

        # Institute Admins cannot modify Super Admins or other Admins
        if not is_super_admin and membership.role in ['PLATFORM_ADMIN', 'SUPER_ADMIN', 'ORG_ADMIN', 'ADMIN']:
            raise UnauthorizedDomainAction("Institute Admins cannot modify administrative members.")

        membership.role = normalized_role
        membership.save(update_fields=['role'])

        # Also update user.role
        from apps.accounts.models import Role
        target_role_name = Role.ROLE_TEACHER if normalized_role == 'INSTRUCTOR' else Role.ROLE_STUDENT if normalized_role == 'STUDENT' else Role.ROLE_ADMIN
        role_obj = Role.objects.filter(name=target_role_name).first()
        if role_obj and membership.user:
            membership.user.role = role_obj
            membership.user.save(update_fields=['role'])

        return membership

    def invite_member(self, org_slug: str, email: str, role: str, actor_user) -> Invitation:
        org = self.org_repo.get_by_slug(org_slug)
        if not org:
            raise EntityNotFoundError(f"Organization '{org_slug}' not found.")

        is_super_admin = (
            actor_user.is_superuser or 
            actor_user.is_staff or 
            (actor_user.role and actor_user.role.name == 'SUPER_ADMIN')
        )

        actor_membership = self.org_repo.get_membership(str(org.id), str(actor_user.id))
        is_org_admin = actor_membership and actor_membership.role in ['PLATFORM_ADMIN', 'ORG_ADMIN', 'ADMIN']

        if not is_super_admin and not is_org_admin:
            raise UnauthorizedDomainAction("Only Institute Admins or Super Admins can send invitations.")

        normalized_role = role.upper()
        if normalized_role == 'TEACHER':
            normalized_role = 'INSTRUCTOR'
        elif normalized_role == 'ADMIN':
            normalized_role = 'ORG_ADMIN'

        # Institute Admins can only invite Students and Teachers
        if not is_super_admin and normalized_role not in ['STUDENT', 'INSTRUCTOR']:
            raise UnauthorizedDomainAction("Institute Admins can only invite Students or Teachers. Institute Admin accounts must be created by a Super Admin.")

        # Check if already a member
        existing_user = self.user_repo.get_by_email(email)
        if existing_user and self.org_repo.get_membership(str(org.id), str(existing_user.id)):
            raise BusinessRuleViolation("User is already a member of this organization.")

        return Invitation.objects.create(
            organization=org,
            email=email,
            role=normalized_role,
            invited_by=actor_user,
            expires_at=timezone.now() + timedelta(days=7)
        )

    def accept_invitation(self, token: str, user) -> tuple[str, OrganizationMembership]:
        invite = self.org_repo.find_invitation_by_token(token)
        if not invite or not invite.is_valid():
            raise BusinessRuleViolation("This invitation is invalid or has expired.")

        membership, created = OrganizationMembership.objects.get_or_create(
            organization=invite.organization,
            user=user,
            defaults={'role': invite.role, 'status': 'ACTIVE'}
        )
        if not created:
            membership.role = invite.role
            membership.status = 'ACTIVE'
            membership.save(update_fields=['role', 'status'])

        invite.status = 'ACCEPTED'
        invite.save(update_fields=['status'])
        return f"Successfully joined {invite.organization.name}!", membership
