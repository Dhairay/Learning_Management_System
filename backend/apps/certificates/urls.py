from django.urls import path
from .views import IssueCertificateView, CertificateDetailView, CertificateVerifyView

urlpatterns = [
    path('enrollments/<uuid:enrollment_id>/certificate/issue/', IssueCertificateView.as_view(), name='issue_certificate'),
    path('certificates/<uuid:certificate_id>/', CertificateDetailView.as_view(), name='certificate_detail'),
    path('certificates/verify/<str:certificate_number>/', CertificateVerifyView.as_view(), name='certificate_verify'),
]
