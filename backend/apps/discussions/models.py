import uuid
from django.db import models
from apps.accounts.models import User, Organization
from apps.courses.models import Course

class DiscussionThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussion_threads')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'discussion_threads'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.email}"

    @property
    def replies_count(self):
        return self.replies.count()

class DiscussionReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'discussion_replies'
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author.email} on {self.thread.title}"

class CourseReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review_text = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, default='PUBLISHED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'course_reviews'
        constraints = [
            models.UniqueConstraint(fields=['course', 'student'], name='unique_course_student_review')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review ({self.rating} stars) for {self.course.title} by {self.student.email}"
