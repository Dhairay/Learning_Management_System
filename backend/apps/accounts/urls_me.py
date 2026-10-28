from django.urls import path
from .views import MeView, MyOrganizationsView

urlpatterns = [
    path('', MeView.as_view(), name='me_profile'),
    path('organizations/', MyOrganizationsView.as_view(), name='me_organizations'),
]
