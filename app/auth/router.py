from fastapi import APIRouter, Depends, HTTPException, status

from typing import Annotated

from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordRequestForm

from app.auth.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
    InvalidRefreshTokenError,
    InvalidSessionError,
)
from app.core.dependencies.database import get_db

from app.auth import service

from app.auth.deps import CurrentSessionId

from app.auth.schemas import (
    TokenResponseSchema, 
    RefreshTokenRequestSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)


router = APIRouter(tags=["Autenticação"])


@router.post(
    "/auth/login",
    response_model=TokenResponseSchema,
    summary="Autentica e retorna um JWT",
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    tokens = service.authenticate_user(
        db, 
        email=str(form_data.username).lower(),
        password=form_data.password,
    )
    return TokenResponseSchema(
        access_token=tokens["access_token"], 
        refresh_token=tokens["refresh_token"],
        token_type=tokens.get("token_type", "bearer")
    )


@router.post(
    "/auth/refresh",
    response_model=TokenResponseSchema,
)
def refresh(
    payload: RefreshTokenRequestSchema,
    db: Annotated[Session, Depends(get_db)],
):
    tokens = service.refresh_session(db, payload.refresh_token)
    return TokenResponseSchema(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"]
    )


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    session_id: CurrentSessionId,
    db: Annotated[Session, Depends(get_db)],
):
    service.terminate_session(db, session_id)


@router.post(
    "/auth/forgot-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Request password reset",
)
def forgot_password(
    payload: ForgotPasswordSchema,
    db: Annotated[Session, Depends(get_db)],
):
    service.request_password_reset(
        db=db,
        email=payload.email,
    )


@router.post(
    "/auth/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset password",
)
def reset_password(
    payload: ResetPasswordSchema,
    db: Annotated[Session, Depends(get_db)],
):
    service.reset_password(
        db=db,
        token=payload.token,
        new_password=payload.new_password,
    )