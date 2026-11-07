from typing import Optional
from core.repositories.base_repository import BaseRepository
from apps.media_assets.models import MediaAsset

class MediaRepository(BaseRepository[MediaAsset]):
    model = MediaAsset

    def find_asset(self, asset_id: str) -> Optional[MediaAsset]:
        return self.model.objects.filter(id=asset_id).first()
