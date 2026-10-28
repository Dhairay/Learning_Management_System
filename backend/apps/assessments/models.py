import uuid
from django.db import models
from apps.courses.models import Course, Lesson
from apps.enrollments.models import Enrollment
from apps.accounts.models import OrganizationMembership

class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.OneToOneField(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    pass_percentage = models.PositiveIntegerField(default=70)
    max_attempts = models.PositiveIntegerField(default=3)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quizzes'
        verbose_name_plural = 'quizzes'

    def __str__(self):
        return f"Quiz: {self.title} ({self.course.title})"

class Question(models.Model):
    QUESTION_TYPES = [
        ('SINGLE_CHOICE', 'Single Choice'),
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='SINGLE_CHOICE')
    points = models.PositiveIntegerField(default=10)
    position = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'questions'
        ordering = ['position']

    def __str__(self):
        return f"Q{self.position}: {self.text[:50]}"

class AnswerOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'answer_options'

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"

class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('EVALUATED', 'Evaluated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']

    def __str__(self):
        return f"Attempt #{self.attempt_number} by {self.enrollment.student_membership.user.email} - Score: {self.score}%"

class QuizResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.JSONField(default=list)  # list of UUID strings
    points_awarded = models.FloatField(default=0.0)

    class Meta:
        db_table = 'quiz_responses'

class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    lesson = models.OneToOneField(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignment')
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    max_score = models.PositiveIntegerField(default=100)
    passing_score = models.PositiveIntegerField(default=60)
    due_at = models.DateTimeField(null=True, blank=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Assignment: {self.title} ({self.course.title})"

class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('GRADED', 'Graded'),
        ('RESUBMISSION_REQUIRED', 'Resubmission Required'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='assignment_submissions')
    version = models.PositiveIntegerField(default=1)
    content_text = models.TextField(blank=True, default='')
    file_url = models.URLField(blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignment_submissions'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission v{self.version} by {self.enrollment.student_membership.user.email} for {self.assignment.title}"

class AssignmentGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(AssignmentSubmission, on_delete=models.CASCADE, related_name='grade')
    grader_membership = models.ForeignKey(OrganizationMembership, on_delete=models.SET_NULL, null=True)
    score = models.FloatField()
    feedback = models.TextField(blank=True, default='')
    graded_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignment_grades'

    def __str__(self):
        return f"Grade {self.score} for {self.submission}"
