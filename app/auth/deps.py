from jose import JWTError
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token


# tokenUrl é usado pelo Swagger para saber onde fazer login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_session_id(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    try:
        payload = decode_access_token(token)

        session_id = payload.get("session_id")

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        return session_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


CurrentSessionId = Annotated[str, Depends(get_current_session_id)]