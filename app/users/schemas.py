"""Pydantic schemas for the Users module."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRoleSchema(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# ============================================================================
# PUBLIC REGISTRATION
# ============================================================================

class UserRegisterSchema(BaseModel):
    """Schema for public user registration."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    avatar_url: str | None = Field(
        default=None,
        max_length=500,
    )

    job_title: str | None = Field(
        default=None,
        max_length=150,
    )

    bio: str | None = Field(
        default=None,
        max_length=1000,
    )

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@company.com",
                "password": "StrongPassword123!",
                "phone": "+5575999999999",
                "job_title": "Promotor de Justiça",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Atuação na área criminal.",
            }
        },
    )


# ============================================================================
# ADMINISTRATION
# ============================================================================

class UserAdminCreateSchema(BaseModel):
    """Schema for administrative user creation."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )

    role: UserRoleSchema = UserRoleSchema.MEMBER


class UserAdminUpdateSchema(BaseModel):
    """Schema for administrative user update."""

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    email: EmailStr | None = None

    role: UserRoleSchema | None = None

    phone: str | None = None

    avatar_url: str | None = Field(
        default=None,
        max_length=500,
    )

    job_title: str | None = Field(
        default=None,
        max_length=150,
    )

    bio: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_active: bool | None = None


class UserProfileUpdateSchema(BaseModel):
    """Schema for updating the current user's profile."""

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    avatar_url: str | None = Field(
        default=None,
        max_length=500,
    )

    job_title: str | None = Field(
        default=None,
        max_length=150,
    )

    bio: str | None = Field(
        default=None,
        max_length=1000,
    )


class ChangePasswordSchema(BaseModel):
    """Schema for password changes."""

    current_password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )

# ============================================================================
# RESPONSES
# ============================================================================

class UserResponseSchema(BaseModel):
    """Schema for user responses."""

    id: UUID
    name: str
    email: EmailStr
    role: UserRoleSchema
    phone: str | None = None
    avatar_url: str | None = None
    job_title: str | None = None
    bio: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "role": "member",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": None,
            }
        },
    )


class UserListResponseSchema(BaseModel):
    """Schema for paginated user lists."""

    items: list[UserResponseSchema]
    total: int
    skip: int
    limit: int