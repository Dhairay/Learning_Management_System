from django.contrib import admin
from .models import DiscussionThread, DiscussionReply, CourseReview

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'author__email')

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'author', 'created_at')
    search_fields = ('author__email', 'thread__title')

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'status', 'created_at')
    list_filter = ('rating', 'status', 'course')
    search_fields = ('student__email', 'course__title')
