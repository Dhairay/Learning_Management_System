from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor_user', 'organization', 'target_type', 'target_id', 'created_at')
    list_filter = ('action', 'target_type', 'organization')
    search_fields = ('action', 'actor_user__email', 'target_type', 'target_id')
    readonly_fields = ('created_at',)
