class DatabaseError(Exception):
    """Raised when a database operation fails."""


class AuthClientError(Exception):
    """Raised when an auth client (i.e. Cognito client) operation fails."""


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""


class AlreadyExistsError(Exception):
    """Raised when creating a resource that already exists."""


class PermissionDeniedError(Exception):
    """Raised when a user is not authorized to perform an action."""


class UserCreationError(Exception):
    """Raised when an error occurs when creating a user."""
