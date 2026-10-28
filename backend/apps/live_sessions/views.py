import uuid
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import LiveSession, LiveSessionRegistration, AttendanceRecord
from .serializers import LiveSessionSerializer, AttendanceRecordSerializer
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.accounts.models import OrganizationMembership

class CourseLiveSessionsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        sessions = LiveSession.objects.filter(course=course).select_related('instructor_membership__user')
        return Response(LiveSessionSerializer(sessions, many=True, context={'request': request}).data)

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        membership = OrganizationMembership.objects.filter(
            organization=course.organization, user=request.user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).first()

        if not membership and not request.user.is_staff:
            return Response({'detail': 'Only instructors or admins can schedule live sessions.'}, status=status.HTTP_403_FORBIDDEN)

        title = request.data.get('title')
        description = request.data.get('description', '')
        provider = request.data.get('provider', 'JITSI')
        scheduled_start = request.data.get('scheduled_start')
        scheduled_end = request.data.get('scheduled_end')
        
        session_id = uuid.uuid4().hex[:10]
        # Jitsi public open room or Daily.co
        room_url = f"https://meet.jit.si/LMS-{course.organization.slug}-{session_id}"

        session = LiveSession.objects.create(
            course=course,
            instructor_membership=membership,
            title=title,
            description=description,
            provider=provider,
            provider_session_id=session_id,
            room_url=room_url,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            status='SCHEDULED'
        )
        return Response(LiveSessionSerializer(session, context={'request': request}).data, status=status.HTTP_201_CREATED)

class LiveSessionRegisterView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(LiveSession, id=session_id)
        enrollment = get_object_or_404(
            Enrollment, course=session.course, student_membership__user=request.user, status='ACTIVE'
        )

        reg, created = LiveSessionRegistration.objects.get_or_create(
            live_session=session,
            enrollment=enrollment
        )

        return Response({
            'detail': 'Registered for live class!',
            'registration_id': str(reg.id),
            'live_session_id': str(session.id)
        })

class LiveSessionJoinView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(LiveSession, id=session_id)
        course = session.course
        user = request.user

        is_instructor = OrganizationMembership.objects.filter(
            organization=course.organization, user=user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).exists()

        enrollment = Enrollment.objects.filter(
            course=course, student_membership__user=user, status='ACTIVE'
        ).first()

        if not is_instructor and not enrollment and not user.is_staff:
            return Response({'detail': 'Active enrollment required to join live session.'}, status=status.HTTP_403_FORBIDDEN)

        # Log attendance if student
        if enrollment:
            reg, _ = LiveSessionRegistration.objects.get_or_create(
                live_session=session, enrollment=enrollment
            )
            AttendanceRecord.objects.create(
                registration=reg,
                joined_at=timezone.now()
            )

        # Transition status to LIVE if scheduled
        if session.status == 'SCHEDULED':
            session.status = 'LIVE'
            session.save(update_fields=['status'])

        return Response({
            'session_id': str(session.id),
            'title': session.title,
            'room_url': session.room_url,
            'provider': session.provider,
            'is_instructor': is_instructor
        })
