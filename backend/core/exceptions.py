"""
Core domain and application exceptions.
"""

class DomainException(Exception):
    """Base class for domain-level exceptions."""
    def __init__(self, message: str = "A domain rule error occurred."):
        super().__init__(message)
        self.message = message

class EntityNotFoundError(DomainException):
    """Raised when a requested entity does not exist in the repository."""
    pass

class BusinessRuleViolation(DomainException):
    """Raised when an operation violates a domain invariant or business constraint."""
    pass

class UnauthorizedDomainAction(DomainException):
    """Raised when an actor lacks domain privileges to perform the requested operation."""
    pass

class PrerequisiteUnmetError(DomainException):
    """Raised when course prerequisites or assessment rules are not satisfied."""
    pass
