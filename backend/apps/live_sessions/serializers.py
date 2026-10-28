from rest_framework import serializers
from .models import LiveSession, LiveSessionRegistration, AttendanceRecord

class LiveSessionSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor_membership.user.full_name', read_only=True)
    is_registered = serializers.SerializerMethodField()
    registered_count = serializers.SerializerMethodField()

    class Meta:
        model = LiveSession
        fields = [
            'id', 'course', 'instructor_name', 'title', 'description',
            'provider', 'provider_session_id', 'room_url', 'scheduled_start',
            'scheduled_end', 'status', 'is_registered', 'registered_count', 'created_at'
        ]

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.registrations.filter(enrollment__student_membership__user=request.user).exists()
        return False

    def get_registered_count(self, obj):
        return obj.registrations.count()

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='registration.enrollment.student_membership.user.full_name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student_name', 'joined_at', 'left_at', 'duration_seconds']
