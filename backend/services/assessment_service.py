from typing import Optional, Dict, Any
from django.utils import timezone
from core.exceptions import EntityNotFoundError, BusinessRuleViolation, UnauthorizedDomainAction
from repositories.assessment_repository import AssessmentRepository
from repositories.enrollment_repository import EnrollmentRepository
from apps.assessments.models import Quiz, QuizAttempt, QuizResponse, Assignment, AssignmentSubmission, AssignmentGrade
from apps.accounts.models import OrganizationMembership
from apps.learning.services import CourseCompletionService

class AssessmentService:
    def __init__(
        self,
        assessment_repo: Optional[AssessmentRepository] = None,
        enrollment_repo: Optional[EnrollmentRepository] = None
    ):
        self.assessment_repo = assessment_repo or AssessmentRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()

    def get_quiz_detail(self, quiz_id: str, user):
        quiz = self.assessment_repo.get_quiz_with_questions(quiz_id)
        if not quiz:
            raise EntityNotFoundError(f"Quiz '{quiz_id}' not found.")

        enrollment = self.enrollment_repo.find_active_enrollment(str(user.id), str(quiz.course.id))
        past_attempts = []
        if enrollment:
            attempts = self.assessment_repo.get_user_quiz_attempts(str(enrollment.id), str(quiz.id))
            from apps.assessments.serializers import QuizAttemptSerializer
            past_attempts = QuizAttemptSerializer(attempts, many=True).data

        from apps.assessments.serializers import QuizPublicSerializer
        return {
            'quiz': QuizPublicSerializer(quiz).data,
            'past_attempts': past_attempts,
            'can_attempt': len(past_attempts) < quiz.max_attempts
        }

    def start_quiz_attempt(self, quiz_id: str, user) -> QuizAttempt:
        quiz = self.assessment_repo.find_by_id(quiz_id)
        if not quiz:
            raise EntityNotFoundError(f"Quiz '{quiz_id}' not found.")

        enrollment = self.enrollment_repo.find_active_enrollment(str(user.id), str(quiz.course.id))
        if not enrollment:
            raise UnauthorizedDomainAction("Active course enrollment required.")

        existing_count = self.assessment_repo.get_user_quiz_attempts(str(enrollment.id), str(quiz.id)).count()
        if existing_count >= quiz.max_attempts:
            raise BusinessRuleViolation(f"Maximum allowed attempts ({quiz.max_attempts}) reached.")

        return QuizAttempt.objects.create(
            enrollment=enrollment,
            quiz=quiz,
            attempt_number=existing_count + 1,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )

    def submit_quiz_attempt(self, attempt_id: str, user, answers: Any) -> QuizAttempt:
        attempt = self.assessment_repo.find_attempt(attempt_id)
        if not attempt:
            raise EntityNotFoundError(f"Attempt '{attempt_id}' not found.")

        if attempt.enrollment.student_membership.user != user and not user.is_staff:
            raise UnauthorizedDomainAction("Permission denied.")

        if attempt.status == 'EVALUATED':
            raise BusinessRuleViolation("This attempt has already been submitted and evaluated.")

        quiz = attempt.quiz
        questions = quiz.questions.prefetch_related('options').all()
        total_possible_points = sum(q.points for q in questions)
        total_awarded_points = 0.0

        # answers can be a dict {q_id: [opt_id]} or list of dicts [{'question_id': ..., 'selected_option_id': ...}]
        answers_dict = {}
        if isinstance(answers, dict):
            answers_dict = answers
        elif isinstance(answers, list):
            for item in answers:
                if isinstance(item, dict):
                    q_id = str(item.get('question_id'))
                    opt_id = str(item.get('selected_option_id'))
                    answers_dict[q_id] = [opt_id]

        for q in questions:
            q_id_str = str(q.id)
            selected_option_ids = answers_dict.get(q_id_str, [])
            if not isinstance(selected_option_ids, list):
                selected_option_ids = [selected_option_ids] if selected_option_ids else []
            selected_option_ids = [str(x) for x in selected_option_ids]

            correct_option_ids = [str(opt.id) for opt in q.options.filter(is_correct=True)]

            if set(selected_option_ids) == set(correct_option_ids) and len(correct_option_ids) > 0:
                awarded = float(q.points)
            else:
                awarded = 0.0

            total_awarded_points += awarded
            QuizResponse.objects.create(
                attempt=attempt,
                question=q,
                selected_options=selected_option_ids,
                points_awarded=awarded
            )

        percentage_score = (total_awarded_points / total_possible_points * 100.0) if total_possible_points > 0 else 100.0
        passed = percentage_score >= float(quiz.pass_percentage)

        attempt.score = round(percentage_score, 1)
        attempt.passed = passed
        attempt.status = 'EVALUATED'
        attempt.submitted_at = timezone.now()
        attempt.save()

        # Check course completion eligibility
        CourseCompletionService.record_completion_if_eligible(attempt.enrollment)

        return attempt

    def submit_assignment(self, assignment_id: str, user, content_text: str, file_url: str) -> AssignmentSubmission:
        assignment = self.assessment_repo.get_assignment_detail(assignment_id)
        if not assignment:
            raise EntityNotFoundError(f"Assignment '{assignment_id}' not found.")

        enrollment = self.enrollment_repo.find_active_enrollment(str(user.id), str(assignment.course.id))
        if not enrollment:
            raise UnauthorizedDomainAction("Active course enrollment required.")

        if not content_text and not file_url:
            raise BusinessRuleViolation("Either text content or a file upload is required.")

        prev_sub = self.assessment_repo.get_latest_submission(str(assignment.id), str(enrollment.id))
        next_version = (prev_sub.version + 1) if prev_sub else 1

        return AssignmentSubmission.objects.create(
            assignment=assignment,
            enrollment=enrollment,
            version=next_version,
            content_text=content_text,
            file_url=file_url,
            status='SUBMITTED'
        )

    def grade_assignment(self, submission_id: str, grader_user, score: float, feedback: str) -> AssignmentGrade:
        submission = AssignmentSubmission.objects.select_related('assignment__course__organization', 'enrollment').filter(id=submission_id).first()
        if not submission:
            raise EntityNotFoundError(f"Submission '{submission_id}' not found.")

        course = submission.assignment.course
        membership = OrganizationMembership.objects.filter(
            organization=course.organization,
            user=grader_user,
            role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).first()

        if not membership and not grader_user.is_staff:
            raise UnauthorizedDomainAction("Only instructors or admins can grade submissions.")

        grade, _ = AssignmentGrade.objects.update_or_create(
            submission=submission,
            defaults={
                'grader_membership': membership,
                'score': score,
                'feedback': feedback,
                'graded_at': timezone.now()
            }
        )
        submission.status = 'GRADED'
        submission.save(update_fields=['status'])

        # Check completion eligibility
        CourseCompletionService.record_completion_if_eligible(submission.enrollment)

        return grade
