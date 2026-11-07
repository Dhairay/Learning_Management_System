from typing import Optional, Dict, Any
from repositories.audit_repository import AuditRepository
from apps.audit.models import AuditLog

class AuditService:
    def __init__(self, audit_repo: Optional[AuditRepository] = None):
        self.audit_repo = audit_repo or AuditRepository()

    def log_action(self, action: str, target_type: str, target_id: str, actor_user, payload: Optional[Dict[str, Any]] = None):
        return self.audit_repo.create(
            action=action,
            target_type=target_type,
            target_id=target_id,
            actor_user=actor_user,
            payload=payload or {}
        )

    def get_logs(self, limit: int = 50):
        return self.audit_repo.get_recent_logs(limit)
