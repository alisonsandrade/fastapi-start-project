from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    """Schema para login de usuário."""

    email: EmailStr = Field(..., max_length=150)
    senha: str = Field(..., min_length=8, max_length=255)


class TokenResponseSchema(BaseModel):
    """Schema para resposta de token JWT."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str = Field(..., min_length=32, max_length=255)


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )


