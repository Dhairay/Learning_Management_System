import uuid
from typing import Optional
from core.exceptions import EntityNotFoundError
from repositories.media_repository import MediaRepository
from apps.accounts.models import Organization
from apps.media_assets.models import MediaAsset

class MediaService:
    def __init__(self, media_repo: Optional[MediaRepository] = None):
        self.media_repo = media_repo or MediaRepository()

    def initiate_upload(self, title: str, asset_type: str, org_slug: Optional[str], playback_url: str, duration_seconds: int) -> tuple[MediaAsset, str]:
        org = Organization.objects.filter(slug=org_slug).first() or Organization.objects.first()
        storage_key = f"media/{org.slug if org else 'default'}/{uuid.uuid4()}"

        asset = self.media_repo.create(
            organization=org,
            title=title or 'Uploaded Asset',
            asset_type=asset_type or 'VIDEO',
            storage_key=storage_key,
            playback_url=playback_url or '',
            duration_seconds=duration_seconds or 300,
            status='READY'
        )
        upload_url = f"/api/v1/media/mock-upload/{asset.id}/"
        return asset, upload_url
