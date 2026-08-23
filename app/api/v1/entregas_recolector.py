from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import EntregaRecolectorCreate, EntregaRecolectorOut, ParcelaOut
from app.services.recolectores import RecolectorService

router = APIRouter(prefix="/entregas-recolector", tags=["Módulo 1 — Entregas recolector"])


def _svc(db: Session = Depends(get_db)) -> RecolectorService:
    return RecolectorService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/entregas-recolector
#   El recolector sincroniza una entrega registrada offline en su app.
#   El recolector_id se deriva del JWT — nunca lo envía el cliente.
#   No lleva lote_id: el lote lo asigna el responsable de acopio al registrar
#   la recepción (ItemRecepcion).
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=EntregaRecolectorOut,
    status_code=201,
    summary="Sincronizar entrega registrada offline por el recolector",
)
def sincronizar_entrega(
    body: EntregaRecolectorCreate,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(require_role(UserRole.recolector)),
):
    recolector = svc.obtener_por_usuario(current_user.id)
    return svc.crear_entrega(recolector.id, body)


# ---------------------------------------------------------------------------
# GET /api/v1/entregas-recolector/{entrega_id}
#   El recolector consulta el detalle de una de sus propias entregas.
# ---------------------------------------------------------------------------

@router.get(
    "/{entrega_id}",
    response_model=EntregaRecolectorOut,
    summary="Obtener detalle de una entrega del recolector autenticado",
)
def obtener_entrega(
    entrega_id: int,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(require_role(UserRole.recolector)),
):
    recolector = svc.obtener_por_usuario(current_user.id)
    return svc.obtener_entrega(entrega_id, recolector.id)


# ---------------------------------------------------------------------------
# GET /api/v1/entregas-recolector/{entrega_id}/parcela
#   Retorna la parcela (con su polígono GPS) asociada a una entrega.
#   Usada para cargar los puntos de la parcela en un mapa.
# ---------------------------------------------------------------------------

@router.get(
    "/{entrega_id}/parcela",
    response_model=ParcelaOut,
    summary="Obtener polígono GPS de la parcela de una entrega",
)
def obtener_parcela_de_entrega(
    entrega_id: int,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(require_role(
        UserRole.responsable_acopio,
        UserRole.operador_planta,
        UserRole.administrador,
    )),
):
    return svc.get_parcela_de_entrega(entrega_id)
