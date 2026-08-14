"""
Fixtures de pytest para los tests del backend.

Estrategia de aislamiento:
    Se usa SQLite en memoria con rollback por transacción, de modo que
    cada test parte de una base limpia y NUNCA toca la DB de desarrollo.

Uso:
    Los tests individuales reciben `client` (TestClient con DB de test)
    o `db` (sesión de SQLAlchemy aislada) como parámetros de fixture.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base
from app.core.deps import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(test_engine):
    """Sesión de test con rollback automático al finalizar cada test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    TestingSession = sessionmaker(bind=connection)
    session = TestingSession()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """TestClient de FastAPI con la DB de test inyectada."""
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
