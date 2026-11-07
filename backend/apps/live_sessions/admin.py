from django.contrib import admin
from .models import LiveSession, LiveSessionRegistration, AttendanceRecord

@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'instructor_membership', 'scheduled_start', 'status', 'provider')
    list_filter = ('status', 'provider')
    search_fields = ('title', 'course__title')

@admin.register(LiveSessionRegistration)
class LiveSessionRegistrationAdmin(admin.ModelAdmin):
    list_display = ('live_session', 'enrollment', 'registered_at')
    search_fields = ('enrollment__student_membership__user__email', 'live_session__title')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('registration', 'joined_at', 'duration_seconds')
