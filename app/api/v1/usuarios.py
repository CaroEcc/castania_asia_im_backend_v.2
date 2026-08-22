from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role, UserRole
from app.models import UsuarioSistema
from app.repositories.comunidades import ComunidadRepository
from app.schemas import ComunidadOut, ComunidadListBody

router = APIRouter(prefix="/usuarios", tags=["Usuarios v1"])

_solo_admin = Depends(require_role(UserRole.administrador))


def _get_responsable_or_404(db: Session, usuario_id: uuid.UUID) -> UsuarioSistema:
    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.id == usuario_id,
        UsuarioSistema.activo == True,
    ).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado o inactivo")
    if usuario.rol != "responsable_acopio":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El usuario no tiene rol responsable_acopio (tiene: {usuario.rol})",
        )
    return usuario


# ---------------------------------------------------------------------------
# GET /api/v1/usuarios/me/comunidades  — responsable_acopio autenticado
# ---------------------------------------------------------------------------

@router.get("/me/comunidades", response_model=list[ComunidadOut])
def mis_comunidades(
    current_user: UsuarioSistema = Depends(require_role(UserRole.responsable_acopio)),
    db: Session = Depends(get_db),
):
    """Comunidades asignadas al responsable de acopio autenticado. Usar tras el login para mostrar el selector de comunidad."""
    repo = ComunidadRepository(db)
    return repo.get_comunidades_by_usuario(current_user.id)


# ---------------------------------------------------------------------------
# GET /api/v1/usuarios/{id}/comunidades  — cualquier JWT válido
# ---------------------------------------------------------------------------

@router.get("/{usuario_id}/comunidades", response_model=list[ComunidadOut],
            dependencies=[Depends(get_current_user)])
def listar_comunidades_responsable(
    usuario_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Lista las comunidades asignadas a un responsable de acopio."""
    _get_responsable_or_404(db, usuario_id)
    repo = ComunidadRepository(db)
    return repo.get_comunidades_by_usuario(usuario_id)


# ---------------------------------------------------------------------------
# POST /api/v1/usuarios/{id}/comunidades  — solo administrador
# ---------------------------------------------------------------------------

@router.post("/{usuario_id}/comunidades", response_model=list[ComunidadOut],
             status_code=status.HTTP_201_CREATED, dependencies=[_solo_admin])
def asignar_comunidades(
    usuario_id: uuid.UUID,
    body: ComunidadListBody,
    db: Session = Depends(get_db),
):
    """Asigna una o más comunidades al responsable de acopio. Las ya asignadas se ignoran."""
    _get_responsable_or_404(db, usuario_id)
    repo = ComunidadRepository(db)

    for comunidad_id in body.comunidad_ids:
        comunidad = repo.get_by_id(comunidad_id)
        if not comunidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comunidad {comunidad_id} no encontrada",
            )
        repo.asignar_responsable(comunidad_id, usuario_id)

    return repo.get_comunidades_by_usuario(usuario_id)


# ---------------------------------------------------------------------------
# DELETE /api/v1/usuarios/{id}/comunidades/{comunidad_id}  — solo administrador
# ---------------------------------------------------------------------------

@router.delete("/{usuario_id}/comunidades/{comunidad_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[_solo_admin])
def desasignar_comunidad(
    usuario_id: uuid.UUID,
    comunidad_id: int,
    db: Session = Depends(get_db),
):
    """Elimina la asignación de una comunidad al responsable de acopio."""
    _get_responsable_or_404(db, usuario_id)
    repo = ComunidadRepository(db)
    removed = repo.desasignar_responsable(comunidad_id, usuario_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El responsable no tiene asignada la comunidad {comunidad_id}",
        )
