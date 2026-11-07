from typing import Optional
from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.live_sessions.models import LiveSession, LiveSessionRegistration, AttendanceRecord

class LiveSessionRepository(BaseRepository[LiveSession]):
    model = LiveSession

    def get_course_sessions(self, course_id: str) -> QuerySet[LiveSession]:
        return self.model.objects.filter(course_id=course_id).select_related('instructor_membership__user')

    def find_session(self, session_id: str) -> Optional[LiveSession]:
        return self.model.objects.select_related('course__organization').filter(id=session_id).first()

    def register_user(self, session: LiveSession, enrollment) -> LiveSessionRegistration:
        reg, _ = LiveSessionRegistration.objects.get_or_create(
            live_session=session,
            enrollment=enrollment
        )
        return reg

    def record_attendance(self, registration: LiveSessionRegistration) -> AttendanceRecord:
        from django.utils import timezone
        return AttendanceRecord.objects.create(
            registration=registration,
            joined_at=timezone.now()
        )
