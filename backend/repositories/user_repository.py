from typing import Optional
from core.repositories.base_repository import BaseRepository
from apps.accounts.models import User

class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> Optional[User]:
        return self.model.objects.filter(email__iexact=email).first()

    def email_exists(self, email: str) -> bool:
        return self.model.objects.filter(email__iexact=email).exists()
