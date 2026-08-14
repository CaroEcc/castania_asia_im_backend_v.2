from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

_url = settings.database_url
if "postgresql://" in _url and "psycopg2" not in _url:
    _url = _url.replace("postgresql://", "postgresql+psycopg2://")

if "sqlite" in _url:
    engine = create_engine(_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        _url,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 30,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
