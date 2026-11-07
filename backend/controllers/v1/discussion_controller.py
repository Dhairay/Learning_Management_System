from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.discussion_service import DiscussionService
from apps.discussions.serializers import DiscussionThreadSerializer, DiscussionReplySerializer, CourseReviewSerializer

class CourseDiscussionsController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiscussionThreadSerializer

    def __init__(self, discussion_service: DiscussionService = None, **kwargs):
        super().__init__(**kwargs)
        self.discussion_service = discussion_service or DiscussionService()

    @extend_schema(summary="List Course Discussion Threads", tags=['Discussion Controller'])
    def get(self, request, course_id: str):
        from repositories.discussion_repository import DiscussionRepository
        threads = DiscussionRepository().get_course_threads(course_id)
        return Response(self.serializer_class(threads, many=True).data)

    @extend_schema(summary="Create Discussion Thread", tags=['Discussion Controller'])
    def post(self, request, course_id: str):
        title = request.data.get('title')
        content = request.data.get('content')
        thread = self.discussion_service.create_thread(course_id, title, content, request.user)
        return Response(self.serializer_class(thread).data, status=status.HTTP_201_CREATED)

class ThreadRepliesController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiscussionReplySerializer

    @extend_schema(summary="Reply to Discussion Thread", tags=['Discussion Controller'])
    def post(self, request, thread_id: str):
        from repositories.discussion_repository import DiscussionRepository
        content = request.data.get('content')
        parent_id = request.data.get('parent_reply_id')
        repo = DiscussionRepository()
        thread = repo.find_thread(thread_id)
        if not thread:
            return Response({'detail': 'Thread not found.'}, status=status.HTTP_404_NOT_FOUND)
        reply = repo.create_reply(thread, request.user, content, parent_id)
        return Response(self.serializer_class(reply).data, status=status.HTTP_201_CREATED)

class CourseReviewsController(BaseController):
    serializer_class = CourseReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def __init__(self, discussion_service: DiscussionService = None, **kwargs):
        super().__init__(**kwargs)
        self.discussion_service = discussion_service or DiscussionService()

    @extend_schema(summary="List Course Reviews & Average Rating", tags=['Discussion Controller'])
    def get(self, request, course_id: str):
        from repositories.discussion_repository import DiscussionRepository
        repo = DiscussionRepository()
        avg_rating, total = repo.get_review_stats(course_id)
        reviews = repo.get_course_reviews(course_id)
        return Response({
            'course_id': course_id,
            'average_rating': avg_rating,
            'total_reviews': total,
            'reviews': self.serializer_class(reviews, many=True).data
        })

    @extend_schema(summary="Submit or Update Course Review", tags=['Discussion Controller'])
    def post(self, request, course_id: str):
        rating = int(request.data.get('rating', 5))
        review_text = request.data.get('review_text', '')
        review = self.discussion_service.add_review(course_id, request.user, rating, review_text)
        return Response(self.serializer_class(review).data, status=status.HTTP_200_OK)
