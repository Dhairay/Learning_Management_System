from typing import Optional
from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.assessments.models import Quiz, QuizAttempt, Assignment, AssignmentSubmission, AssignmentGrade

class AssessmentRepository(BaseRepository[Quiz]):
    model = Quiz

    def get_quiz_with_questions(self, quiz_id: str) -> Optional[Quiz]:
        return self.model.objects.prefetch_related('questions__options').filter(id=quiz_id).first()

    def get_user_quiz_attempts(self, enrollment_id: str, quiz_id: str) -> QuerySet[QuizAttempt]:
        return QuizAttempt.objects.filter(enrollment_id=enrollment_id, quiz_id=quiz_id)

    def find_attempt(self, attempt_id: str) -> Optional[QuizAttempt]:
        return QuizAttempt.objects.select_related('enrollment__student_membership__user', 'quiz').filter(id=attempt_id).first()

    def get_assignment_detail(self, assignment_id: str) -> Optional[Assignment]:
        return Assignment.objects.select_related('course').filter(id=assignment_id).first()

    def get_latest_submission(self, assignment_id: str, enrollment_id: str) -> Optional[AssignmentSubmission]:
        return AssignmentSubmission.objects.filter(
            assignment_id=assignment_id, enrollment_id=enrollment_id
        ).order_by('-version').first()

    def get_course_assignments(self, course_id: str) -> QuerySet[Assignment]:
        return Assignment.objects.filter(course_id=course_id)

    def get_course_submissions(self, course_id: str) -> QuerySet[AssignmentSubmission]:
        return AssignmentSubmission.objects.filter(
            assignment__course_id=course_id
        ).select_related('assignment', 'enrollment__student_membership__user', 'grade')
