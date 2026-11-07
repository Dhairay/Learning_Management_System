"""
Django URL Configuration for LMS Enterprise Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='root-redirect'),
    path('admin/', admin.site.urls),

    # OpenAPI 3 Schema & Swagger UI endpoints (supporting all common aliases)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/swagger', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/v1/schema/', SpectacularAPIView.as_view()),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/v1/docs', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/v1/swagger', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/v1/swagger.html', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/v1/', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema')),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('swagger', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('swagger.html', SpectacularSwaggerView.as_view(url_name='schema')),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('docs', RedirectView.as_view(url='/api/docs/', permanent=False)),

    # API routes managed and versioned directly inside controllers
    path('api/', include('controllers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
