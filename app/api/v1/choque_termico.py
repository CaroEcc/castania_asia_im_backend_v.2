from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import SesionChoqueTermicoCreate, SesionChoqueTermicoOut
from app.services.choque_termico import SesionChoqueTermicoService

router = APIRouter(
    prefix="/sesiones-choque-termico",
    tags=["Módulo 3 — Choque térmico"],
)


def _svc(db: Session = Depends(get_db)) -> SesionChoqueTermicoService:
    return SesionChoqueTermicoService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/sesiones-choque-termico
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=SesionChoqueTermicoOut,
    status_code=201,
    summary="Registrar sesión de choque térmico",
)
def crear_sesion_choque_termico(
    body: SesionChoqueTermicoCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: SesionChoqueTermicoService = Depends(_svc),
):
    return svc.crear(body, current_user.id)
