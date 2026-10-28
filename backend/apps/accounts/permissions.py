from rest_framework import permissions
from .models import OrganizationMembership

def get_membership(request, organization):
    if not request.user or not request.user.is_authenticated:
        return None
    return OrganizationMembership.objects.filter(
        organization=organization,
        user=request.user,
        status='ACTIVE'
    ).first()

class IsPlatformAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))

class IsOrgAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        org = getattr(obj, 'organization', obj if hasattr(obj, 'memberships') else None)
        if not org:
            return False
        membership = get_membership(request, org)
        return bool(membership and membership.role in ['PLATFORM_ADMIN', 'ORG_ADMIN'])

class IsInstructorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        org_slug = request.headers.get('X-Organization-Slug') or request.query_params.get('org_slug')
        if not org_slug:
            # Check if user is instructor in any org
            return OrganizationMembership.objects.filter(
                user=request.user,
                role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR'],
                status='ACTIVE'
            ).exists()
        return OrganizationMembership.objects.filter(
            organization__slug=org_slug,
            user=request.user,
            role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR'],
            status='ACTIVE'
        ).exists()
