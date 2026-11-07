from typing import Optional
from core.exceptions import EntityNotFoundError
from repositories.notification_repository import NotificationRepository
from apps.notifications.models import Notification

class NotificationService:
    def __init__(self, notif_repo: Optional[NotificationRepository] = None):
        self.notif_repo = notif_repo or NotificationRepository()

    def get_notifications(self, user):
        return self.notif_repo.get_user_notifications(user)

    def mark_as_read(self, notification_id: str, user) -> Notification:
        note = Notification.objects.filter(id=notification_id, user=user).first()
        if not note:
            raise EntityNotFoundError(f"Notification '{notification_id}' not found.")
        note.read = True
        note.save(update_fields=['read'])
        return note
