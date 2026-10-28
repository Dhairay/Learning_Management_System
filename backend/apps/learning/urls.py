from django.urls import path
from .views import UpdateLessonProgressView, RecalculateCompletionView

urlpatterns = [
    path('progress/', UpdateLessonProgressView.as_view(), name='learning_progress_update'),
    path('completion/<uuid:enrollment_id>/recalculate/', RecalculateCompletionView.as_view(), name='learning_recalculate_completion'),
]
