"""Application entry point."""

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers

from app.auth.router import router as auth_router
from app.users.admin_router import router as admin_users_router
from app.users.router import router as users_router

# Import models so they are registered in the metadata / Alembic sees them.
from app.users import models as user_models  # noqa: F401
from app.auth import models as auth_models  # noqa: F401
from app.audit import models as audit_models  # noqa: F401

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

register_exception_handlers(app)

API_V1_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(admin_users_router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["Health"])
def health_check():
    """Simple endpoint to verify the API status."""
    return {"status": "ok"}