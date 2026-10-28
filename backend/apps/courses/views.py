from rest_framework import status, views, viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, Course, CoursePrice, CourseSection, Lesson
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseSectionSerializer, LessonDetailSerializer, LessonSummarySerializer
)
from apps.accounts.models import Organization, OrganizationMembership

class CategoryListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

class CourseViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        org_slug = self.request.headers.get('X-Organization-Slug') or self.request.query_params.get('org_slug')
        qs = Course.objects.all()
        if org_slug:
            qs = qs.filter(organization__slug=org_slug)
        
        # Non-staff and non-instructors only see PUBLISHED courses
        is_instructor_or_admin = False
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or OrganizationMembership.objects.filter(
                user=self.request.user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
            ).exists():
                is_instructor_or_admin = True

        if not is_instructor_or_admin:
            qs = qs.filter(status='PUBLISHED')

        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(title__icontains=search)

        return qs.select_related('organization', 'instructor_membership__user', 'category', 'price').prefetch_related('sections__lessons')

    def perform_create(self, serializer):
        org_slug = self.request.headers.get('X-Organization-Slug') or self.request.data.get('org_slug')
        org = Organization.objects.filter(slug=org_slug).first() or Organization.objects.first()
        
        instructor_membership = None
        if self.request.user.is_authenticated:
            instructor_membership = OrganizationMembership.objects.filter(
                organization=org, user=self.request.user
            ).first()

        import re
        title = serializer.validated_data.get('title')
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        base_slug = slug
        c = 1
        while Course.objects.filter(organization=org, slug=slug).exists():
            slug = f"{base_slug}-{c}"
            c += 1

        course = serializer.save(organization=org, instructor_membership=instructor_membership, slug=slug)

        # Handle price creation if paid
        is_free = self.request.data.get('is_free', True)
        if not is_free:
            amount_minor = int(float(self.request.data.get('price_amount', 49.00)) * 100)
            currency = self.request.data.get('price_currency', 'USD')
            CoursePrice.objects.create(course=course, amount_minor=amount_minor, currency=currency)

class CoursePublishView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        # Check permissions
        membership = OrganizationMembership.objects.filter(
            organization=course.organization, user=request.user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).first()
        if not membership and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        course.status = 'PUBLISHED'
        course.save()
        return Response({'detail': 'Course published successfully!', 'status': course.status})

class CourseSectionCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        title = request.data.get('title')
        if not title:
            return Response({'detail': 'Title is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        position = CourseSection.objects.filter(course=course).count() + 1
        section = CourseSection.objects.create(course=course, title=title, position=position)
        return Response(CourseSectionSerializer(section).data, status=status.HTTP_201_CREATED)

class SectionLessonCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, section_id):
        section = get_object_or_404(CourseSection, id=section_id)
        title = request.data.get('title')
        lesson_type = request.data.get('lesson_type', 'VIDEO')
        content_text = request.data.get('content_text', '')
        duration_seconds = request.data.get('duration_seconds', 300)
        
        position = Lesson.objects.filter(section=section).count() + 1
        lesson = Lesson.objects.create(
            section=section,
            title=title,
            lesson_type=lesson_type,
            content_text=content_text,
            position=position,
            duration_seconds=duration_seconds
        )
        return Response(LessonDetailSerializer(lesson).data, status=status.HTTP_201_CREATED)

class LessonPlaybackView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.section.course
        
        # Verify enrollment or instructor status
        from apps.enrollments.models import Enrollment
        has_enrollment = Enrollment.objects.filter(
            course=course,
            student_membership__user=request.user,
            status='ACTIVE'
        ).exists()

        is_instructor = OrganizationMembership.objects.filter(
            organization=course.organization,
            user=request.user,
            role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).exists()

        if not has_enrollment and not is_instructor and not request.user.is_staff:
            return Response({'detail': 'Active enrollment required to access lesson content.'}, status=status.HTTP_403_FORBIDDEN)

        # Return authorized playback info
        playback_url = ''
        if lesson.media_asset and lesson.media_asset.playback_url:
            playback_url = lesson.media_asset.playback_url
        elif lesson.media_asset and lesson.media_asset.file:
            playback_url = lesson.media_asset.file.url
        else:
            # Demonstration streaming source
            playback_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

        return Response({
            'lesson_id': str(lesson.id),
            'title': lesson.title,
            'lesson_type': lesson.lesson_type,
            'playback_url': playback_url,
            'content_text': lesson.content_text,
            'duration_seconds': lesson.duration_seconds,
            'expires_in_seconds': 3600
        })
