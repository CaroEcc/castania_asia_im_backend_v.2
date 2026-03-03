# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://caroecc:64pLPUFuUADlQqfXM20GLNTzb5so7CAC@dpg-d47ts3qli9vc738ve0o0-a.oregon-postgres.render.com/im_asai_castania")

# OBLIGATORIO: agregar +psycopg2 para SQLAlchemy
if DB_URL and "psycopg2" not in DB_URL:
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(
    DB_URL,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10
    },
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
