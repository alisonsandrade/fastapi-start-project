"""Dependências globais de autenticação e autorização.

Aqui vivem os "guards" que protegem os endpoints:
- get_current_user: extrai o user do JWT (endpoint protegido)
- require_admin: garante que o user é ADMIN (endpoint só-admin)
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.dependencies.database import get_db
from app.core.security import decode_access_token
from app.users.models import UserModel, UserRole
from app.users.service import get_user_by_id
from app.users.exceptions import UserNotFoundError

from app.auth.models import UserSessionModel

# tokenUrl é usado pelo Swagger para saber onde fazer login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Annotated[Session, Depends(get_db)]
) -> UserModel:
    """Extrai o user do JWT.

    Args:
        token (str): Token JWT do header Authorization.
        db (Session): Sessão do banco de dados.

    Raises:
        HTTPException: Se o token for inválido ou o user não for encontrado.

    Returns:
        UserModel: User autenticado.
    """
    credenciais_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: UUID = payload.get("sub")

        if user_id is None:
            raise credenciais_exc

        session_id = payload.get("session_id")
        session = db.get(UserSessionModel, session_id)

        if session is None:
            raise credenciais_exc
        if not session.is_active:
            raise credenciais_exc
    except JWTError:
        raise credenciais_exc

    try:
        user = get_user_by_id(db, user_id)
    except UserNotFoundError:
        raise credenciais_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    return user


def require_admin(
    current_user: Annotated[UserModel, Depends(get_current_user)]
) -> UserModel:
    """Garante que o user é ADMIN.

    Args:
        current_user (UserModel): User autenticado.

    Raises:
        HTTPException: Se o user não for ADMIN.

    Returns:
        UserModel: User autenticado.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não tem permissão de administrador",
        )
    return current_user


# Tipos "prontos para usar" — evitam repetir Annotated[...] em cada endpoint
CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CurrentAdmin = Annotated[UserModel, Depends(require_admin)]
