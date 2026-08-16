from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import EntregaRecolectorCreate, EntregaRecolectorOut
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
