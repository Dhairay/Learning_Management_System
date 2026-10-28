from django.urls import path
from .views import NotificationListView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications_list'),
    path('<uuid:notification_id>/read/', NotificationListView.as_view(), name='notification_read'),
]
