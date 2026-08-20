from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import (
    LoteMateriaPrimaOut,
    ProcesoLimpiezaCreate,
    ProcesoLimpiezaOut,
    ProcesoAblandamientoCreate,
    ProcesoAblandamientoOut,
    ProcesoElaboracionCreate,
    ProcesoElaboracionOut,
)
from app.services.procesos_planta import (
    ProcesoLimpiezaService,
    ProcesoAblandamientoService,
    ProcesoElaboracionService,
    VoboPlantaService,
)

router = APIRouter(tags=["Módulo 3 — Procesos de planta"])

_roles = Depends(require_role(UserRole.operador_planta, UserRole.administrador))


def _svc_limpieza(db: Session = Depends(get_db)) -> ProcesoLimpiezaService:
    return ProcesoLimpiezaService(db)


def _svc_ablandamiento(db: Session = Depends(get_db)) -> ProcesoAblandamientoService:
    return ProcesoAblandamientoService(db)


def _svc_elaboracion(db: Session = Depends(get_db)) -> ProcesoElaboracionService:
    return ProcesoElaboracionService(db)


def _svc_vobo(db: Session = Depends(get_db)) -> VoboPlantaService:
    return VoboPlantaService(db)


# ---------------------------------------------------------------------------
# PATCH /api/v1/lotes-materia-prima/{id}/vobo-planta
# ---------------------------------------------------------------------------

@router.patch(
    "/lotes-materia-prima/{lote_id}/vobo-planta",
    response_model=LoteMateriaPrimaOut,
    summary="Dar VoBo de planta a un lote cerrado",
)
def dar_vobo_planta(
    lote_id: int,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: VoboPlantaService = Depends(_svc_vobo),
):
    return svc.dar_vobo(lote_id)


# ---------------------------------------------------------------------------
# POST /api/v1/procesos-limpieza
# ---------------------------------------------------------------------------

@router.post(
    "/procesos-limpieza",
    response_model=ProcesoLimpiezaOut,
    status_code=201,
    summary="Registrar proceso de limpieza para un lote",
)
def crear_proceso_limpieza(
    body: ProcesoLimpiezaCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: ProcesoLimpiezaService = Depends(_svc_limpieza),
):
    return svc.crear(body, current_user.id)


# ---------------------------------------------------------------------------
# GET /api/v1/procesos-limpieza/{lote_id}
# ---------------------------------------------------------------------------

@router.get(
    "/procesos-limpieza/{lote_id}",
    response_model=ProcesoLimpiezaOut,
    summary="Obtener proceso de limpieza por lote de materia prima",
    dependencies=[_roles],
)
def obtener_proceso_limpieza(
    lote_id: int,
    svc: ProcesoLimpiezaService = Depends(_svc_limpieza),
):
    return svc.get_by_lote_or_404(lote_id)


# ---------------------------------------------------------------------------
# POST /api/v1/procesos-ablandamiento
# ---------------------------------------------------------------------------

@router.post(
    "/procesos-ablandamiento",
    response_model=ProcesoAblandamientoOut,
    status_code=201,
    summary="Registrar proceso de ablandamiento para un lote",
)
def crear_proceso_ablandamiento(
    body: ProcesoAblandamientoCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: ProcesoAblandamientoService = Depends(_svc_ablandamiento),
):
    return svc.crear(body, current_user.id)


# ---------------------------------------------------------------------------
# GET /api/v1/procesos-ablandamiento/{lote_id}
# ---------------------------------------------------------------------------

@router.get(
    "/procesos-ablandamiento/{lote_id}",
    response_model=ProcesoAblandamientoOut,
    summary="Obtener proceso de ablandamiento por lote de materia prima",
    dependencies=[_roles],
)
def obtener_proceso_ablandamiento(
    lote_id: int,
    svc: ProcesoAblandamientoService = Depends(_svc_ablandamiento),
):
    return svc.get_by_lote_or_404(lote_id)


# ---------------------------------------------------------------------------
# POST /api/v1/procesos-elaboracion-pulpa
# ---------------------------------------------------------------------------

@router.post(
    "/procesos-elaboracion-pulpa",
    response_model=ProcesoElaboracionOut,
    status_code=201,
    summary="Registrar proceso de elaboración de pulpa para un lote",
)
def crear_proceso_elaboracion(
    body: ProcesoElaboracionCreate,
    current_user=Depends(require_role(UserRole.operador_planta, UserRole.administrador)),
    svc: ProcesoElaboracionService = Depends(_svc_elaboracion),
):
    return svc.crear(body, current_user.id)
