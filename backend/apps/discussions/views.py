from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import DiscussionThread, DiscussionReply, CourseReview
from .serializers import DiscussionThreadSerializer, DiscussionReplySerializer, CourseReviewSerializer
from apps.courses.models import Course
from apps.enrollments.models import Enrollment

class CourseDiscussionsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        threads = DiscussionThread.objects.filter(course=course).select_related('author').prefetch_related('replies__author')
        return Response(DiscussionThreadSerializer(threads, many=True).data)

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        title = request.data.get('title')
        content = request.data.get('content')
        if not title or not content:
            return Response({'detail': 'Title and content are required.'}, status=status.HTTP_400_BAD_REQUEST)

        thread = DiscussionThread.objects.create(
            organization=course.organization,
            course=course,
            author=request.user,
            title=title,
            content=content
        )
        return Response(DiscussionThreadSerializer(thread).data, status=status.HTTP_201_CREATED)

class ThreadRepliesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, thread_id):
        thread = get_object_or_404(DiscussionThread, id=thread_id)
        content = request.data.get('content')
        parent_id = request.data.get('parent_reply_id')

        if not content:
            return Response({'detail': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        if parent_id:
            parent = DiscussionReply.objects.filter(id=parent_id, thread=thread).first()

        reply = DiscussionReply.objects.create(
            thread=thread,
            author=request.user,
            parent_reply=parent,
            content=content
        )
        return Response(DiscussionReplySerializer(reply).data, status=status.HTTP_201_CREATED)

class CourseReviewsView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        reviews = CourseReview.objects.filter(course=course, status='PUBLISHED').select_related('student')
        
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        
        return Response({
            'course_id': str(course.id),
            'average_rating': round(float(avg_rating), 1),
            'total_reviews': reviews.count(),
            'reviews': CourseReviewSerializer(reviews, many=True).data
        })

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        # Verify enrollment: student must have an active enrollment to leave review
        is_enrolled = Enrollment.objects.filter(
            course=course,
            student_membership__user=request.user
        ).exists()

        if not is_enrolled and not request.user.is_staff:
            return Response({'detail': 'You must be enrolled in this course to leave a review.'}, status=status.HTTP_403_FORBIDDEN)

        rating = int(request.data.get('rating', 5))
        review_text = request.data.get('review_text', '')

        if rating < 1 or rating > 5:
            return Response({'detail': 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        review, created = CourseReview.objects.update_or_create(
            course=course,
            student=request.user,
            defaults={
                'organization': course.organization,
                'rating': rating,
                'review_text': review_text,
                'status': 'PUBLISHED'
            }
        )
        return Response(CourseReviewSerializer(review).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
