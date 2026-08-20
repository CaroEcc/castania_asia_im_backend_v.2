from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import LoteProductoTerminadoOut
from app.services.lotes_terminado import LoteProductoTerminadoService

router = APIRouter(
    prefix="/lotes-producto-terminado",
    tags=["Módulo 3 — Lotes de producto terminado"],
)

_roles = Depends(require_role(UserRole.operador_planta, UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> LoteProductoTerminadoService:
    return LoteProductoTerminadoService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-producto-terminado
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[LoteProductoTerminadoOut],
    summary="Listar lotes de producto terminado",
    dependencies=[_roles],
)
def listar_lotes_terminado(
    estado: Optional[str] = Query(
        None,
        description="en_proceso | choque_termico | camara_frio | parcialmente_despachado | despachado",
    ),
    svc: LoteProductoTerminadoService = Depends(_svc),
):
    return svc.listar(estado=estado)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-producto-terminado/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/{lote_id}",
    response_model=LoteProductoTerminadoOut,
    summary="Detalle de un lote de producto terminado",
    dependencies=[_roles],
)
def obtener_lote_terminado(
    lote_id: int,
    svc: LoteProductoTerminadoService = Depends(_svc),
):
    return svc.get_by_id(lote_id)
