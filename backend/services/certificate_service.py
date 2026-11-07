import uuid
from typing import Optional
from core.exceptions import EntityNotFoundError, UnauthorizedDomainAction, BusinessRuleViolation
from repositories.certificate_repository import CertificateRepository
from repositories.enrollment_repository import EnrollmentRepository
from apps.certificates.models import Certificate
from apps.certificates.services import CertificateGeneratorService
from apps.learning.services import CourseCompletionService

class CertificateService:
    def __init__(
        self,
        cert_repo: Optional[CertificateRepository] = None,
        enrollment_repo: Optional[EnrollmentRepository] = None
    ):
        self.cert_repo = cert_repo or CertificateRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()

    def issue_certificate(self, enrollment_id: str, actor_user) -> Certificate:
        from apps.enrollments.models import Enrollment
        enrollment = Enrollment.objects.select_related('student_membership__user', 'organization', 'course').filter(id=enrollment_id).first()
        if not enrollment:
            raise EntityNotFoundError(f"Enrollment '{enrollment_id}' not found.")

        if enrollment.student_membership.user != actor_user and not actor_user.is_staff:
            raise UnauthorizedDomainAction("Permission denied.")

        # Check existing certificate
        existing = self.cert_repo.find_by_enrollment(str(enrollment.id))
        if existing:
            return existing

        # Evaluate eligibility criteria
        eligible, reason = CourseCompletionService.evaluate_eligibility(enrollment)
        if not eligible:
            raise BusinessRuleViolation(f"Cannot issue certificate: {reason}")

        # Record completion
        CourseCompletionService.record_completion_if_eligible(enrollment)

        # Generate unique certificate number
        date_str = enrollment.enrolled_at.strftime('%Y%m')
        cert_num = f"CERT-{enrollment.organization.slug[:4].upper()}-{date_str}-{uuid.uuid4().hex[:6].upper()}"

        cert = self.cert_repo.create(
            organization=enrollment.organization,
            enrollment=enrollment,
            certificate_number=cert_num,
            status='VALID'
        )

        # Generate PDF with ReportLab
        CertificateGeneratorService.generate_pdf(cert)

        return cert

    def verify_certificate(self, certificate_number: str) -> tuple[bool, Optional[Certificate]]:
        cert = self.cert_repo.find_by_number(certificate_number)
        if not cert:
            return False, None
        return cert.status == 'VALID', cert
