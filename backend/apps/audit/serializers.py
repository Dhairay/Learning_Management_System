from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='actor_user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'target_type', 'target_id', 'actor_email', 'payload', 'created_at']
