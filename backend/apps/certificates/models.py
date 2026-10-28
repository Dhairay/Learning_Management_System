import uuid
from django.db import models
from apps.accounts.models import Organization
from apps.enrollments.models import Enrollment

class Certificate(models.Model):
    STATUS_CHOICES = [
        ('VALID', 'Valid'),
        ('REVOKED', 'Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=64, unique=True, db_index=True)
    policy_version = models.CharField(max_length=20, default='v1.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VALID')
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certificates'
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.enrollment.student_membership.user.full_name}"

    @property
    def student_name(self):
        return self.enrollment.student_membership.user.full_name

    @property
    def course_title(self):
        return self.enrollment.course.title

    @property
    def organization_name(self):
        return self.organization.name
