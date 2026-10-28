import uuid
from django.db import models
from apps.courses.models import Course
from apps.accounts.models import OrganizationMembership
from apps.enrollments.models import Enrollment

class LiveSession(models.Model):
    PROVIDER_CHOICES = [
        ('DAILY_CO', 'Daily.co'),
        ('ZOOM', 'Zoom Video'),
        ('JITSI', 'Jitsi Meet'),
        ('INTERNAL', 'WebRTC Room'),
    ]
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live Now'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_sessions')
    instructor_membership = models.ForeignKey(
        OrganizationMembership, on_delete=models.SET_NULL, null=True, related_name='hosted_sessions'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default='JITSI')
    provider_session_id = models.CharField(max_length=255, blank=True, default='')
    room_url = models.URLField(blank=True, default='')
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'live_sessions'
        ordering = ['scheduled_start']

    def __str__(self):
        return f"{self.title} ({self.status}) - {self.course.title}"

class LiveSessionRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='registrations')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='live_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'live_session_registrations'
        constraints = [
            models.UniqueConstraint(fields=['live_session', 'enrollment'], name='unique_session_enrollment_registration')
        ]

    def __str__(self):
        return f"{self.enrollment.student_membership.user.email} -> {self.live_session.title}"

class AttendanceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey(LiveSessionRegistration, on_delete=models.CASCADE, related_name='attendance_records')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'attendance_records'
        ordering = ['-joined_at']

    def __str__(self):
        return f"Attendance: {self.registration.enrollment.student_membership.user.email} for {self.registration.live_session.title}"
