from rest_framework import serializers
from .models import MediaAsset

class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ['id', 'organization', 'title', 'asset_type', 'storage_key', 'playback_url', 'file', 'duration_seconds', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
