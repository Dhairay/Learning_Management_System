from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, OrganizationMembersView, OrganizationInvitationView

router = DefaultRouter()
router.register('', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('<slug:org_slug>/members/', OrganizationMembersView.as_view(), name='org_members'),
    path('<slug:org_slug>/members/<uuid:membership_id>/roles/', OrganizationMembersView.as_view(), name='org_member_roles'),
    path('<slug:org_slug>/invitations/', OrganizationInvitationView.as_view(), name='org_invitations'),
    path('', include(router.urls)),
]
