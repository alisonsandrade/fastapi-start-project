"""Configuração do SQLAlchemy 2.0 e sessão por request.
- engine: conexão com o banco (singleton).
- Base: classe pai de todos os models (usada para o metadata).
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite exige um argumento especial para funcionar em ambiente multi-thread do FastAPI
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False,
    future=True
)

# Habilita foreign keys no SQLite
if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session
)


class Base(DeclarativeBase):
    pass
