from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.live_session_service import LiveSessionService
from apps.live_sessions.serializers import LiveSessionSerializer

class CourseLiveSessionsController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LiveSessionSerializer

    def __init__(self, live_service: LiveSessionService = None, **kwargs):
        super().__init__(**kwargs)
        self.live_service = live_service or LiveSessionService()

    @extend_schema(summary="List Course Live Sessions", tags=['Live Session Controller'])
    def get(self, request, course_id: str):
        from repositories.live_session_repository import LiveSessionRepository
        sessions = LiveSessionRepository().get_course_sessions(course_id)
        return Response(self.serializer_class(sessions, many=True, context={'request': request}).data)

    @extend_schema(summary="Schedule Live Session", tags=['Live Session Controller'])
    def post(self, request, course_id: str):
        title = request.data.get('title')
        description = request.data.get('description', '')
        provider = request.data.get('provider', 'JITSI')
        scheduled_start = request.data.get('scheduled_start')
        scheduled_end = request.data.get('scheduled_end')

        session = self.live_service.schedule_session(
            course_id=course_id,
            title=title,
            description=description,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            provider=provider,
            actor_user=request.user
        )
        return Response(self.serializer_class(session, context={'request': request}).data, status=status.HTTP_201_CREATED)

class LiveSessionRegisterController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LiveSessionSerializer

    def __init__(self, live_service: LiveSessionService = None, **kwargs):
        super().__init__(**kwargs)
        self.live_service = live_service or LiveSessionService()

    @extend_schema(summary="Register for Live Session", tags=['Live Session Controller'])
    def post(self, request, session_id: str):
        reg = self.live_service.register_for_session(session_id, request.user)
        return Response({
            'detail': 'Registered for live class!',
            'registration_id': str(reg.id),
            'live_session_id': str(reg.live_session.id)
        })

class LiveSessionJoinController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LiveSessionSerializer

    def __init__(self, live_service: LiveSessionService = None, **kwargs):
        super().__init__(**kwargs)
        self.live_service = live_service or LiveSessionService()

    @extend_schema(summary="Join Live Session Room", tags=['Live Session Controller'])
    def post(self, request, session_id: str):
        data = self.live_service.join_session(session_id, request.user)
        return Response(data)
