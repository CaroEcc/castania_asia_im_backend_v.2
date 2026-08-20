from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import (
    CerrarLoteBody,
    LoteListResponse,
    LoteMateriaPrimaCreate,
    LoteMateriaPrimaOut,
    RechazarLoteBody,
)
from app.services.lotes import LoteMateriaPrimaService

router = APIRouter(prefix="/lotes-materia-prima", tags=["Módulo 2 — Lotes de materia prima"])

_roles_acopio = Depends(require_role(UserRole.responsable_acopio, UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> LoteMateriaPrimaService:
    return LoteMateriaPrimaService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-materia-prima/activo
# ---------------------------------------------------------------------------

@router.get(
    "/activo",
    response_model=LoteMateriaPrimaOut,
    summary="Lote de acopio activo de una comunidad",
    dependencies=[_roles_acopio],
)
def lote_activo(
    comunidad_id: int = Query(..., description="ID de la comunidad cuyo lote activo se consulta"),
    svc: LoteMateriaPrimaService = Depends(_svc),
):
    return svc.get_activo(comunidad_id)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-materia-prima  — historial con filtros
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=LoteListResponse,
    summary="Historial de lotes con filtros",
    dependencies=[_roles_acopio],
)
def listar_lotes(
    comunidad_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None, description="abierto | cerrado | en_limpieza | en_ablandamiento | en_elaboracion | completado | rechazado"),
    svc: LoteMateriaPrimaService = Depends(_svc),
):
    lotes = svc.listar(comunidad_id=comunidad_id, estado=estado)
    return LoteListResponse(total=len(lotes), lotes=lotes)


# ---------------------------------------------------------------------------
# POST /api/v1/lotes-materia-prima  — abrir nuevo lote
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=LoteMateriaPrimaOut,
    status_code=201,
    summary="Abrir nuevo lote de acopio",
)
def abrir_lote(
    body: LoteMateriaPrimaCreate,
    svc: LoteMateriaPrimaService = Depends(_svc),
    current_user=Depends(require_role(UserRole.responsable_acopio, UserRole.administrador)),
):
    return svc.abrir(body, current_user.id)


# ---------------------------------------------------------------------------
# GET /api/v1/lotes-materia-prima/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/{lote_id}",
    response_model=LoteMateriaPrimaOut,
    summary="Detalle de un lote",
    dependencies=[_roles_acopio],
)
def obtener_lote(
    lote_id: int,
    svc: LoteMateriaPrimaService = Depends(_svc),
):
    return svc._get_or_404(lote_id)


# ---------------------------------------------------------------------------
# POST /api/v1/lotes-materia-prima/{id}/cerrar
# ---------------------------------------------------------------------------

@router.post(
    "/{lote_id}/cerrar",
    response_model=LoteMateriaPrimaOut,
    summary="Cerrar lote de acopio",
    dependencies=[_roles_acopio],
)
def cerrar_lote(
    lote_id: int,
    body: CerrarLoteBody,
    svc: LoteMateriaPrimaService = Depends(_svc),
):
    return svc.cerrar(lote_id, body)


# ---------------------------------------------------------------------------
# POST /api/v1/lotes-materia-prima/{id}/rechazar
# ---------------------------------------------------------------------------

@router.post(
    "/{lote_id}/rechazar",
    response_model=LoteMateriaPrimaOut,
    summary="Rechazar lote de acopio",
    dependencies=[_roles_acopio],
)
def rechazar_lote(
    lote_id: int,
    body: RechazarLoteBody,
    svc: LoteMateriaPrimaService = Depends(_svc),
):
    return svc.rechazar(lote_id, body)
