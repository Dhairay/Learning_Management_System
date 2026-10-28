from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import LessonProgress, CourseCompletion
from .services import CourseCompletionService
from apps.courses.models import Lesson
from apps.enrollments.models import Enrollment

class UpdateLessonProgressView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        completed = request.data.get('completed', False)
        last_position = request.data.get('last_position_seconds', 0)

        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = Enrollment.objects.filter(
            course=lesson.section.course,
            student_membership__user=request.user
        ).first()

        if not enrollment:
            return Response({'detail': 'Not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN)

        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={
                'completed': completed,
                'last_position_seconds': last_position,
                'completed_at': timezone.now() if completed else None
            }
        )

        if not created:
            if completed and not progress.completed:
                progress.completed = True
                progress.completed_at = timezone.now()
            progress.last_position_seconds = last_position
            progress.save()

        # Check if course completion can now be recorded
        completion, eligible, msg = CourseCompletionService.record_completion_if_eligible(enrollment)

        return Response({
            'lesson_id': str(lesson.id),
            'completed': progress.completed,
            'last_position_seconds': progress.last_position_seconds,
            'course_progress_percentage': enrollment.progress_percentage,
            'is_course_completed': eligible,
            'completion_status': msg
        })

class RecalculateCompletionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        if enrollment.student_membership.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        completion, eligible, reason = CourseCompletionService.record_completion_if_eligible(enrollment)

        return Response({
            'eligible': eligible,
            'reason': reason,
            'progress_percentage': enrollment.progress_percentage,
            'completion_id': str(completion.id) if completion else None
        })
