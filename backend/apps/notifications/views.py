from rest_framework import views, permissions, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'read', 'created_at']

class NotificationListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notes = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(notes, many=True).data)

    def patch(self, request, notification_id):
        note = get_object_or_404(Notification, id=notification_id, user=request.user)
        note.read = True
        note.save(update_fields=['read'])
        return Response(NotificationSerializer(note).data)
