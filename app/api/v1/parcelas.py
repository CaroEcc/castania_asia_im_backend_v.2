from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import ParcelaCreate, ParcelaOut, ParcelaUpdate
from app.services.parcelas import ParcelaService
from app.services.recolectores import RecolectorService

router = APIRouter(prefix="/parcelas", tags=["Módulo 1 — Parcelas"])


def _svc(db: Session = Depends(get_db)) -> ParcelaService:
    return ParcelaService(db)


def _rec_svc(db: Session = Depends(get_db)) -> RecolectorService:
    return RecolectorService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/parcelas  — recolector registra su propia parcela
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=ParcelaOut,
    status_code=201,
    summary="Registrar nueva parcela del recolector autenticado",
)
def crear_parcela(
    body: ParcelaCreate,
    svc: ParcelaService = Depends(_svc),
    rec_svc: RecolectorService = Depends(_rec_svc),
    current_user=Depends(require_role(UserRole.recolector)),
):
    recolector = rec_svc.obtener_por_usuario(current_user.id)
    return svc.crear(recolector.id, body)


# ---------------------------------------------------------------------------
# GET /api/v1/parcelas/{id}  — recolector consulta su parcela (polígono GPS)
# ---------------------------------------------------------------------------

@router.get(
    "/{parcela_id}",
    response_model=ParcelaOut,
    summary="Obtener polígono GPS de una parcela del recolector autenticado",
)
def obtener_parcela(
    parcela_id: int,
    svc: ParcelaService = Depends(_svc),
    rec_svc: RecolectorService = Depends(_rec_svc),
    current_user=Depends(require_role(UserRole.recolector)),
):
    recolector = rec_svc.obtener_por_usuario(current_user.id)
    return svc.obtener(parcela_id, recolector.id)


# ---------------------------------------------------------------------------
# PATCH /api/v1/parcelas/{id}  — recolector edita o desactiva su parcela
# ---------------------------------------------------------------------------

@router.patch(
    "/{parcela_id}",
    response_model=ParcelaOut,
    summary="Editar parcela o cambiar estado (activa/inactiva)",
)
def actualizar_parcela(
    parcela_id: int,
    body: ParcelaUpdate,
    svc: ParcelaService = Depends(_svc),
    rec_svc: RecolectorService = Depends(_rec_svc),
    current_user=Depends(require_role(UserRole.recolector)),
):
    recolector = rec_svc.obtener_por_usuario(current_user.id)
    return svc.actualizar(parcela_id, recolector.id, body)
