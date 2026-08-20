from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import MatrizProcesosCreate, MatrizProcesosOut
from app.services.matrices import MatrizProcesosService

router = APIRouter(
    prefix="/matrices-procesos",
    tags=["Módulo 4 — Matriz de procesos"],
)


def _svc(db: Session = Depends(get_db)) -> MatrizProcesosService:
    return MatrizProcesosService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/matrices-procesos
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=MatrizProcesosOut,
    status_code=201,
    summary="Registrar matriz de procesos para un lote de producto terminado",
)
def crear_matriz_procesos(
    body: MatrizProcesosCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: MatrizProcesosService = Depends(_svc),
):
    return svc.crear(body, current_user.id)
