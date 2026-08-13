"""Administrative router for Users: accessible only by ADMIN."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies.database import get_db
from app.deps import CurrentAdmin, require_permission
from app.rbac.permissions import Permissions
from app.users import service
from app.users.exceptions import (
    EmailAlreadyExistsError,
    WeakPasswordError,
    UserNotFoundError,
)
from app.users.schemas import (
    UserAdminCreateSchema,
    UserAdminUpdateSchema,
    UserListResponseSchema,
    UserResponseSchema,
)

router = APIRouter(
    prefix="/admin/users",
    tags=["Administração de usuários"],
)


@router.post(
    "/",
    dependencies=[Depends(require_permission(Permissions.USERS_CREATE))],
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create user (ADMIN)",
)
def create_user_by_admin(
    payload: UserAdminCreateSchema,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create a new user with a role defined by an ADMIN.
    """
    try:
        user = service.create_user(
            db,
            avatar_url=payload.avatar_url,
            name=payload.name,
            email=str(payload.email).lower(),
            password=payload.password,
            role_name=payload.role.value,
            phone=payload.phone,
            job_title=payload.job_title,
            bio=payload.bio,
        )
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except WeakPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    return user


@router.get(
    "/",
    dependencies=[Depends(require_permission(Permissions.USERS_LIST))],
    response_model=UserListResponseSchema,
    summary="List users (ADMIN)",
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    role: str | None = Query(
        None,
        description="Filter users by role",
    ),
    active_only: bool | None = Query(
        None,
        description="Filter active users only",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),
):
    """
    List all registered users.
    """
    items, total = service.list_users(
        db,
        role=role,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )

    return UserListResponseSchema(
        total=total,
        skip=skip,
        limit=limit,
        items=[
            UserResponseSchema.model_validate(item)
            for item in items
        ],
    )


@router.patch(
    "/{user_id}",
    dependencies=[Depends(require_permission(Permissions.USERS_UPDATE))],
    response_model=UserResponseSchema,
    summary="Update user (ADMIN)",
)
def update_user_by_admin(
    user_id: UUID,
    payload: UserAdminUpdateSchema,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Update an existing user.
    """
    try:
        user = service.update_user_by_admin(
            db,
            user_id,
            name=payload.name,
            email=str(payload.email).lower()
            if payload.email
            else None,
            role_name=payload.role.value
            if payload.role
            else None,
            is_active=payload.is_active,
        )

    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permission(Permissions.USERS_DELETE))],
    response_model=UserResponseSchema,
    summary="Soft delete user (ADMIN)",
)
def soft_delete_user_by_admin(
    user_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    admin: CurrentAdmin
):
    user = service.get_user_by_id(db, user_id)

    if str(user.id) == str(admin.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    service.soft_delete_user(
        db=db,
        user=user,
        actor_id=str(admin.id)
    )

    return user


@router.delete(
    "/{user_id}/hard",
    dependencies=[Depends(require_permission(Permissions.USERS_DELETE))],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard delete user (ADMIN)",
)
def hard_delete_user_by_admin(
    user_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    admin: CurrentAdmin,
):
    user = service.get_user_by_id(db, user_id)

    if str(user.id) == str(admin.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account."
        )

    service.hard_delete_user(
        db=db,
        user=user,
        actor_id=str(admin.id),
    )
