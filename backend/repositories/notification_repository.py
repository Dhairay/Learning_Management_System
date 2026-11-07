from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.notifications.models import Notification

class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    def get_user_notifications(self, user) -> QuerySet[Notification]:
        return self.model.objects.filter(user=user)
