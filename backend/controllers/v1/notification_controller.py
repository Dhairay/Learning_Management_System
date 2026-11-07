from rest_framework import permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.notification_service import NotificationService
from apps.notifications.serializers import NotificationSerializer

class NotificationListController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def __init__(self, notif_service: NotificationService = None, **kwargs):
        super().__init__(**kwargs)
        self.notif_service = notif_service or NotificationService()

    @extend_schema(summary="List User Notifications", tags=['Notification Controller'])
    def get(self, request):
        notes = self.notif_service.get_notifications(request.user)
        return Response(self.serializer_class(notes, many=True).data)

    @extend_schema(summary="Mark Notification as Read", tags=['Notification Controller'])
    def patch(self, request, notification_id: str):
        note = self.notif_service.mark_as_read(notification_id, request.user)
        return Response(self.serializer_class(note).data)
