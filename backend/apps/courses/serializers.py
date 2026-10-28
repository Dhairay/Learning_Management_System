from rest_framework import serializers
from .models import Category, Course, CoursePrice, CourseSection, Lesson
from apps.media_assets.serializers import MediaAssetSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']

class CoursePriceSerializer(serializers.ModelSerializer):
    formatted_price = serializers.SerializerMethodField()

    class Meta:
        model = CoursePrice
        fields = ['id', 'currency', 'amount_minor', 'formatted_price', 'is_active']

    def get_formatted_price(self, obj):
        return f"{obj.currency} {obj.amount_minor / 100:.2f}"

class LessonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'position', 'is_required', 'duration_seconds']

class LessonDetailSerializer(serializers.ModelSerializer):
    media_asset = MediaAssetSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'section', 'title', 'lesson_type', 'media_asset', 'content_text', 'position', 'is_required', 'duration_seconds']

class CourseSectionSerializer(serializers.ModelSerializer):
    lessons = LessonSummarySerializer(many=True, read_only=True)

    class Meta:
        model = CourseSection
        fields = ['id', 'course', 'title', 'position', 'lessons']

class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    price = CoursePriceSerializer(read_only=True)
    price_display = serializers.ReadOnlyField()
    total_lessons = serializers.ReadOnlyField()
    total_duration_seconds = serializers.ReadOnlyField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_slug = serializers.CharField(source='organization.slug', read_only=True)
    instructor_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'thumbnail_url',
            'level', 'status', 'visibility', 'is_free', 'price', 'price_display',
            'category', 'organization_name', 'organization_slug', 'instructor_name',
            'total_lessons', 'total_duration_seconds', 'created_at'
        ]

    def get_instructor_name(self, obj):
        if obj.instructor_membership and obj.instructor_membership.user:
            return obj.instructor_membership.user.full_name
        return 'Instructor'

class CourseDetailSerializer(CourseListSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['description', 'sections', 'updated_at']
