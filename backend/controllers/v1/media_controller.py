from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.media_service import MediaService
from apps.media_assets.serializers import MediaAssetSerializer

class MediaUploadSessionController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaAssetSerializer

    def __init__(self, media_service: MediaService = None, **kwargs):
        super().__init__(**kwargs)
        self.media_service = media_service or MediaService()

    @extend_schema(summary="Initiate Media Upload Session", tags=['Media Controller'])
    def post(self, request):
        title = request.data.get('title', 'Uploaded Asset')
        asset_type = request.data.get('asset_type', 'VIDEO')
        org_slug = request.headers.get('X-Organization-Slug') or request.data.get('org_slug')
        playback_url = request.data.get('playback_url', '')
        duration_seconds = request.data.get('duration_seconds', 300)

        asset, upload_url = self.media_service.initiate_upload(
            title=title,
            asset_type=asset_type,
            org_slug=org_slug,
            playback_url=playback_url,
            duration_seconds=duration_seconds
        )
        return Response({
            'asset': self.serializer_class(asset).data,
            'upload_url': upload_url,
            'storage_key': asset.storage_key
        }, status=status.HTTP_201_CREATED)

class MediaAssetDetailController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaAssetSerializer

    @extend_schema(summary="Get Media Asset Detail", tags=['Media Controller'])
    def get(self, request, asset_id: str):
        from repositories.media_repository import MediaRepository
        asset = MediaRepository().find_asset(asset_id)
        if not asset:
            return Response({'detail': 'Media asset not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.serializer_class(asset).data)
