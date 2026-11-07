from rest_framework import serializers
from .models import LessonProgress, CourseCompletion

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['id', 'enrollment', 'lesson', 'completed', 'last_position_seconds', 'completed_at']

class CourseCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletion
        fields = ['id', 'enrollment', 'policy_version', 'completed_at', 'status']
