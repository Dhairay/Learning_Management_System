from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'enrollment', 'organization', 'status', 'issued_at')
    list_filter = ('status', 'organization')
    search_fields = ('certificate_number', 'enrollment__student_membership__user__email', 'enrollment__course__title')
