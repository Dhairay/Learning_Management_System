from django.urls import path
from .views import MediaUploadSessionView, MediaAssetDetailView

urlpatterns = [
    path('upload-sessions/', MediaUploadSessionView.as_view(), name='media_upload_session'),
    path('<uuid:asset_id>/status/', MediaAssetDetailView.as_view(), name='media_status'),
]
