from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.certificate_service import CertificateService
from apps.certificates.models import Certificate
from apps.certificates.serializers import CertificateSerializer, CertificatePublicVerifySerializer

class IssueCertificateController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def __init__(self, cert_service: CertificateService = None, **kwargs):
        super().__init__(**kwargs)
        self.cert_service = cert_service or CertificateService()

    @extend_schema(summary="Issue Course Certificate", tags=['Certificate Controller'])
    def post(self, request, enrollment_id: str):
        cert = self.cert_service.issue_certificate(enrollment_id, request.user)
        return Response(self.serializer_class(cert).data, status=status.HTTP_201_CREATED)

class CertificateDetailController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    @extend_schema(summary="Get Certificate Details", tags=['Certificate Controller'])
    def get(self, request, certificate_id: str):
        cert = Certificate.objects.filter(id=certificate_id).first()
        if not cert:
            return Response({'detail': 'Certificate not found.'}, status=status.HTTP_404_NOT_FOUND)
        if cert.enrollment.student_membership.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.serializer_class(cert).data)

class CertificateVerifyController(BaseController):
    permission_classes = [permissions.AllowAny]
    serializer_class = CertificatePublicVerifySerializer

    def __init__(self, cert_service: CertificateService = None, **kwargs):
        super().__init__(**kwargs)
        self.cert_service = cert_service or CertificateService()

    @extend_schema(summary="Verify Certificate Publicly by Code", tags=['Certificate Controller'])
    def get(self, request, certificate_number: str):
        valid, cert = self.cert_service.verify_certificate(certificate_number)
        if not cert:
            return Response({
                'valid': False,
                'message': 'No valid certificate found with this verification number.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'valid': valid,
            'certificate': self.serializer_class(cert).data
        })
