from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Organization, OrganizationMembership, Invitation, Role

class LoginTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role_name,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        return data

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    role = RoleSerializer(read_only=True)
    role_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar_url', 'bio', 'headline', 'role', 'role_name', 'is_staff', 'is_superuser', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'role_name', 'is_staff', 'is_superuser', 'created_at']

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    role = serializers.ChoiceField(choices=['STUDENT', 'TEACHER', 'INSTRUCTOR'], required=False, default='STUDENT')
    organization_slug = serializers.CharField(required=False, allow_blank=True, default='')

class ProvisionAdminUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    role = serializers.ChoiceField(choices=['SUPER_ADMIN', 'ADMIN', 'ORG_ADMIN', 'PLATFORM_ADMIN'], required=True)
    institute_name = serializers.CharField(required=False, allow_blank=True, default='')
    institute_slug = serializers.CharField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'description', 'logo_url', 'website', 'status', 'settings', 'created_at']
        read_only_fields = ['id', 'created_at']

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ['id', 'organization', 'user', 'role', 'status', 'joined_at']
        read_only_fields = ['id', 'joined_at']

class InvitationSerializer(serializers.ModelSerializer):
    organization_slug = serializers.CharField(source='organization.slug', read_only=True)
    invited_by_email = serializers.CharField(source='invited_by.email', read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'organization', 'organization_slug', 'email', 'role', 'status', 'token', 'expires_at', 'created_at', 'invited_by_email']
        read_only_fields = ['id', 'token', 'status', 'created_at', 'invited_by_email']
