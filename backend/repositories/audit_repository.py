from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.audit.models import AuditLog

class AuditRepository(BaseRepository[AuditLog]):
    model = AuditLog

    def get_recent_logs(self, limit: int = 50) -> QuerySet[AuditLog]:
        return self.model.objects.all()[:limit]
