from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.course_service import CourseService
from apps.courses.models import Course, Category, CoursePrice
from apps.courses.serializers import (
    CourseListSerializer, CourseDetailSerializer, CategorySerializer,
    CourseSectionSerializer, LessonDetailSerializer
)
from apps.accounts.models import Organization, OrganizationMembership

@extend_schema(tags=['Course Controller'])
class CourseViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        service = CourseService()
        org_slug = self.request.headers.get('X-Organization-Slug') or self.request.query_params.get('org_slug')
        category_slug = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        return service.list_courses(
            user=self.request.user,
            org_slug=org_slug,
            category_slug=category_slug,
            search=search
        )

    def perform_create(self, serializer):
        org_slug = self.request.headers.get('X-Organization-Slug') or self.request.data.get('org_slug')
        org = Organization.objects.filter(slug=org_slug).first() or Organization.objects.first()

        instructor_membership = None
        if self.request.user.is_authenticated and org:
            instructor_membership = OrganizationMembership.objects.filter(
                organization=org, user=self.request.user
            ).first()
            if not instructor_membership:
                role = 'PLATFORM_ADMIN' if (self.request.user.is_superuser or self.request.user.is_staff) else 'INSTRUCTOR'
                instructor_membership, _ = OrganizationMembership.objects.get_or_create(
                    organization=org, user=self.request.user, defaults={'role': role, 'status': 'ACTIVE'}
                )

        course = serializer.save(organization=org, instructor_membership=instructor_membership)

        is_free = self.request.data.get('is_free', True)
        if not is_free:
            amount_minor = int(float(self.request.data.get('price_amount', 49.00)) * 100)
            currency = self.request.data.get('price_currency', 'USD')
            CoursePrice.objects.create(course=course, amount_minor=amount_minor, currency=currency)

class CategoryListController(BaseController):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    @extend_schema(summary="List Categories", tags=['Course Controller'])
    def get(self, request):
        return Response(self.serializer_class(Category.objects.all(), many=True).data)

class CoursePublishController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def __init__(self, course_service: CourseService = None, **kwargs):
        super().__init__(**kwargs)
        self.course_service = course_service or CourseService()

    @extend_schema(summary="Publish Course", tags=['Course Controller'])
    def post(self, request, course_id: str):
        course = self.course_service.publish_course(course_id, request.user)
        return Response(CourseDetailSerializer(course).data)

class CourseSectionCreateController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseSectionSerializer

    def __init__(self, course_service: CourseService = None, **kwargs):
        super().__init__(**kwargs)
        self.course_service = course_service or CourseService()

    @extend_schema(summary="Create Section", tags=['Course Controller'])
    def post(self, request, course_id: str):
        title = request.data.get('title')
        section = self.course_service.add_section(course_id, title, request.user)
        return Response(self.serializer_class(section).data, status=status.HTTP_201_CREATED)

class SectionLessonCreateController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonDetailSerializer

    def __init__(self, course_service: CourseService = None, **kwargs):
        super().__init__(**kwargs)
        self.course_service = course_service or CourseService()

    @extend_schema(summary="Create Lesson", tags=['Course Controller'])
    def post(self, request, section_id: str):
        title = request.data.get('title')
        lesson_type = request.data.get('lesson_type', 'VIDEO')
        content_text = request.data.get('content_text', '')
        duration_seconds = request.data.get('duration_seconds', 300)

        lesson = self.course_service.add_lesson(
            section_id, title, lesson_type, content_text, duration_seconds, request.user
        )
        return Response(self.serializer_class(lesson).data, status=status.HTTP_201_CREATED)

class LessonPlaybackController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonDetailSerializer

    def __init__(self, course_service: CourseService = None, **kwargs):
        super().__init__(**kwargs)
        self.course_service = course_service or CourseService()

    @extend_schema(summary="Get Lesson Playback Detail", tags=['Course Controller'])
    def get(self, request, lesson_id: str):
        lesson = self.course_service.verify_lesson_playback_access(lesson_id, request.user)
        return Response(self.serializer_class(lesson).data)
