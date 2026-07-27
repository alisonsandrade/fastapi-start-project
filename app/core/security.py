"""Utilitários de segurança: hash de senha (bcrypt) e JWT.

Usa bcrypt diretamente (sem passlib) — mais leve e sem o warning
"error reading bcrypt version" que aparece em algumas builds.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError

from app.core.config import get_settings

settings = get_settings()


def hash_password(plain_password: str) -> str:
    """Gera o hash da senha usando bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(
        subject: str,
        extra_claims: dict[str, Any] | None = None, 
        expires_delta: timedelta | None = None
    ) -> str:
    """Cria um token JWT de acesso.

    Args:
        subject (str): O assunto do token (geralmente o ID do usuário).
        extra_claims (dict[str, Any] | None): Reclamações extras a serem incluídas no payload do token.
        expires_delta (timedelta | None): Tempo de expiração do token. Se None, usa o padrão da configuração.

    Returns:
        str: Token JWT codificado.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta
    }
    if extra_claims:
        payload.update(extra_claims)
    encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica um token JWT de acesso.

    Args:
        token (str): Token JWT a ser decodificado.

    Returns:
        dict[str, Any]: Payload decodificado do token.

    Raises:
        JWTError: Se o token for inválido ou expirado.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        raise JWTError(f"Token inválido ou expirado: {str(e)}") from e