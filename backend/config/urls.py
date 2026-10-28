"""
Django URL Configuration for LMS Enterprise Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 routes
    path('api/v1/auth/', include('apps.accounts.urls_auth')),
    path('api/v1/me/', include('apps.accounts.urls_me')),
    path('api/v1/organizations/', include('apps.accounts.urls_orgs')),
    path('api/v1/courses/', include('apps.courses.urls')),
    path('api/v1/', include('apps.enrollments.urls')),
    path('api/v1/learning/', include('apps.learning.urls')),
    path('api/v1/', include('apps.assessments.urls')),
    path('api/v1/', include('apps.live_sessions.urls')),
    path('api/v1/', include('apps.discussions.urls')),
    path('api/v1/', include('apps.certificates.urls')),
    path('api/v1/media/', include('apps.media_assets.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
