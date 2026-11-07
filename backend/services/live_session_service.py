import uuid
from typing import Optional
from core.exceptions import EntityNotFoundError, UnauthorizedDomainAction
from repositories.live_session_repository import LiveSessionRepository
from repositories.enrollment_repository import EnrollmentRepository
from apps.accounts.models import OrganizationMembership
from apps.live_sessions.models import LiveSession

class LiveSessionService:
    def __init__(
        self,
        live_repo: Optional[LiveSessionRepository] = None,
        enrollment_repo: Optional[EnrollmentRepository] = None
    ):
        self.live_repo = live_repo or LiveSessionRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()

    def schedule_session(self, course_id: str, title: str, description: str, scheduled_start, scheduled_end, provider: str, actor_user) -> LiveSession:
        from apps.courses.models import Course
        course = Course.objects.select_related('organization').filter(id=course_id).first()
        if not course:
            raise EntityNotFoundError(f"Course '{course_id}' not found.")

        membership = OrganizationMembership.objects.filter(
            organization=course.organization, user=actor_user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).first()

        if not membership and not actor_user.is_staff:
            raise UnauthorizedDomainAction("Only instructors or admins can schedule live sessions.")

        session_id = uuid.uuid4().hex[:10]
        room_url = f"https://meet.jit.si/LMS-{course.organization.slug}-{session_id}"

        return self.live_repo.create(
            course=course,
            instructor_membership=membership,
            title=title,
            description=description,
            provider=provider or 'JITSI',
            provider_session_id=session_id,
            room_url=room_url,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            status='SCHEDULED'
        )

    def register_for_session(self, session_id: str, user):
        session = self.live_repo.find_session(session_id)
        if not session:
            raise EntityNotFoundError(f"Live session '{session_id}' not found.")

        enrollment = self.enrollment_repo.find_active_enrollment(str(user.id), str(session.course.id))
        if not enrollment:
            raise UnauthorizedDomainAction("Active enrollment required to register.")

        return self.live_repo.register_user(session, enrollment)

    def join_session(self, session_id: str, user):
        session = self.live_repo.find_session(session_id)
        if not session:
            raise EntityNotFoundError(f"Live session '{session_id}' not found.")

        course = session.course
        is_instructor = OrganizationMembership.objects.filter(
            organization=course.organization, user=user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).exists()

        enrollment = self.enrollment_repo.find_active_enrollment(str(user.id), str(course.id))
        if not is_instructor and not enrollment and not user.is_staff:
            raise UnauthorizedDomainAction("Active enrollment required to join live session.")

        if enrollment:
            reg = self.live_repo.register_user(session, enrollment)
            self.live_repo.record_attendance(reg)

        if session.status == 'SCHEDULED':
            session.status = 'LIVE'
            session.save(update_fields=['status'])

        return {
            'session_id': str(session.id),
            'title': session.title,
            'room_url': session.room_url,
            'provider': session.provider,
            'is_instructor': is_instructor
        }
