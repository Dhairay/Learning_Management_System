from django.contrib import admin
from .models import LessonProgress, CourseCompletion

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed', 'last_position_seconds', 'completed_at', 'updated_at')
    list_filter = ('completed',)
    search_fields = ('enrollment__student_membership__user__email', 'lesson__title')

@admin.register(CourseCompletion)
class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'policy_version', 'status', 'completed_at')
    list_filter = ('status',)
    search_fields = ('enrollment__student_membership__user__email', 'enrollment__course__title')
