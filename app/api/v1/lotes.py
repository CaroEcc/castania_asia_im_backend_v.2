from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import LoteMateriaPrimaOut
from app.services.lotes import LoteMateriaPrimaService

router = APIRouter(prefix="/lotes-materia-prima", tags=["Módulo 2 — Lotes de materia prima"])


def _svc(db: Session = Depends(get_db)) -> LoteMateriaPrimaService:
    return LoteMateriaPrimaService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-materia-prima/activo
#   Devuelve el lote en estado "abierto" de la comunidad indicada.
#   Rol: responsable_acopio o administrador.
# ---------------------------------------------------------------------------

@router.get(
    "/activo",
    response_model=LoteMateriaPrimaOut,
    summary="Lote de acopio activo de una comunidad",
)
def lote_activo(
    comunidad_id: int = Query(..., description="ID de la comunidad cuyo lote activo se consulta"),
    svc: LoteMateriaPrimaService = Depends(_svc),
    current_user=Depends(require_role(UserRole.responsable_acopio, UserRole.administrador)),
):
    return svc.get_activo(comunidad_id)
