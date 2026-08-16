from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role, UserRole
from app.schemas import (
    RecolectorCreate,
    RecolectorListResponse,
    RecolectorOut,
    RecolectorUpdate,
    EntregaRecolectorCreate,
    EntregaRecolectorOut,
    EntregaListResponse,
)
from app.services.recolectores import RecolectorService

router = APIRouter(prefix="/recolectores", tags=["Módulo 1 — Recolectores"])

# Shortcuts de permisos
_puede_crear = Depends(require_role(UserRole.responsable_acopio, UserRole.administrador))
_puede_editar = Depends(require_role(UserRole.responsable_acopio, UserRole.administrador))
_puede_crear_entrega = Depends(
    require_role(UserRole.recolector, UserRole.responsable_acopio, UserRole.administrador)
)


def _svc(db: Session = Depends(get_db)) -> RecolectorService:
    return RecolectorService(db)


# ---------------------------------------------------------------------------
# POST /api/v1/recolectores  — responsable_acopio o administrador
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=RecolectorOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_recolector(
    body: RecolectorCreate,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(require_role(UserRole.responsable_acopio, UserRole.administrador)),
):
    return svc.crear(body, current_user.id)


# ---------------------------------------------------------------------------
# GET /api/v1/recolectores  — cualquier JWT válido
#   recolector: solo ve el propio
#   responsable_acopio / administrador: lista paginada con filtros
# ---------------------------------------------------------------------------

@router.get("", response_model=RecolectorListResponse)
def listar_recolectores(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    comunidad_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None, description="activo | inactivo"),
    search: Optional[str] = Query(None, description="Busca en nombre, código o C.I."),
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(get_current_user),
):
    if current_user.rol == UserRole.recolector:
        rec = svc.repo.get_by_usuario_id(current_user.id)
        items = [rec] if rec else []
        return RecolectorListResponse(
            total=len(items), page=1, page_size=1, recolectores=items
        )

    total, items = svc.listar(
        comunidad_id=comunidad_id,
        estado=estado,
        search=search,
        page=page,
        page_size=page_size,
    )
    return RecolectorListResponse(total=total, page=page, page_size=page_size, recolectores=items)


# ---------------------------------------------------------------------------
# GET /api/v1/recolectores/{id}  — cualquier JWT válido
#   recolector: solo el propio
# ---------------------------------------------------------------------------

@router.get("/{recolector_id}", response_model=RecolectorOut)
def obtener_recolector(
    recolector_id: int,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(get_current_user),
):
    rec = svc.obtener(recolector_id)
    if current_user.rol == UserRole.recolector and str(rec.usuario_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede consultar su propio perfil",
        )
    return rec


# ---------------------------------------------------------------------------
# PUT /api/v1/recolectores/{id}  — responsable_acopio o administrador
# ---------------------------------------------------------------------------

@router.put("/{recolector_id}", response_model=RecolectorOut, dependencies=[_puede_editar])
def actualizar_recolector(
    recolector_id: int,
    body: RecolectorUpdate,
    svc: RecolectorService = Depends(_svc),
):
    return svc.actualizar(recolector_id, body)


# ---------------------------------------------------------------------------
# GET /api/v1/recolectores/{id}/entregas  — cualquier JWT válido
#   recolector: solo las propias
# ---------------------------------------------------------------------------

@router.get("/{recolector_id}/entregas", response_model=EntregaListResponse)
def listar_entregas(
    recolector_id: int,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(get_current_user),
):
    rec = svc.obtener(recolector_id)
    if current_user.rol == UserRole.recolector and str(rec.usuario_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puede consultar sus propias entregas",
        )
    entregas = svc.listar_entregas(recolector_id)
    return EntregaListResponse(
        total=len(entregas), recolector_id=recolector_id, entregas=entregas
    )


# ---------------------------------------------------------------------------
# POST /api/v1/recolectores/{id}/entregas
#   recolector: solo las propias | responsable_acopio | administrador
# ---------------------------------------------------------------------------

@router.post(
    "/{recolector_id}/entregas",
    response_model=EntregaRecolectorOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_puede_crear_entrega],
)
def crear_entrega(
    recolector_id: int,
    body: EntregaRecolectorCreate,
    svc: RecolectorService = Depends(_svc),
    current_user=Depends(get_current_user),
):
    # Recolector solo puede registrar entregas en su propio perfil
    if current_user.rol == UserRole.recolector:
        rec = svc.obtener(recolector_id)
        if str(rec.usuario_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede registrar sus propias entregas",
            )
    return svc.crear_entrega(recolector_id, body)
