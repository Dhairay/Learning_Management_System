from rest_framework import permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.audit_service import AuditService
from apps.audit.serializers import AuditLogSerializer

class AuditLogListController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuditLogSerializer

    def __init__(self, audit_service: AuditService = None, **kwargs):
        super().__init__(**kwargs)
        self.audit_service = audit_service or AuditService()

    @extend_schema(summary="List System Audit Logs (Admin)", tags=['Audit Controller'])
    def get(self, request):
        logs = self.audit_service.get_logs()
        return Response(self.serializer_class(logs, many=True).data)
