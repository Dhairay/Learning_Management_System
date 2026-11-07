from typing import Optional, Set
from core.repositories.base_repository import BaseRepository
from apps.learning.models import LessonProgress, CourseCompletion
from apps.enrollments.models import Enrollment

class LearningRepository(BaseRepository[LessonProgress]):
    model = LessonProgress

    def get_completed_lesson_ids(self, enrollment: Enrollment) -> Set[str]:
        return set(
            self.model.objects.filter(enrollment=enrollment, completed=True).values_list('lesson_id', flat=True)
        )

    def find_progress(self, enrollment: Enrollment, lesson_id: str) -> Optional[LessonProgress]:
        return self.model.objects.filter(enrollment=enrollment, lesson_id=lesson_id).first()

    def get_or_create_completion(self, enrollment: Enrollment) -> CourseCompletion:
        completion, _ = CourseCompletion.objects.get_or_create(
            enrollment=enrollment,
            defaults={'policy_version': 'v1.0', 'status': 'COMPLETED'}
        )
        return completion

    def find_completion(self, enrollment: Enrollment) -> Optional[CourseCompletion]:
        return CourseCompletion.objects.filter(enrollment=enrollment).first()
