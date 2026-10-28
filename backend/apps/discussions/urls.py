from django.urls import path
from .views import CourseDiscussionsView, ThreadRepliesView, CourseReviewsView

urlpatterns = [
    path('courses/<uuid:course_id>/discussions/', CourseDiscussionsView.as_view(), name='course_discussions'),
    path('discussions/<uuid:thread_id>/replies/', ThreadRepliesView.as_view(), name='thread_replies'),
    path('courses/<uuid:course_id>/reviews/', CourseReviewsView.as_view(), name='course_reviews'),
]
