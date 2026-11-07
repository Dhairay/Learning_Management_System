from typing import Optional
from django.utils import timezone
from core.exceptions import EntityNotFoundError, UnauthorizedDomainAction
from repositories.course_repository import CourseRepository
from repositories.enrollment_repository import EnrollmentRepository
from repositories.learning_repository import LearningRepository
from apps.learning.models import LessonProgress, CourseCompletion
from apps.learning.services import CourseCompletionService

class LearningService:
    def __init__(
        self,
        learning_repo: Optional[LearningRepository] = None,
        course_repo: Optional[CourseRepository] = None,
        enrollment_repo: Optional[EnrollmentRepository] = None
    ):
        self.learning_repo = learning_repo or LearningRepository()
        self.course_repo = course_repo or CourseRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()

    def update_progress(self, user, lesson_id: str, completed: bool, last_position: int):
        lesson = self.course_repo.find_lesson(lesson_id)
        if not lesson:
            raise EntityNotFoundError(f"Lesson '{lesson_id}' not found.")

        enrollment = self.enrollment_repo.find_active_enrollment(str(user.id), str(lesson.section.course.id))
        if not enrollment:
            raise UnauthorizedDomainAction("Not enrolled in this course.")

        progress = self.learning_repo.find_progress(enrollment, str(lesson.id))
        if not progress:
            progress = self.learning_repo.create(
                enrollment=enrollment,
                lesson=lesson,
                completed=completed,
                last_position_seconds=last_position,
                completed_at=timezone.now() if completed else None
            )
        else:
            if completed and not progress.completed:
                progress.completed = True
                progress.completed_at = timezone.now()
            progress.last_position_seconds = last_position
            progress.save()

        # Check course completion eligibility
        completion, eligible, msg = CourseCompletionService.record_completion_if_eligible(enrollment)

        return {
            'lesson_id': str(lesson.id),
            'completed': progress.completed,
            'last_position_seconds': progress.last_position_seconds,
            'course_progress_percentage': enrollment.progress_percentage,
            'is_course_completed': eligible,
            'completion_status': msg
        }

    def get_enrollment_curriculum(self, user, enrollment_id: str):
        from apps.enrollments.models import Enrollment
        from apps.courses.models import CourseSection

        enrollment = Enrollment.objects.select_related('course', 'student_membership__user').filter(id=enrollment_id).first()
        if not enrollment:
            raise EntityNotFoundError(f"Enrollment '{enrollment_id}' not found.")

        if enrollment.student_membership.user != user and not user.is_staff:
            raise UnauthorizedDomainAction("Permission denied.")

        course = enrollment.course
        sections = CourseSection.objects.filter(course=course).prefetch_related('lessons', 'lessons__media_asset')
        completed_lessons = self.learning_repo.get_completed_lesson_ids(enrollment)

        curriculum = []
        for sec in sections:
            sec_data = {
                'id': str(sec.id),
                'title': sec.title,
                'position': sec.position,
                'lessons': []
            }
            for les in sec.lessons.all():
                playback = les.media_asset.playback_url if getattr(les, 'media_asset', None) else ''
                is_done = les.id in completed_lessons
                sec_data['lessons'].append({
                    'id': str(les.id),
                    'title': les.title,
                    'lesson_type': les.lesson_type,
                    'position': les.position,
                    'is_required': les.is_required,
                    'duration_seconds': les.duration_seconds,
                    'completed': is_done,
                    'is_completed': is_done,
                    'playback_url': playback,
                    'content_text': les.content_text,
                })
            curriculum.append(sec_data)

        return {
            'enrollment_id': str(enrollment.id),
            'course_id': str(course.id),
            'course_title': course.title,
            'progress_percentage': enrollment.progress_percentage,
            'status': enrollment.status,
            'curriculum': curriculum,
            'sections': curriculum
        }

