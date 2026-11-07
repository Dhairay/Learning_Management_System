from typing import Optional
from django.db.models import QuerySet, Avg
from core.repositories.base_repository import BaseRepository
from apps.discussions.models import DiscussionThread, DiscussionReply, CourseReview

class DiscussionRepository(BaseRepository[DiscussionThread]):
    model = DiscussionThread

    def get_course_threads(self, course_id: str) -> QuerySet[DiscussionThread]:
        return self.model.objects.filter(course_id=course_id).select_related('author').prefetch_related('replies__author')

    def find_thread(self, thread_id: str) -> Optional[DiscussionThread]:
        return self.model.objects.filter(id=thread_id).first()

    def create_reply(self, thread: DiscussionThread, author, content: str, parent_reply_id: Optional[str] = None) -> DiscussionReply:
        parent = None
        if parent_reply_id:
            parent = DiscussionReply.objects.filter(id=parent_reply_id, thread=thread).first()
        return DiscussionReply.objects.create(
            thread=thread,
            author=author,
            parent_reply=parent,
            content=content
        )

    def get_course_reviews(self, course_id: str) -> QuerySet[CourseReview]:
        return CourseReview.objects.filter(course_id=course_id, status='PUBLISHED').select_related('student')

    def get_review_stats(self, course_id: str) -> tuple[float, int]:
        reviews = self.get_course_reviews(course_id)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        return round(float(avg_rating), 1), reviews.count()
