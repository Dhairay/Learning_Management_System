from django.db import transaction

class BaseService:
    """
    Base service providing common helpers and transactional decorators.
    """
    @staticmethod
    def atomic_transaction():
        return transaction.atomic()
