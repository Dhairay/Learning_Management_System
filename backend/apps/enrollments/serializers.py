from rest_framework import serializers
from .models import Order, OrderItem, Payment, Entitlement, Enrollment
from apps.courses.serializers import CourseListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'course_title', 'price_minor', 'currency']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'organization', 'buyer_user', 'currency', 'total_minor', 'status', 'idempotency_key', 'items', 'created_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    student_name = serializers.CharField(source='student_membership.user.full_name', read_only=True)
    student_email = serializers.CharField(source='student_membership.user.email', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'organization', 'course', 'student_name', 'student_email', 'status', 'progress_percentage', 'enrolled_at']
