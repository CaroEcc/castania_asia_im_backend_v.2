from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import AutorizacionRecolectorOut, HabilitarRecolectoresBody
from app.services.autorizaciones import AutorizacionRecolectorService

router = APIRouter(
    prefix="/autorizaciones-zafra",
    tags=["Campaña de Recolección — Recolectores Habilitados"],
)

_roles_permitidos = Depends(require_role(UserRole.responsable_acopio, UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> AutorizacionRecolectorService:
    return AutorizacionRecolectorService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/autorizaciones-zafra/recolectores
# Habilita uno o varios recolectores para una comunidad y cosecha.
# ---------------------------------------------------------------------------

@router.post(
    "/recolectores",
    response_model=List[AutorizacionRecolectorOut],
    status_code=201,
    summary="Habilitar recolectores para una comunidad y cosecha",
    dependencies=[_roles_permitidos],
)
def habilitar_recolectores(
    body: HabilitarRecolectoresBody,
    svc: AutorizacionRecolectorService = Depends(_svc),
):
    return svc.habilitar(body)


# ---------------------------------------------------------------------------
# GET /api/v1/autorizaciones-zafra/recolectores-habilitados
# Lista de trabajo diario con badge de estado por recolector.
# ---------------------------------------------------------------------------

@router.get(
    "/recolectores-habilitados",
    response_model=List[dict],
    dependencies=[_roles_permitidos],
    summary="Lista de recolectores habilitados con estado de entrega",
)
def recolectores_habilitados(
    comunidad_id: int = Query(...),
    cosecha: int = Query(..., ge=2000, le=2100),
    svc: AutorizacionRecolectorService = Depends(_svc),
):
    return svc.listar_habilitados(comunidad_id, cosecha)
