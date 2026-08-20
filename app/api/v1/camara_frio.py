from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import InventarioCamaraFrioCreate, InventarioCamaraFrioOut
from app.services.camara_frio import InventarioCamaraFrioService

router = APIRouter(
    prefix="/inventario-camara-frio",
    tags=["Módulo 4 — Cámara de frío"],
)


def _svc(db: Session = Depends(get_db)) -> InventarioCamaraFrioService:
    return InventarioCamaraFrioService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/inventario-camara-frio
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=InventarioCamaraFrioOut,
    status_code=201,
    summary="Registrar entrada en inventario de cámara de frío",
)
def crear_inventario_camara_frio(
    body: InventarioCamaraFrioCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: InventarioCamaraFrioService = Depends(_svc),
):
    return svc.crear(body, current_user.id)
