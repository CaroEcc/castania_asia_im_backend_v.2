# tests/test_usuarios.py
"""
Tests básicos del CRUD de UsuarioSistema.
Usa SQLite en memoria para no necesitar la DB de Render.
El dependency de require_administrador se parchea con override.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.auth import require_administrador

# ---------------------------------------------------------------------------
# Infraestructura de test
# ---------------------------------------------------------------------------

SQLITE_TEST_URL = "sqlite:///./test_usuarios.db"

engine_test = create_engine(SQLITE_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class _MockAdmin:
    """Simula un UsuarioSistema administrador sin necesitar JWT ni DB real."""
    id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    rol = "administrador"
    username = "admin_test"
    nombre_completo = "Admin Test"
    activo = True


def override_require_administrador():
    return _MockAdmin()


@pytest.fixture(autouse=True)
def setup_teardown():
    Base.metadata.create_all(bind=engine_test)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_administrador] = override_require_administrador
    yield
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()


client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _crear_recolector(username="german.gongora"):
    return client.post("/usuarios", json={
        "nombre_completo": "German Góngora Soliz",
        "username": username,
        "rol": "recolector",
        "comunidad": "Villa Fátima",
    })


def _crear_jefe(username="jefe.planta"):
    return client.post("/usuarios", json={
        "nombre_completo": "Jefe de Planta",
        "username": username,
        "rol": "jefe_planta",
        "credencial": "password123",
    })


# ---------------------------------------------------------------------------
# Tests: creación exitosa
# ---------------------------------------------------------------------------

def test_crear_recolector_devuelve_201_y_pin():
    r = _crear_recolector()
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "german.gongora"
    assert data["rol"] == "recolector"
    assert data["metodo_auth"] == "pin"
    assert data["pin_generado"] is not None
    assert len(data["pin_generado"]) == 6
    assert data["pin_generado"].isdigit()


def test_crear_operador_planta_devuelve_pin():
    r = client.post("/usuarios", json={
        "nombre_completo": "Operador Planta",
        "username": "operador.uno",
        "rol": "operador_planta",
    })
    assert r.status_code == 201
    assert r.json()["metodo_auth"] == "pin"
    assert r.json()["pin_generado"] is not None


def test_crear_jefe_planta_sin_pin_devuelve_201():
    r = _crear_jefe()
    assert r.status_code == 201
    data = r.json()
    assert data["metodo_auth"] == "password"
    assert data["pin_generado"] is None


def test_crear_administrador_exitoso():
    r = client.post("/usuarios", json={
        "nombre_completo": "Admin Nuevo",
        "username": "admin.nuevo",
        "rol": "administrador",
        "credencial": "superSecreta99",
    })
    assert r.status_code == 201
    assert r.json()["rol"] == "administrador"


# ---------------------------------------------------------------------------
# Test: username duplicado devuelve 409 con mensaje claro
# ---------------------------------------------------------------------------

def test_username_duplicado_devuelve_409():
    _crear_recolector("duplicado.user")
    r = _crear_recolector("duplicado.user")
    assert r.status_code == 409
    assert "duplicado.user" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Tests: el response NUNCA incluye credencial_hash
# ---------------------------------------------------------------------------

def test_crear_response_no_expone_credencial_hash():
    r = _crear_jefe("jefe.seguro")
    assert r.status_code == 201
    assert "credencial_hash" not in r.json()


def test_listar_response_no_expone_credencial_hash():
    _crear_jefe("jefe.lista")
    r = client.get("/usuarios")
    assert r.status_code == 200
    for u in r.json():
        assert "credencial_hash" not in u


def test_obtener_response_no_expone_credencial_hash():
    r_create = _crear_jefe("jefe.detalle")
    user_id = r_create.json()["id"]
    r = client.get(f"/usuarios/{user_id}")
    assert r.status_code == 200
    assert "credencial_hash" not in r.json()


def test_pin_solo_aparece_en_respuesta_de_creacion():
    """El PIN no aparece en GET /usuarios/{id} ni en GET /usuarios."""
    r_create = _crear_recolector("recolector.pin")
    user_id = r_create.json()["id"]

    r_get = client.get(f"/usuarios/{user_id}")
    assert "pin_generado" not in r_get.json()

    r_list = client.get("/usuarios")
    for u in r_list.json():
        assert "pin_generado" not in u


# ---------------------------------------------------------------------------
# Tests: roles que requieren password sin credencial → 422
# ---------------------------------------------------------------------------

def test_crear_jefe_sin_credencial_devuelve_422():
    r = client.post("/usuarios", json={
        "nombre_completo": "Jefe Sin Pass",
        "username": "jefe.sinpass",
        "rol": "jefe_planta",
        # sin 'credencial'
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Tests: GET con filtros
# ---------------------------------------------------------------------------

def test_listar_filtra_por_rol():
    _crear_recolector("recolector.filtro")
    _crear_jefe("jefe.filtro")
    r = client.get("/usuarios?rol=recolector")
    assert r.status_code == 200
    assert all(u["rol"] == "recolector" for u in r.json())


def test_listar_filtra_por_activo():
    r_create = _crear_jefe("jefe.inactivo")
    user_id = r_create.json()["id"]
    client.patch(f"/usuarios/{user_id}/estado", json={"activo": False})

    r = client.get("/usuarios?activo=false")
    assert r.status_code == 200
    assert all(not u["activo"] for u in r.json())


# ---------------------------------------------------------------------------
# Tests: soft delete (PATCH /estado)
# ---------------------------------------------------------------------------

def test_desactivar_usuario_no_lo_elimina():
    r_create = _crear_jefe("jefe.softdelete")
    user_id = r_create.json()["id"]

    r_patch = client.patch(f"/usuarios/{user_id}/estado", json={"activo": False})
    assert r_patch.status_code == 200
    assert r_patch.json()["activo"] is False

    r_get = client.get(f"/usuarios/{user_id}")
    assert r_get.status_code == 200  # sigue existiendo
    assert r_get.json()["activo"] is False


# ---------------------------------------------------------------------------
# Tests: reset-credencial
# ---------------------------------------------------------------------------

def test_reset_credencial_pin_devuelve_nuevo_pin():
    r_create = _crear_recolector("recolector.reset")
    user_id = r_create.json()["id"]

    r = client.post(f"/usuarios/{user_id}/reset-credencial", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["pin_generado"] is not None
    assert len(data["pin_generado"]) == 6


def test_reset_credencial_password_sin_nueva_devuelve_422():
    r_create = _crear_jefe("jefe.reset")
    user_id = r_create.json()["id"]

    r = client.post(f"/usuarios/{user_id}/reset-credencial", json={})
    assert r.status_code == 422
