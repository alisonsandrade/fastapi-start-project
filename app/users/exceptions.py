"""User module exceptions."""


class UserError(Exception):
    """Base exception for user-related errors."""
    pass


class EmailAlreadyExistsError(UserError):
    """Raised when an email is already registered."""
    pass


class UserNotFoundError(UserError):
    """Raised when a user cannot be found."""
    pass


class WeakPasswordError(UserError):
    """Raised when the provided password does not meet security requirements."""
    pass


class InactiveUserError(UserError):
    """Raised when attempting to use an inactive user."""
    pass


class PermissionDeniedError(UserError):
    """Raised when a user does not have permission to perform an action."""
    pass


class PasswordReuseError(UserError):
    """Raised when the new password is the same as the current password."""
    pass


class SelfDeactivationError(UserError):
    """Raised when a user attempts to deactivate theis own account."""
    pass