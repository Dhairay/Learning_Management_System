from django.contrib import admin
from .models import (
    Quiz, Question, AnswerOption, QuizAttempt, QuizResponse,
    Assignment, AssignmentSubmission, AssignmentGrade
)

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 2

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_percentage', 'max_attempts', 'time_limit_minutes', 'created_at')
    search_fields = ('title', 'course__title')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'position', 'points')
    list_filter = ('question_type', 'quiz')
    inlines = [AnswerOptionInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'enrollment', 'attempt_number', 'score', 'passed', 'status', 'started_at')
    list_filter = ('status', 'passed', 'quiz')
    search_fields = ('enrollment__student_membership__user__email', 'quiz__title')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'max_score', 'passing_score', 'due_at', 'is_required')
    search_fields = ('title', 'course__title')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'enrollment', 'version', 'status', 'submitted_at')
    list_filter = ('status', 'assignment')
    search_fields = ('enrollment__student_membership__user__email', 'assignment__title')

@admin.register(AssignmentGrade)
class AssignmentGradeAdmin(admin.ModelAdmin):
    list_display = ('submission', 'grader_membership', 'score', 'graded_at')
    search_fields = ('submission__enrollment__student_membership__user__email',)
