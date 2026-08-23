from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from typing import List

from app.schemas import DespachoCreate, DespachoOut, RecepcionDestinoBody
from app.services.despachos import DespachoService

router = APIRouter(
    prefix="/despachos",
    tags=["Módulo 4 — Despacho"],
)


def _svc(db: Session = Depends(get_db)) -> DespachoService:
    return DespachoService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/despachos
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[DespachoOut],
    summary="Listar despachos",
)
def listar_despachos(
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: DespachoService = Depends(_svc),
):
    return svc.listar()


# ---------------------------------------------------------------------------
# POST /api/v1/despachos
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=DespachoOut,
    status_code=201,
    summary="Registrar despacho de pulpa",
)
def crear_despacho(
    body: DespachoCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: DespachoService = Depends(_svc),
):
    return svc.crear(body, current_user.id)


# ---------------------------------------------------------------------------
# PATCH /api/v1/despachos/{id}/recepcion-destino
# ---------------------------------------------------------------------------

@router.patch(
    "/{despacho_id}/recepcion-destino",
    response_model=DespachoOut,
    summary="Registrar recepción en destino de un despacho",
)
def recepcion_destino(
    despacho_id: int,
    body: RecepcionDestinoBody,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: DespachoService = Depends(_svc),
):
    return svc.recepcion_destino(despacho_id, body)
