from rest_framework import serializers
from .models import DiscussionThread, DiscussionReply, CourseReview

class DiscussionReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_avatar = serializers.CharField(source='author.avatar_url', read_only=True)

    class Meta:
        model = DiscussionReply
        fields = ['id', 'thread', 'author', 'author_name', 'author_avatar', 'parent_reply', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class DiscussionThreadSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_avatar = serializers.CharField(source='author.avatar_url', read_only=True)
    replies_count = serializers.ReadOnlyField()
    replies = DiscussionReplySerializer(many=True, read_only=True)

    class Meta:
        model = DiscussionThread
        fields = ['id', 'course', 'author', 'author_name', 'author_avatar', 'title', 'content', 'replies_count', 'replies', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_avatar = serializers.CharField(source='student.avatar_url', read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'student', 'student_name', 'student_avatar', 'rating', 'review_text', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']
