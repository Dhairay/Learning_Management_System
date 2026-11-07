"""
Controllers Version Router.
Manages API versioning across controllers (v1, and future v2).
"""
from django.urls import path, include

urlpatterns = [
    path('v1/', include('controllers.v1.urls')),
]
