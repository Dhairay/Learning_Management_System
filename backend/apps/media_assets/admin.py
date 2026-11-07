from django.contrib import admin
from .models import MediaAsset

@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'asset_type', 'status', 'duration_seconds', 'created_at')
    list_filter = ('asset_type', 'status', 'organization')
    search_fields = ('title', 'storage_key')
