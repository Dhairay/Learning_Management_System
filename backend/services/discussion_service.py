from typing import Optional
from core.exceptions import EntityNotFoundError, BusinessRuleViolation, UnauthorizedDomainAction
from repositories.discussion_repository import DiscussionRepository
from repositories.enrollment_repository import EnrollmentRepository
from apps.discussions.models import DiscussionThread, CourseReview

class DiscussionService:
    def __init__(
        self,
        discussion_repo: Optional[DiscussionRepository] = None,
        enrollment_repo: Optional[EnrollmentRepository] = None
    ):
        self.discussion_repo = discussion_repo or DiscussionRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()

    def create_thread(self, course_id: str, title: str, content: str, author) -> DiscussionThread:
        from apps.courses.models import Course
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise EntityNotFoundError(f"Course '{course_id}' not found.")

        if not title or not content:
            raise BusinessRuleViolation("Title and content are required.")

        return self.discussion_repo.create(
            organization=course.organization,
            course=course,
            author=author,
            title=title,
            content=content
        )

    def add_review(self, course_id: str, student_user, rating: int, review_text: str) -> CourseReview:
        from apps.courses.models import Course
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise EntityNotFoundError(f"Course '{course_id}' not found.")

        # Check enrollment
        has_enrollment = self.enrollment_repo.find_active_enrollment(str(student_user.id), str(course.id))
        if not has_enrollment and not student_user.is_staff:
            raise UnauthorizedDomainAction("You must be enrolled in this course to leave a review.")

        if rating < 1 or rating > 5:
            raise BusinessRuleViolation("Rating must be between 1 and 5.")

        review, _ = CourseReview.objects.update_or_create(
            course=course,
            student=student_user,
            defaults={
                'organization': course.organization,
                'rating': rating,
                'review_text': review_text,
                'status': 'PUBLISHED'
            }
        )
        return review
