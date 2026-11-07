from rest_framework import views, status
from rest_framework.response import Response
from core.exceptions import EntityNotFoundError, BusinessRuleViolation, UnauthorizedDomainAction

class BaseController(views.APIView):
    """
    Base controller class with standardized exception mapping for domain errors.
    """
    def handle_exception(self, exc):
        if isinstance(exc, EntityNotFoundError):
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        if isinstance(exc, BusinessRuleViolation):
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exc, UnauthorizedDomainAction):
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)
