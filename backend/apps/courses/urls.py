from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryListView, CourseViewSet, CoursePublishView,
    CourseSectionCreateView, SectionLessonCreateView, LessonPlaybackView
)

router = DefaultRouter()
router.register('', CourseViewSet, basename='course')

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('<uuid:course_id>/publish/', CoursePublishView.as_view(), name='course_publish'),
    path('<uuid:course_id>/sections/', CourseSectionCreateView.as_view(), name='course_section_create'),
    path('sections/<uuid:section_id>/lessons/', SectionLessonCreateView.as_view(), name='section_lesson_create'),
    path('lessons/<uuid:lesson_id>/playback/', LessonPlaybackView.as_view(), name='lesson_playback'),
    path('', include(router.urls)),
]
