from rest_framework import permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.learning_service import LearningService
from apps.learning.serializers import LessonProgressSerializer, CourseCompletionSerializer

class UpdateLessonProgressController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonProgressSerializer

    def __init__(self, learning_service: LearningService = None, **kwargs):
        super().__init__(**kwargs)
        self.learning_service = learning_service or LearningService()

    @extend_schema(summary="Update Lesson Completion and Playback Progress", tags=['Learning Controller'])
    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        completed = request.data.get('completed', False)
        last_position = request.data.get('last_position_seconds', 0)

        result = self.learning_service.update_progress(
            user=request.user,
            lesson_id=lesson_id,
            completed=completed,
            last_position=last_position
        )
        return Response(result)

class RecalculateCompletionController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseCompletionSerializer

    @extend_schema(summary="Recalculate Course Completion Eligibility", tags=['Learning Controller'])
    def post(self, request, enrollment_id: str):
        from apps.enrollments.models import Enrollment
        from apps.learning.services import CourseCompletionService
        from core.exceptions import EntityNotFoundError

        enrollment = Enrollment.objects.filter(id=enrollment_id).first()
        if not enrollment:
            raise EntityNotFoundError(f"Enrollment '{enrollment_id}' not found.")

        completion, eligible, msg = CourseCompletionService.record_completion_if_eligible(enrollment)
        return Response({
            'enrollment_id': str(enrollment.id),
            'eligible': eligible,
            'status': msg,
            'completion': CourseCompletionSerializer(completion).data if completion else None
        })
