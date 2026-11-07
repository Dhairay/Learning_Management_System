from typing import Optional
from core.repositories.base_repository import BaseRepository
from apps.certificates.models import Certificate

class CertificateRepository(BaseRepository[Certificate]):
    model = Certificate

    def find_by_enrollment(self, enrollment_id: str) -> Optional[Certificate]:
        return self.model.objects.filter(enrollment_id=enrollment_id).first()

    def find_by_number(self, certificate_number: str) -> Optional[Certificate]:
        return (
            self.model.objects
            .select_related('organization', 'enrollment__student_membership__user', 'enrollment__course')
            .filter(certificate_number__iexact=certificate_number)
            .first()
        )
