from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    Quiz, Question, AnswerOption, QuizAttempt, QuizResponse,
    Assignment, AssignmentSubmission, AssignmentGrade
)
from .serializers import (
    QuizPublicSerializer, QuizAttemptSerializer,
    AssignmentDetailSerializer, AssignmentSubmissionSerializer,
    AssignmentGradeSerializer
)
from apps.enrollments.models import Enrollment
from apps.learning.services import CourseCompletionService
from apps.accounts.models import OrganizationMembership

class QuizDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__options'), id=quiz_id)
        
        # User attempt history
        enrollment = Enrollment.objects.filter(
            course=quiz.course, student_membership__user=request.user
        ).first()

        past_attempts = []
        if enrollment:
            attempts = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz)
            past_attempts = QuizAttemptSerializer(attempts, many=True).data

        return Response({
            'quiz': QuizPublicSerializer(quiz).data,
            'past_attempts': past_attempts,
            'can_attempt': len(past_attempts) < quiz.max_attempts
        })

class QuizStartAttemptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        enrollment = get_object_or_404(
            Enrollment, course=quiz.course, student_membership__user=request.user, status='ACTIVE'
        )

        existing_attempts_count = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz).count()
        if existing_attempts_count >= quiz.max_attempts:
            return Response({'detail': f'Maximum allowed attempts ({quiz.max_attempts}) reached.'}, status=status.HTTP_400_BAD_REQUEST)

        attempt = QuizAttempt.objects.create(
            enrollment=enrollment,
            quiz=quiz,
            attempt_number=existing_attempts_count + 1,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        return Response(QuizAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)

class QuizSubmitView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, attempt_id):
        attempt = get_object_or_404(QuizAttempt, id=attempt_id)
        if attempt.enrollment.student_membership.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        if attempt.status == 'EVALUATED':
            return Response({'detail': 'This attempt has already been evaluated.'}, status=status.HTTP_400_BAD_REQUEST)

        answers = request.data.get('answers', {}) # dict of question_id: [option_ids]
        questions = attempt.quiz.questions.prefetch_related('options').all()
        
        total_possible_points = sum(q.points for q in questions)
        total_awarded_points = 0.0

        for q in questions:
            q_id_str = str(q.id)
            selected_option_ids = answers.get(q_id_str, [])
            if not isinstance(selected_option_ids, list):
                selected_option_ids = [selected_option_ids] if selected_option_ids else []

            # Check correct answers
            correct_option_ids = [str(opt.id) for opt in q.options.filter(is_correct=True)]
            
            # Simple scoring: exact match of options
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
        passed = percentage_score >= attempt.quiz.pass_percentage

        attempt.score = round(percentage_score, 1)
        attempt.passed = passed
        attempt.status = 'EVALUATED'
        attempt.submitted_at = timezone.now()
        attempt.save()

        # Check course completion eligibility
        CourseCompletionService.record_completion_if_eligible(attempt.enrollment)

        return Response({
            'attempt_id': str(attempt.id),
            'score': attempt.score,
            'passed': attempt.passed,
            'pass_percentage': attempt.quiz.pass_percentage,
            'message': 'Congratulations, you passed!' if passed else 'You did not achieve the passing percentage. You may retry if attempts remain.'
        })

class AssignmentDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        user_submission = None
        enrollment = Enrollment.objects.filter(
            course=assignment.course, student_membership__user=request.user
        ).first()

        if enrollment:
            sub = AssignmentSubmission.objects.filter(
                assignment=assignment, enrollment=enrollment
            ).order_by('-version').first()
            if sub:
                user_submission = AssignmentSubmissionSerializer(sub).data

        return Response({
            'assignment': AssignmentDetailSerializer(assignment).data,
            'submission': user_submission
        })

class AssignmentSubmitView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        enrollment = get_object_or_404(
            Enrollment, course=assignment.course, student_membership__user=request.user, status='ACTIVE'
        )

        content_text = request.data.get('content_text', '')
        file_url = request.data.get('file_url', '')

        if not content_text and not file_url:
            return Response({'detail': 'Either text content or a file upload is required.'}, status=status.HTTP_400_BAD_REQUEST)

        prev_sub = AssignmentSubmission.objects.filter(
            assignment=assignment, enrollment=enrollment
        ).order_by('-version').first()

        next_version = (prev_sub.version + 1) if prev_sub else 1

        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            enrollment=enrollment,
            version=next_version,
            content_text=content_text,
            file_url=file_url,
            status='SUBMITTED'
        )

        return Response(AssignmentSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)

class AssignmentGradeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, submission_id):
        submission = get_object_or_404(AssignmentSubmission, id=submission_id)
        course = submission.assignment.course
        
        # Verify grader is instructor or admin
        membership = OrganizationMembership.objects.filter(
            organization=course.organization,
            user=request.user,
            role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).first()

        if not membership and not request.user.is_staff:
            return Response({'detail': 'Only course instructors or admins can grade submissions.'}, status=status.HTTP_403_FORBIDDEN)

        score = float(request.data.get('score', 0))
        feedback = request.data.get('feedback', '')

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

        # Check course completion eligibility
        CourseCompletionService.record_completion_if_eligible(submission.enrollment)

        return Response(AssignmentGradeSerializer(grade).data)

class CourseAssignmentsListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        assignments = Assignment.objects.filter(course_id=course_id)
        return Response(AssignmentDetailSerializer(assignments, many=True).data)

class InstructorSubmissionsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        submissions = AssignmentSubmission.objects.filter(
            assignment__course=course
        ).select_related('assignment', 'enrollment__student_membership__user', 'grade')
        return Response(AssignmentSubmissionSerializer(submissions, many=True).data)
