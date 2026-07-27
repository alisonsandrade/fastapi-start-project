from datetime import datetime, timezone, timedelta
import hashlib
import secrets

from sqlalchemy import UUID, func, select
from sqlalchemy.orm import Session

from app.auth.exceptions import (
    InvalidRefreshTokenError,
    InvalidSessionError,
    InvalidCredentialsError,
    InactiveUserError,
    PasswordResetTokenError,
)

from app.users.exceptions import (
    PasswordReuseError,
)

from app.auth.models import (
    RefreshTokenModel,
    UserSessionModel,
    PasswordResetTokenModel,
)

from app.core.security import (
    create_access_token,
    verify_password,
    hash_password,
)

from app.users.models import UserModel

from app.users.service import (
    _normalize_email,
    get_user_by_id,
    validate_password,
)

from app.audit.constants import (
    USER_LOGIN,
    USER_LOGOUT,
    PASSWORD_RESET_COMPLETED,
    PASSWORD_RESET_REQUESTED,
)

from app.audit.service import create_audit_log

from app.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# DATETIME HELPERS
# ============================================================================

def utc_now() -> datetime:
    """Return current UTC datetime."""

    return datetime.now(timezone.utc)


# ============================================================================
# TOKEN HELPERS
# ============================================================================

def generate_refresh_token() -> str:
    """Generate a secure refresh token."""

    return secrets.token_urlsafe(64)


def generate_password_reset_token() -> str:
    """Generate a password reset token."""

    return secrets.token_urlsafe(64)


def hash_token(token_value: str) -> str:
    """Generate SHA256 hash from a token."""

    return hashlib.sha256(
        token_value.encode("utf-8")
    ).hexdigest()


# ============================================================================
# USER HELPERS
# ============================================================================

def get_user_by_email(
    db: Session,
    email: str,
) -> UserModel | None:
    """Get user by email."""

    normalized_email = _normalize_email(
        email
    )

    return (
        db.execute(
            select(UserModel).where(
                func.lower(UserModel.email)
                == normalized_email
            )
        )
        .scalar_one_or_none()
    )


# ============================================================================
# JWT HELPERS
# ============================================================================

def build_access_token_claims(
    user: UserModel,
    session: UserSessionModel,
) -> dict:
    """Build access token claims."""

    return {
        "role": user.role,
        "email": user.email,
        "session_id": str(session.id),
    }


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_session(
    db: Session,
    user_id: str,
) -> UserSessionModel:
    """Create a new user session."""

    new_session = UserSessionModel(
        user_id=user_id,
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


def get_session(
    db: Session,
    session_id: str,
) -> UserSessionModel | None:
    """Get user session by id."""

    return db.get(
        UserSessionModel,
        session_id,
    )


def terminate_session(
    db: Session,
    session_id: str,
) -> None:
    """Terminate a session and revoke all refresh tokens."""

    session = get_session(
        db,
        session_id,
    )

    if session is None:
        raise InvalidSessionError(
            "Session not found."
        )

    session.is_active = False

    stmt = select(
        RefreshTokenModel
    ).where(
        RefreshTokenModel.user_session_id == session_id
    )

    refresh_tokens = (
        db.execute(stmt)
        .scalars()
        .all()
    )

    for refresh_token_record in refresh_tokens:
        refresh_token_record.is_revoked = True

    create_audit_log(
        db=db,
        action=USER_LOGOUT,
        resource="UserSession",
        actor_id=str(session.user_id),
        target_id=str(session.user_id),
        resource_id=str(session.id),
        details="User logged out.",
    )

    logger.info(
        "Session terminated: %s",
        session_id,
    )

    db.commit()


# ============================================================================
# REFRESH TOKEN MANAGEMENT
# ============================================================================

def create_refresh_token(
    db: Session,
    user_session_id: str,
) -> str:
    """Create and persist a refresh token."""

    token = generate_refresh_token()

    token_hash = hash_token(token)

    refresh_token_record = RefreshTokenModel(
        user_session_id=user_session_id,
        token_hash=token_hash,
        expires_at=datetime.now() + timedelta(days=30),
    )

    db.add(refresh_token_record)
    db.commit()
    db.refresh(refresh_token_record)

    return token


def get_refresh_token(
    db: Session,
    refresh_token_value: str,
) -> RefreshTokenModel | None:
    """Load refresh token from database."""

    token_hash = hash_token(
        refresh_token_value
    )

    return (
        db.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash
            )
        )
        .scalar_one_or_none()
    )


def revoke_refresh_token(
    db: Session,
    refresh_token_record: RefreshTokenModel,
) -> None:
    """Revoke a refresh token."""

    refresh_token_record.is_revoked = True

    db.commit()


# ============================================================================
# AUTHENTICATION
# ============================================================================

def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> dict:
    """Validate credentials and create session/tokens."""

    user = get_user_by_email(
        db,
        email,
    )

    if (
        not user
        or not verify_password(
            password,
            user.password_hash,
        )
    ):
        raise InvalidCredentialsError(
            "Invalid email or password."
        )

    if not user.is_active:
        raise InactiveUserError(
            "User is inactive."
        )

    session = create_session(
        db=db,
        user_id=str(user.id),
    )

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims=build_access_token_claims(
            user,
            session,
        ),
    )

    refresh_token_value = create_refresh_token(
        db=db,
        user_session_id=session.id,
    )

    create_audit_log(
        db=db,
        action=USER_LOGIN,
        resource="User",
        actor_id=str(user.id),
        target_id=str(user.id),
        resource_id=str(user.id),
        details="User authenticated successfully.",
    )

    logger.info(
        "User authenticated: %s",
        user.email,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
    }


# ============================================================================
# REFRESH FLOW
# ============================================================================

def refresh_session(
    db: Session,
    refresh_token_value: str,
) -> dict:
    """Rotate refresh token and issue new access token."""

    refresh_token_record = get_refresh_token(
        db,
        refresh_token_value,
    )

    if refresh_token_record is None:
        raise InvalidRefreshTokenError(
            "Invalid refresh token."
        )

    if refresh_token_record.is_revoked:
        raise InvalidRefreshTokenError(
            "Refresh token revoked."
        )

    now = datetime.now()

    if refresh_token_record.expires_at < now:
        raise InvalidRefreshTokenError(
            "Refresh token expired."
        )

    session = get_session(
        db,
        refresh_token_record.user_session_id,
    )

    if session is None:
        raise InvalidSessionError()

    if not session.is_active:
        raise InvalidSessionError()

    user = get_user_by_id(
        db,
        session.user_id,
    )

    refresh_token_record.is_revoked = True

    new_refresh_token = generate_refresh_token()

    new_refresh_hash = hash_token(
        new_refresh_token
    )

    new_refresh_token_record = RefreshTokenModel(
        user_session_id=session.id,
        token_hash=new_refresh_hash,
        expires_at=now + timedelta(days=30),
    )

    db.add(new_refresh_token_record)

    db.commit()

    new_access_token = create_access_token(
        subject=str(user.id),
        extra_claims=build_access_token_claims(
            user,
            session,
        ),
    )

    logger.info(
        "Session refreshed: %s",
        session.id,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


# ============================================================================
# PASSWORD RECOVERY
# ============================================================================

def request_password_reset(
    db: Session,
    email: str,
) -> str | None:
    """Generate a password reset token."""

    user = get_user_by_email(
        db,
        email,
    )

    if not user:
        return None

    reset_token = generate_password_reset_token()

    token_hash = hash_token(
        reset_token
    )

    reset_record = PasswordResetTokenModel(
        user_id=str(user.id),
        token_hash=token_hash,
        expires_at=utc_now() + timedelta(hours=1),
    )

    db.add(reset_record)
    db.commit()

    create_audit_log(
        db=db,
        action=PASSWORD_RESET_REQUESTED,
        resource="User",
        actor_id=str(user.id),
        target_id=str(user.id),
        resource_id=str(user.id),
        details="Password reset requested.",
    )

    logger.warning(
        "Password reset token generated | user_id=%s | token=%s",
        user.id,
        reset_token,
    )

    return reset_token


def reset_password(
    db: Session,
    *,
    token: str,
    new_password: str,
) -> None:
    """Reset user password."""

    token_hash = hash_token(
        token
    )

    reset_record = db.execute(
        select(PasswordResetTokenModel).where(
            PasswordResetTokenModel.token_hash
            == token_hash
        )
    ).scalar_one_or_none()

    if not reset_record:
        raise PasswordResetTokenError(
            "Invalid password reset token."
        )

    if reset_record.used:
        raise PasswordResetTokenError(
            "Password reset token already used."
        )

    if reset_record.expires_at < datetime.utcnow():
        raise PasswordResetTokenError(
            "Password reset token expired."
        )

    user = db.execute(
        select(UserModel).where(
            UserModel.id == reset_record.user_id
        )
    ).scalar_one_or_none()

    if not user:
        raise PasswordResetTokenError(
            "User not found."
        )

    if verify_password(
        new_password,
        user.password_hash,
    ):
        raise PasswordReuseError(
            "The new password must be different from the current password."
        )

    validate_password(
        new_password
    )

    user.password_hash = hash_password(
        new_password
    )

    user.updated_at = utc_now()

    reset_record.used = True

    db.commit()

    create_audit_log(
        db=db,
        action=PASSWORD_RESET_COMPLETED,
        resource="User",
        actor_id=str(user.id),
        target_id=str(user.id),
        resource_id=str(user.id),
        details="Password reset completed.",
    )