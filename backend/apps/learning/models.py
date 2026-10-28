import uuid
from django.db import models
from apps.enrollments.models import Enrollment
from apps.courses.models import Lesson

class LessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed = models.BooleanField(default=False)
    last_position_seconds = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lesson_progress'
        constraints = [
            models.UniqueConstraint(fields=['enrollment', 'lesson'], name='unique_enrollment_lesson_progress')
        ]

    def __str__(self):
        return f"Progress: {self.enrollment.student_membership.user.email} - {self.lesson.title} ({'Done' if self.completed else 'In Progress'})"

class CourseCompletion(models.Model):
    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('REVOKED', 'Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='completion')
    policy_version = models.CharField(max_length=50, default='v1.0')
    completed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')

    class Meta:
        db_table = 'course_completions'

    def __str__(self):
        return f"Completion: {self.enrollment.student_membership.user.email} - {self.enrollment.course.title}"
