import uuid
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Certificate
from .serializers import CertificateSerializer, CertificatePublicVerifySerializer
from .services import CertificateGeneratorService
from apps.enrollments.models import Enrollment
from apps.learning.services import CourseCompletionService

class IssueCertificateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        if enrollment.student_membership.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Check existing certificate
        existing_cert = Certificate.objects.filter(enrollment=enrollment).first()
        if existing_cert:
            return Response(CertificateSerializer(existing_cert).data)

        # Evaluate eligibility criteria
        eligible, reason = CourseCompletionService.evaluate_eligibility(enrollment)
        if not eligible:
            return Response({
                'detail': f'Cannot issue certificate: {reason}',
                'eligible': False
            }, status=status.HTTP_400_BAD_REQUEST)

        # Record completion
        CourseCompletionService.record_completion_if_eligible(enrollment)

        # Generate unique certificate number: CERT-ORG-YYYYMMDD-XXXX
        date_str = enrollment.enrolled_at.strftime('%Y%m')
        cert_num = f"CERT-{enrollment.organization.slug[:4].upper()}-{date_str}-{uuid.uuid4().hex[:6].upper()}"

        cert = Certificate.objects.create(
            organization=enrollment.organization,
            enrollment=enrollment,
            certificate_number=cert_num,
            status='VALID'
        )

        # Generate PDF with ReportLab
        CertificateGeneratorService.generate_pdf(cert)

        return Response(CertificateSerializer(cert).data, status=status.HTTP_201_CREATED)

class CertificateDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, certificate_id):
        cert = get_object_or_404(Certificate, id=certificate_id)
        if cert.enrollment.student_membership.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(CertificateSerializer(cert).data)

class CertificateVerifyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, certificate_number):
        cert = Certificate.objects.filter(certificate_number__iexact=certificate_number).first()
        if not cert:
            return Response({
                'valid': False,
                'message': 'No valid certificate found with this verification number.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'valid': cert.status == 'VALID',
            'certificate': CertificatePublicVerifySerializer(cert).data
        })
