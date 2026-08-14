from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role, UserRole
from app.schemas import ComunidadCreate, ComunidadListResponse, ComunidadOut, ComunidadUpdate
from app.services.comunidades import ComunidadService

router = APIRouter(prefix="/comunidades", tags=["Comunidades v1"])

_solo_admin = Depends(require_role(UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> ComunidadService:
    return ComunidadService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/comunidades  — solo administrador
# ---------------------------------------------------------------------------

@router.post("", response_model=ComunidadOut, status_code=status.HTTP_201_CREATED,
             dependencies=[_solo_admin])
def crear_comunidad(body: ComunidadCreate, svc: ComunidadService = Depends(_svc)):
    return svc.crear(body)


# ---------------------------------------------------------------------------
# GET /api/v1/comunidades  — cualquier JWT válido
# ---------------------------------------------------------------------------

@router.get("", response_model=ComunidadListResponse,
            dependencies=[Depends(get_current_user)])
def listar_comunidades(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="Activa | Inactiva"),
    search: Optional[str] = Query(None, description="Busca en nombre o abreviación"),
    svc: ComunidadService = Depends(_svc),
):
    total, items = svc.listar(status=status, search=search, page=page, page_size=page_size)
    return ComunidadListResponse(total=total, page=page, page_size=page_size, comunidades=items)


# ---------------------------------------------------------------------------
# GET /api/v1/comunidades/select  — cualquier JWT válido
# ---------------------------------------------------------------------------

@router.get("/select", response_model=list[dict],
            dependencies=[Depends(get_current_user)])
def comunidades_para_select(svc: ComunidadService = Depends(_svc)):
    """Lista simplificada de comunidades activas para poblar dropdowns."""
    return svc.select()


# ---------------------------------------------------------------------------
# GET /api/v1/comunidades/stats  — cualquier JWT válido
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=dict,
            dependencies=[Depends(get_current_user)])
def estadisticas(svc: ComunidadService = Depends(_svc)):
    return svc.estadisticas()


# ---------------------------------------------------------------------------
# GET /api/v1/comunidades/{id}  — cualquier JWT válido
# ---------------------------------------------------------------------------

@router.get("/{comunidad_id}", response_model=ComunidadOut,
            dependencies=[Depends(get_current_user)])
def obtener_comunidad(comunidad_id: int, svc: ComunidadService = Depends(_svc)):
    return svc.obtener(comunidad_id)


# ---------------------------------------------------------------------------
# PUT /api/v1/comunidades/{id}  — solo administrador
# ---------------------------------------------------------------------------

@router.put("/{comunidad_id}", response_model=ComunidadOut,
            dependencies=[_solo_admin])
def actualizar_comunidad(
    comunidad_id: int, body: ComunidadUpdate, svc: ComunidadService = Depends(_svc)
):
    return svc.actualizar(comunidad_id, body)


# ---------------------------------------------------------------------------
# PATCH /api/v1/comunidades/{id}/status  — solo administrador
# ---------------------------------------------------------------------------

@router.patch("/{comunidad_id}/status", response_model=ComunidadOut,
              dependencies=[_solo_admin])
def cambiar_status(
    comunidad_id: int,
    activar: bool = Query(..., description="true → Activa | false → Inactiva"),
    svc: ComunidadService = Depends(_svc),
):
    return svc.cambiar_status(comunidad_id, activar=activar)


# ---------------------------------------------------------------------------
# DELETE /api/v1/comunidades/{id}  — solo administrador (soft delete → Inactiva)
# ---------------------------------------------------------------------------

@router.delete("/{comunidad_id}", response_model=ComunidadOut,
               dependencies=[_solo_admin])
def eliminar_comunidad(comunidad_id: int, svc: ComunidadService = Depends(_svc)):
    """Soft delete: pasa la comunidad a estado Inactiva."""
    return svc.eliminar(comunidad_id)
