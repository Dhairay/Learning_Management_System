from django.urls import path
from .views import (
    QuizDetailView, QuizStartAttemptView, QuizSubmitView,
    AssignmentDetailView, AssignmentSubmitView, AssignmentGradeView,
    CourseAssignmentsListView, InstructorSubmissionsView
)

urlpatterns = [
    path('quizzes/<uuid:quiz_id>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('quizzes/<uuid:quiz_id>/attempts/', QuizStartAttemptView.as_view(), name='quiz_start_attempt'),
    path('quiz-attempts/<uuid:attempt_id>/submit/', QuizSubmitView.as_view(), name='quiz_submit'),
    path('assignments/<uuid:assignment_id>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<uuid:assignment_id>/submit/', AssignmentSubmitView.as_view(), name='assignment_submit'),
    path('submissions/<uuid:submission_id>/grade/', AssignmentGradeView.as_view(), name='assignment_grade'),
    path('courses/<uuid:course_id>/assignments/', CourseAssignmentsListView.as_view(), name='course_assignments'),
    path('courses/<uuid:course_id>/submissions/', InstructorSubmissionsView.as_view(), name='instructor_submissions'),
]
