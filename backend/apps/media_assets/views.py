import uuid
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MediaAsset
from .serializers import MediaAssetSerializer
from apps.accounts.models import Organization

class MediaUploadSessionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        title = request.data.get('title', 'Uploaded Asset')
        asset_type = request.data.get('asset_type', 'VIDEO')
        org_slug = request.headers.get('X-Organization-Slug') or request.data.get('org_slug')
        
        org = Organization.objects.filter(slug=org_slug).first() or Organization.objects.first()
        storage_key = f"media/{org.slug if org else 'default'}/{uuid.uuid4()}"
        
        asset = MediaAsset.objects.create(
            organization=org,
            title=title,
            asset_type=asset_type,
            storage_key=storage_key,
            playback_url=request.data.get('playback_url', ''),
            duration_seconds=request.data.get('duration_seconds', 300),
            status='READY'
        )
        return Response({
            'asset': MediaAssetSerializer(asset).data,
            'upload_url': f"/api/v1/media/mock-upload/{asset.id}/",
            'storage_key': storage_key
        }, status=status.HTTP_201_CREATED)

class MediaAssetDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, asset_id):
        asset = get_object_or_404(MediaAsset, id=asset_id)
        return Response(MediaAssetSerializer(asset).data)
