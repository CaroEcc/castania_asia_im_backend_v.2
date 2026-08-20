from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import (
    EntregaSinRecepcionOut,
    ItemRecepcionCreate,
    ItemRecepcionOut,
)
from app.services.items_recepcion import ItemRecepcionService

router = APIRouter(tags=["Módulo 2 — Recepción de materia prima"])

_roles_recepcion = Depends(require_role(UserRole.responsable_acopio, UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> ItemRecepcionService:
    return ItemRecepcionService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/lotes-materia-prima/{id}/recepciones
# ---------------------------------------------------------------------------

@router.post(
    "/lotes-materia-prima/{lote_id}/recepciones",
    status_code=201,
    dependencies=[_roles_recepcion],
    summary="Registrar recepción de un recolector en el lote activo",
)
def registrar_recepcion(
    lote_id: int,
    body: ItemRecepcionCreate,
    svc: ItemRecepcionService = Depends(_svc),
):
    return svc.registrar(lote_id, body)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-materia-prima/{id}/recepciones
# ---------------------------------------------------------------------------

@router.get(
    "/lotes-materia-prima/{lote_id}/recepciones",
    response_model=List[ItemRecepcionOut],
    dependencies=[_roles_recepcion],
    summary="Listar recepciones de un lote",
)
def listar_recepciones(
    lote_id: int,
    svc: ItemRecepcionService = Depends(_svc),
):
    return svc.listar_por_lote(lote_id)


# ---------------------------------------------------------------------------
# GET /api/v1/entregas-recolector?recolector_id=X&sin_recepcion=true
# Entregas del recolector que aún no tienen ItemRecepcion vinculado.
# Usadas para pre-cargar el formulario de recepción.
# ---------------------------------------------------------------------------

@router.get(
    "/entregas-recolector",
    response_model=List[EntregaSinRecepcionOut],
    dependencies=[_roles_recepcion],
    summary="Entregas de un recolector pendientes de recepción",
)
def entregas_sin_recepcion(
    recolector_id: int = Query(...),
    sin_recepcion: bool = Query(True),
    svc: ItemRecepcionService = Depends(_svc),
):
    if sin_recepcion:
        return svc.entregas_sin_recepcion(recolector_id)
    return []
