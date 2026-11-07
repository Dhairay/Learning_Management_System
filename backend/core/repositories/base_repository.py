from typing import TypeVar, Generic, Type, Optional, List, Any
from django.db.models import Model, QuerySet
from core.exceptions import EntityNotFoundError

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """
    Generic Base Repository encapsulating common Django ORM data access operations.
    """
    model: Type[T]

    def __init__(self, model: Optional[Type[T]] = None):
        if model:
            self.model = model

    def get_queryset(self) -> QuerySet[T]:
        return self.model.objects.all()

    def get_by_id(self, id: Any) -> T:
        try:
            return self.get_queryset().get(id=id)
        except self.model.DoesNotExist:
            raise EntityNotFoundError(f"{self.model.__name__} with ID '{id}' does not exist.")

    def find_by_id(self, id: Any) -> Optional[T]:
        return self.get_queryset().filter(id=id).first()

    def filter(self, **kwargs) -> QuerySet[T]:
        return self.get_queryset().filter(**kwargs)

    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(kwargs.keys()))
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()

    def exists(self, **kwargs) -> bool:
        return self.model.objects.filter(**kwargs).exists()

    def count(self, **kwargs) -> int:
        return self.model.objects.filter(**kwargs).count()
