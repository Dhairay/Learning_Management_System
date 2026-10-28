from rest_framework import views, permissions, serializers
from rest_framework.response import Response
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='actor_user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'target_type', 'target_id', 'actor_email', 'payload', 'created_at']

class AuditLogListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = AuditLog.objects.all()[:50]
        return Response(AuditLogSerializer(logs, many=True).data)
