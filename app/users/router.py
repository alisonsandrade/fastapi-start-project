"""Public user router: registration and current user profile."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import CurrentUser, require_permission
from app.core.dependencies.database import get_db
from app.users import service
from app.users.exceptions import PasswordReuseError
from app.users.models import UserRole
from app.users.schemas import (
    UserRegisterSchema,
    UserResponseSchema,
    UserProfileUpdateSchema,
    ChangePasswordSchema,
)


router = APIRouter(
    tags=["User Registration"],
)


@router.post(
    "/auth/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    payload: UserRegisterSchema,
    db: Annotated[Session, Depends(get_db)],
):
    return service.create_user(
        db=db,
        name=payload.name,
        email=str(payload.email).lower(),
        password=payload.password,
        role_name=UserRole.USER,
        phone=payload.phone,
        avatar_url=payload.avatar_url,
        job_title=payload.job_title,
        bio=payload.bio,
    )


@router.get(
    "/users/me",
    response_model=UserResponseSchema,
    summary="Get current authenticated user",
)
def get_current_user_profile(
    current_user: CurrentUser,
):
    return current_user


@router.patch(
    "/users/me",
    response_model=UserResponseSchema,
    summary="Update current user profile",
)
def update_current_user_profile(
    payload: UserProfileUpdateSchema,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        user = service.update_current_user(
            db=db,
            user=current_user,
            name=payload.name,
            phone=payload.phone,
            avatar_url=payload.avatar_url,
            job_title=payload.job_title,
            bio=payload.bio,
        )
    except PasswordReuseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return user


@router.patch(
    "/users/me/password",
    response_model=UserResponseSchema,
    summary="Change current user password",
)
def change_my_password(
    payload: ChangePasswordSchema,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    return service.change_password(
        db=db,
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )


@router.delete("/users/me")
def delete_my_account(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)]
):
    return service.soft_delete_user(
        db=db,
        user=current_user,
        actor_id=str(current_user.id),
    )
