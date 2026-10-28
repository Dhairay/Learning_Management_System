from django.utils import timezone
from .models import LessonProgress, CourseCompletion
from apps.courses.models import Lesson
from apps.assessments.models import Quiz, QuizAttempt, Assignment, AssignmentSubmission

class CourseCompletionService:
    @staticmethod
    def evaluate_eligibility(enrollment):
        """
        Calculates whether an enrolled learner has satisfied all criteria for course completion:
        1. Active Enrollment
        2. All Required Lessons Complete
        3. All Required Quizzes Passed
        4. All Required Assignments Passed
        """
        if enrollment.status not in ['ACTIVE', 'COMPLETED']:
            return False, 'Enrollment is not active or completed.'

        course = enrollment.course

        # 1. Required lessons
        required_lessons = Lesson.objects.filter(section__course=course, is_required=True)
        completed_lesson_ids = set(
            LessonProgress.objects.filter(enrollment=enrollment, completed=True).values_list('lesson_id', flat=True)
        )
        for lesson in required_lessons:
            if lesson.id not in completed_lesson_ids:
                return False, f"Incomplete mandatory lesson: '{lesson.title}'."

        # 2. Required Quizzes
        quizzes = Quiz.objects.filter(course=course)
        for quiz in quizzes:
            has_passed = QuizAttempt.objects.filter(
                enrollment=enrollment, quiz=quiz, passed=True
            ).exists()
            if not has_passed:
                return False, f"Passing score not achieved for required quiz: '{quiz.title}'."

        # 3. Required Assignments
        assignments = Assignment.objects.filter(course=course, is_required=True)
        for assignment in assignments:
            passing_submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                enrollment=enrollment,
                status='GRADED',
                grade__score__gte=assignment.passing_score
            ).exists()
            if not passing_submission:
                return False, f"Passing grade not achieved for required assignment: '{assignment.title}'."

        return True, 'All completion and assessment requirements met.'

    @classmethod
    def record_completion_if_eligible(cls, enrollment):
        eligible, reason = cls.evaluate_eligibility(enrollment)
        if eligible:
            completion, created = CourseCompletion.objects.get_or_create(
                enrollment=enrollment,
                defaults={
                    'policy_version': 'v1.0',
                    'status': 'COMPLETED',
                    'completed_at': timezone.now()
                }
            )
            enrollment.status = 'COMPLETED'
            enrollment.save(update_fields=['status'])
            return completion, True, reason
        return None, False, reason
