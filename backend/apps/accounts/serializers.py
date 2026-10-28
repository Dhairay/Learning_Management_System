from rest_framework import serializers
from .models import User, Organization, OrganizationMembership, Invitation

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar_url', 'bio', 'headline', 'is_staff', 'created_at']
        read_only_fields = ['id', 'email', 'is_staff', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    organization_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'organization_name']

    def create(self, validated_data):
        org_name = validated_data.pop('organization_name', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        
        # If organization provided, create or attach default membership
        if org_name:
            import re
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', org_name.lower()).strip('-') or 'org'
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            org = Organization.objects.create(name=org_name, slug=slug)
            OrganizationMembership.objects.create(organization=org, user=user, role='ORG_ADMIN')
        return user

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
