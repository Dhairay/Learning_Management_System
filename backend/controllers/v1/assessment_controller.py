from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.assessment_service import AssessmentService
from apps.assessments.serializers import (
    QuizPublicSerializer, QuizAttemptSerializer,
    AssignmentDetailSerializer, AssignmentSubmissionSerializer,
    AssignmentGradeSerializer
)

class QuizDetailController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizPublicSerializer

    def __init__(self, assessment_service: AssessmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.assessment_service = assessment_service or AssessmentService()

    @extend_schema(summary="Get Quiz Details & Attempts", tags=['Assessment Controller'])
    def get(self, request, quiz_id: str):
        data = self.assessment_service.get_quiz_detail(quiz_id, request.user)
        return Response(data)

class QuizStartAttemptController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizAttemptSerializer

    def __init__(self, assessment_service: AssessmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.assessment_service = assessment_service or AssessmentService()

    @extend_schema(summary="Start Quiz Attempt", tags=['Assessment Controller'])
    def post(self, request, quiz_id: str):
        attempt = self.assessment_service.start_quiz_attempt(quiz_id, request.user)
        return Response(self.serializer_class(attempt).data, status=status.HTTP_201_CREATED)

class QuizSubmitController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizAttemptSerializer

    def __init__(self, assessment_service: AssessmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.assessment_service = assessment_service or AssessmentService()

    @extend_schema(summary="Submit Quiz Answers", tags=['Assessment Controller'])
    def post(self, request, attempt_id: str):
        answers = request.data.get('answers', [])
        attempt = self.assessment_service.submit_quiz_attempt(attempt_id, request.user, answers)
        return Response(self.serializer_class(attempt).data)

class AssignmentDetailController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignmentDetailSerializer

    @extend_schema(summary="Get Assignment Details & User Submission", tags=['Assessment Controller'])
    def get(self, request, assignment_id: str):
        from apps.assessments.models import Assignment, AssignmentSubmission
        from apps.enrollments.models import Enrollment

        assignment = Assignment.objects.filter(id=assignment_id).first()
        if not assignment:
            return Response({'detail': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

        user_submission = None
        enrollment = Enrollment.objects.filter(course=assignment.course, student_membership__user=request.user).first()
        if enrollment:
            sub = AssignmentSubmission.objects.filter(assignment=assignment, enrollment=enrollment).order_by('-version').first()
            if sub:
                user_submission = AssignmentSubmissionSerializer(sub).data

        return Response({
            'assignment': AssignmentDetailSerializer(assignment).data,
            'submission': user_submission
        })

class AssignmentSubmitController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignmentSubmissionSerializer

    def __init__(self, assessment_service: AssessmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.assessment_service = assessment_service or AssessmentService()

    @extend_schema(summary="Submit Assignment", tags=['Assessment Controller'])
    def post(self, request, assignment_id: str):
        content_text = request.data.get('content_text', '')
        file_url = request.data.get('file_url', '')
        sub = self.assessment_service.submit_assignment(assignment_id, request.user, content_text, file_url)
        return Response(self.serializer_class(sub).data, status=status.HTTP_201_CREATED)

class AssignmentGradeController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignmentGradeSerializer

    def __init__(self, assessment_service: AssessmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.assessment_service = assessment_service or AssessmentService()

    @extend_schema(summary="Grade Student Submission", tags=['Assessment Controller'])
    def post(self, request, submission_id: str):
        score = float(request.data.get('score', 0))
        feedback = request.data.get('feedback', '')
        grade = self.assessment_service.grade_assignment(submission_id, request.user, score, feedback)
        return Response(self.serializer_class(grade).data)

class CourseAssignmentsListController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignmentDetailSerializer

    @extend_schema(summary="List Course Assignments", tags=['Assessment Controller'])
    def get(self, request, course_id: str):
        from repositories.assessment_repository import AssessmentRepository
        assignments = AssessmentRepository().get_course_assignments(course_id)
        return Response(self.serializer_class(assignments, many=True).data)

class InstructorSubmissionsController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignmentSubmissionSerializer

    @extend_schema(summary="List Instructor Submissions for Grading", tags=['Assessment Controller'])
    def get(self, request, course_id: str):
        from repositories.assessment_repository import AssessmentRepository
        submissions = AssessmentRepository().get_course_submissions(course_id)
        return Response(self.serializer_class(submissions, many=True).data)
