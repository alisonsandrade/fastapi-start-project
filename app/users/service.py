"""Users service layer.

Business rules for user identity and management.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)

from app.rbac.seed import get_role_by_name
from app.rbac.models import RoleModel

from app.users.exceptions import (
    EmailAlreadyExistsError,
    WeakPasswordError,
    UserNotFoundError,
    PasswordReuseError,
)
from app.auth.exceptions import InvalidCredentialsError
from app.users.models import UserModel, UserRole

from app.audit.constants import (
    USER_CREATED,
    PROFILE_UPDATED,
    PASSWORD_CHANGED,
    USER_SOFT_DELETED,
    USER_HARD_DELETED,
)

from app.core.logging import get_logger
logger = get_logger(__name__)

from app.audit.service import create_audit_log


PASSWORD_MIN_LENGTH = 8


# ============================================================================
# VALIDATIONS
# ============================================================================

def validate_password(password: str) -> None:
    """Validate password strength."""

    if len(password) < PASSWORD_MIN_LENGTH:
        raise WeakPasswordError(
            f"Password must contain at least {PASSWORD_MIN_LENGTH} characters."
        )

    if not any(char.isupper() for char in password):
        raise WeakPasswordError(
            "Password must contain at least one uppercase letter."
        )

    if not any(char.islower() for char in password):
        raise WeakPasswordError(
            "Password must contain at least one lowercase letter."
        )

    if not any(char.isdigit() for char in password):
        raise WeakPasswordError(
            "Password must contain at least one number."
        )

    if not any(not char.isalnum() for char in password):
        raise WeakPasswordError(
            "Password must contain at least one special character."
        )


def _normalize_email(email: str) -> str:
    """Normalize email address."""

    return email.strip().lower()


# ============================================================================
# USER OPERATIONS
# ============================================================================

def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role_name: str = "user",
    phone: str | None = None,
    avatar_url: str | None = None,
    job_title: str | None = None,
    bio: str | None = None,
) -> UserModel:
    """Create a new user."""

    normalized_email = _normalize_email(email)

    validate_password(password)

    existing_user = db.execute(
        select(UserModel).where(
            func.lower(UserModel.email) == normalized_email
        )
    ).scalar_one_or_none()

    if existing_user:
        raise EmailAlreadyExistsError(
            f"Email '{normalized_email}' is already registered."
        )

    role = get_role_by_name(db, role_name)
    if role is None:
        raise ValueError(f"Role '{role_name}' not found. Run the RBAC seed first.")

    new_user = UserModel(
        name=name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        role_id=role.id,
        phone=phone,
        avatar_url=avatar_url,
        job_title=job_title,
        bio=bio,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_audit_log(
        db=db,
        action=USER_CREATED,
        resource="User",
        actor_id=str(new_user.id),
        target_id=str(new_user.id),
        resource_id=str(new_user.id),
        details="User account created"
    )

    logger.info(f"User created: {new_user.email}")

    return new_user


def get_user_by_id(
    db: Session,
    user_id: str,
) -> UserModel:
    """Get user by id."""

    user = db.execute(
        select(UserModel).where(
            UserModel.id == str(user_id)
        )
    ).scalar_one_or_none()

    if not user:
        raise UserNotFoundError(
            f"User with id '{user_id}' was not found."
        )

    return user


def list_users(
    db: Session,
    *,
    role: str | None = None,
    active_only: bool | None = True,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[UserModel], int]:
    """List users."""

    stmt = select(UserModel)
    count_stmt = select(func.count(UserModel.id))

    if active_only is not None:
        stmt = stmt.where(
            UserModel.is_active.is_(active_only)
        )

        count_stmt = count_stmt.where(
            UserModel.is_active.is_(active_only)
        )

    if role:
        stmt = stmt.join(RoleModel).where(
            func.lower(RoleModel.name) == role.lower()
        )
        count_stmt = count_stmt.join(RoleModel).where(
            func.lower(RoleModel.name) == role.lower()
        )

    stmt = stmt.order_by(
        UserModel.name
    ).offset(skip).limit(limit)

    items = list(
        db.execute(stmt)
        .scalars()
        .all()
    )

    total = int(
        db.execute(count_stmt)
        .scalar_one()
    )

    return items, total


def update_current_user(
    db: Session,
    user: UserModel,
    *,
    name: str | None = None,
    phone: str | None = None,
    avatar_url: str | None = None,
    job_title: str | None = None,
    bio: str | None = None,
) -> UserModel:
    """Update current user's frofile"""

    if name is not None:
        user.name = name.strip()

    if phone is not None:
        user.phone = phone

    if avatar_url is not None:
        user.avatar_url = avatar_url

    if job_title is not None:
        user.job_title = job_title

    if bio is not None:
        user.bio = bio

    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action=PROFILE_UPDATED,
        resource="User",
        actor_id=str(user.id),
        target_id=str(user.id),
        resource_id=str(user.id),
        details="Profile information updated.",
    )

    logger.info(f"User updated: {user.email}")

    return user


def change_password(
    db: Session,
    user: UserModel,
    current_password: str,
    new_password: str,
) -> UserModel:
    if not verify_password(
        current_password,
        user.password_hash,
    ):
        raise InvalidCredentialsError(
            "Current password is invalid."
        )

    if verify_password(
        new_password,
        user.password_hash,
    ):
        raise PasswordReuseError(
            "The new password must be different from the current password."
        )

    validate_password(new_password)

    user.password_hash = hash_password(
        new_password
    )

    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action=PASSWORD_CHANGED,
        resource="User",
        actor_id=str(user.id),
        target_id=str(user.id),
        resource_id=str(user.id),
        details="Password changed.",
    )

    return user


def soft_delete_user(
    db: Session,
    user: UserModel,
    actor_id: str,
):
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action=USER_SOFT_DELETED,
        resource="User",
        actor_id=actor_id,
        target_id=str(user.id),
        resource_id=str(user.id),
        details="User soft delete.",
    )

    logger.warning(f"User deactivated: {user.email}")

    return user

# ============================================================================
# USER OPERATIONS FOR ADMIN
# ============================================================================

def update_user_by_admin(
    db: Session,
    user_id: UUID,
    *,
    name: str | None = None,
    email: str | None = None,
    role_name: str | None = None,
    is_active: bool | None = None,
) -> UserModel:
    """Update a user by administrator."""

    user = get_user_by_id(
        db,
        user_id,
    )

    if name is not None:
        user.name = name.strip()

    if email is not None:
        normalized_email = _normalize_email(email)

        if normalized_email != user.email:
            existing_user = db.execute(
                select(UserModel).where(
                    func.lower(UserModel.email)
                    == normalized_email
                )
            ).scalar_one_or_none()

            if existing_user:
                raise EmailAlreadyExistsError(
                    f"Email '{email}' is already registered."
                )

            user.email = normalized_email
    if role_name is not None:
        role = get_role_by_name(db, role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' not found.")
        user.role_id = role.id


    if is_active is not None:
        user.is_active = is_active

    user.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.email}")

    return user


def hard_delete_user(
    db: Session,
    user: UserModel,
    *,
    actor_id: str | None = None,
) -> None:
    """Permanently delete a user."""

    target_id = str(user.id)

    create_audit_log(
        db=db,
        action=USER_HARD_DELETED,
        resource="User",
        actor_id=actor_id,
        target_id=target_id,
        resource_id=target_id,
        details="User permanently deleted.",
    )

    db.delete(user)
    db.commit()
