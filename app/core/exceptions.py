from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
    InvalidRefreshTokenError,
    InvalidSessionError,
    PasswordResetTokenError,
)

from app.users.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    WeakPasswordError,
    PasswordReuseError,
    PermissionDeniedError,
)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(EmailAlreadyExistsError)
    async def email_already_exists_handler(
        request: Request,
        exc: EmailAlreadyExistsError,
    ):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(WeakPasswordError)
    async def weak_password_handler(
        request: Request,
        exc: WeakPasswordError,
    ):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PasswordReuseError)
    async def password_reuse_handler(
        request: Request,
        exc: PasswordReuseError,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    @app.exception_handler(InactiveUserError)
    async def inactive_user_handler(
        request: Request,
        exc: InactiveUserError,
    ):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidRefreshTokenError)
    async def invalid_refresh_token_handler(
        request: Request,
        exc: InvalidRefreshTokenError,
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidSessionError)
    async def invalid_session_handler(
        request: Request,
        exc: InvalidSessionError,
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(
        request: Request,
        exc: PermissionDeniedError,
    ):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PasswordResetTokenError)
    async def password_reset_token_handler(
        request: Request,
        exc: PasswordResetTokenError,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
            },
        )