from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import (
    AutorizacionZafraCreate,
    AutorizacionZafraOut,
    HabilitarRecolectoresBody,
    RecolectorHabilitadoOut,
)
from app.services.autorizaciones import AutorizacionZafraService

router = APIRouter(prefix="/autorizaciones-zafra", tags=["Módulo 1 — Autorizaciones de Zafra"])

_roles_permitidos = Depends(require_role(UserRole.responsable_acopio, UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> AutorizacionZafraService:
    return AutorizacionZafraService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/autorizaciones-zafra?comunidad_id=X&cosecha=YYYY
# ---------------------------------------------------------------------------

@router.get("", response_model=AutorizacionZafraOut, dependencies=[_roles_permitidos])
def obtener_autorizacion(
    comunidad_id: int = Query(...),
    cosecha: int = Query(...),
    svc: AutorizacionZafraService = Depends(_svc),
):
    return svc.get_by_comunidad_cosecha(comunidad_id, cosecha)


# ---------------------------------------------------------------------------
# POST /api/v1/autorizaciones-zafra
# ---------------------------------------------------------------------------

@router.post("", response_model=AutorizacionZafraOut, status_code=201)
def crear_autorizacion(
    body: AutorizacionZafraCreate,
    svc: AutorizacionZafraService = Depends(_svc),
    current_user=Depends(require_role(UserRole.responsable_acopio, UserRole.administrador)),
):
    return svc.crear(body, current_user.id)


# ---------------------------------------------------------------------------
# POST /api/v1/autorizaciones-zafra/{id}/recolectores
# Habilita uno o varios recolectores en una autorización existente.
# ---------------------------------------------------------------------------

@router.post(
    "/{autorizacion_id}/recolectores",
    response_model=AutorizacionZafraOut,
    status_code=201,
)
def habilitar_recolectores(
    autorizacion_id: int,
    body: HabilitarRecolectoresBody,
    svc: AutorizacionZafraService = Depends(_svc),
    current_user=Depends(require_role(UserRole.responsable_acopio, UserRole.administrador)),
):
    return svc.habilitar_recolectores(autorizacion_id, body, current_user.id)


# ---------------------------------------------------------------------------
# GET /api/v1/autorizaciones-zafra/recolectores-habilitados
# Lista de trabajo diario con badge de estado por recolector.
# ---------------------------------------------------------------------------

@router.get(
    "/recolectores-habilitados",
    response_model=List[RecolectorHabilitadoOut],
    dependencies=[_roles_permitidos],
    summary="Lista de recolectores habilitados con estado de entrega",
)
def recolectores_habilitados(
    comunidad_id: int = Query(...),
    cosecha: int = Query(...),
    svc: AutorizacionZafraService = Depends(_svc),
):
    return svc.listar_recolectores_habilitados(comunidad_id, cosecha)
