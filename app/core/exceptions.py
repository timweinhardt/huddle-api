class DatabaseError(Exception):
    """Raised when a database operation fails."""
    pass

class AuthClientError(Exception):
    """Raised when an auth client (i.e. Cognito client) operation fails."""
    pass

class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass

class AlreadyExistsError(Exception):
    """Raised when creating a resource that already exists."""
    pass

class PermissionDeniedError(Exception):
    """Raised when a user is not authorized to perform an action."""
    pass

class UserCreationError(Exception):
    """Raised when an error occurs when creating a user."""
    pass