from django.urls import path
from .views import CourseLiveSessionsView, LiveSessionRegisterView, LiveSessionJoinView

urlpatterns = [
    path('courses/<uuid:course_id>/live-sessions/', CourseLiveSessionsView.as_view(), name='course_live_sessions'),
    path('live-sessions/<uuid:session_id>/register/', LiveSessionRegisterView.as_view(), name='live_session_register'),
    path('live-sessions/<uuid:session_id>/join/', LiveSessionJoinView.as_view(), name='live_session_join'),
]
