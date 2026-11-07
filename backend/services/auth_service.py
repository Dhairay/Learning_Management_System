from typing import Optional, Dict, Any
from rest_framework_simplejwt.tokens import RefreshToken
from core.exceptions import BusinessRuleViolation, EntityNotFoundError
from repositories.user_repository import UserRepository
from repositories.organization_repository import OrganizationRepository
from apps.accounts.models import User, OrganizationMembership

class AuthService:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        org_repo: Optional[OrganizationRepository] = None
    ):
        self.user_repo = user_repo or UserRepository()
        self.org_repo = org_repo or OrganizationRepository()

    def register_user(self, validated_data: Dict[str, Any]) -> tuple[User, Dict[str, str]]:
        import re
        from apps.accounts.models import Organization, OrganizationMembership, Role

        email = validated_data.get('email')
        if self.user_repo.email_exists(email):
            raise BusinessRuleViolation(f"User with email '{email}' already exists.")

        # Guard: Public registration is ONLY for Students and Teachers
        raw_role = validated_data.get('role', 'STUDENT').upper()
        if raw_role in ('ADMIN', 'ORG_ADMIN', 'OWNER', 'SUPER_ADMIN', 'PLATFORM_ADMIN'):
            raise BusinessRuleViolation("Institute and Admin registration can only be provisioned by a Super Admin. Public registration is only available for Students and Teachers.")

        if raw_role in ('TEACHER', 'INSTRUCTOR'):
            membership_role = 'INSTRUCTOR'
            role_code = Role.ROLE_TEACHER
        else:
            membership_role = 'STUDENT'
            role_code = Role.ROLE_STUDENT

        role_obj = Role.objects.filter(name=role_code).first()

        user = self.user_repo.create(
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role_obj,
        )
        user.set_password(validated_data.get('password'))
        user.save()

        # Connect user to institute/organization
        org_slug = validated_data.get('organization_slug', '').strip()
        org = None
        if org_slug:
            org = Organization.objects.filter(slug=org_slug).first()
        if not org:
            org = Organization.objects.filter(status='ACTIVE').first()

        if org:
            OrganizationMembership.objects.get_or_create(
                organization=org,
                user=user,
                defaults={'role': membership_role, 'status': 'ACTIVE'}
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return user, tokens

    def provision_admin_user(self, validated_data: Dict[str, Any], actor_user: Optional[User] = None) -> tuple[User, Optional[Any], Dict[str, str]]:
        import re
        from apps.accounts.models import Organization, OrganizationMembership, Role

        email = validated_data.get('email')
        if self.user_repo.email_exists(email):
            raise BusinessRuleViolation(f"User with email '{email}' already exists.")

        raw_role = validated_data.get('role', 'ADMIN').upper()
        if raw_role in ('SUPER_ADMIN', 'PLATFORM_ADMIN'):
            role_type = 'SUPER_ADMIN'
            role_obj = Role.objects.filter(name=Role.ROLE_SUPER_ADMIN).first()
        elif raw_role in ('ADMIN', 'ORG_ADMIN', 'OWNER'):
            role_type = 'ADMIN'
            role_obj = Role.objects.filter(name=Role.ROLE_ADMIN).first()
        else:
            raise BusinessRuleViolation(f"Provisioning API only supports 'SUPER_ADMIN' and 'ADMIN' roles. Given: '{raw_role}'.")

        is_staff_val = True if role_type == 'SUPER_ADMIN' else False
        is_superuser_val = True if role_type == 'SUPER_ADMIN' else False

        user = self.user_repo.create(
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role_obj,
            is_staff=is_staff_val,
            is_superuser=is_superuser_val,
        )
        user.set_password(validated_data.get('password'))
        user.save()

        org = None
        if role_type == 'ADMIN':
            # Admin is the owner of an institute
            institute_name = validated_data.get('institute_name', '').strip()
            if not institute_name:
                raise BusinessRuleViolation("An institute name ('institute_name') is required to provision an Admin user.")
            
            slug = validated_data.get('institute_slug', '').strip()
            if not slug:
                slug = re.sub(r'[^a-zA-Z0-9]+', '-', institute_name.lower()).strip('-') or 'institute'
            
            base_slug = slug
            counter = 1
            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            org = Organization.objects.create(
                name=institute_name,
                slug=slug,
                description=validated_data.get('description', ''),
                status='ACTIVE'
            )
            OrganizationMembership.objects.create(
                organization=org,
                user=user,
                role='ORG_ADMIN',
                status='ACTIVE'
            )
        else:
            # Super Admin attached to default/active organization with PLATFORM_ADMIN access
            default_org = Organization.objects.filter(status='ACTIVE').first()
            if default_org:
                OrganizationMembership.objects.get_or_create(
                    organization=default_org,
                    user=user,
                    defaults={'role': 'PLATFORM_ADMIN', 'status': 'ACTIVE'}
                )
            org = default_org

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return user, org, tokens

    def get_user_profile(self, user: User) -> tuple[User, Any]:
        memberships = self.org_repo.get_user_memberships(str(user.id))
        return user, memberships

