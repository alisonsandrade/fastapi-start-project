from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:    
    """Dependência do FastAPI: fornece uma sessão nova por request.

    Uso nos endpoints:
        def meu_endpoint(db: Annotated[Session, Depends(get_db)]):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()