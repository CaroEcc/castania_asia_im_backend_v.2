# app/routes/usuarios.py
import random
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import get_password_hash
from app.core.deps import get_db, require_role, UserRole
from app.models import ROLES_PIN, UsuarioSistema
from app.schemas_sic import (
    EstadoUpdate,
    ResetCredencialRequest,
    ResetCredencialResponse,
    RolUsuario,
    UsuarioCreate,
    UsuarioCreateResponse,
    UsuarioOut,
    UsuarioUpdate,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios Sistema"])


def _generar_pin() -> str:
    return str(random.randint(100000, 999999))


def _get_or_404(db: Session, usuario_id: uuid.UUID) -> UsuarioSistema:
    usuario = (
        db.query(UsuarioSistema)
        .options(selectinload(UsuarioSistema.comunidades))
        .filter(UsuarioSistema.id == usuario_id)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


# ---------------------------------------------------------------------------
# GET /usuarios — lista paginada con filtros
# ---------------------------------------------------------------------------

@router.get("", response_model=List[UsuarioOut])
def listar_usuarios(
    rol: Optional[RolUsuario] = Query(None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = (
        db.query(UsuarioSistema)
        .options(selectinload(UsuarioSistema.comunidades))
        .filter(UsuarioSistema.rol != RolUsuario.recolector)
    )
    if rol is not None:
        q = q.filter(UsuarioSistema.rol == rol)
    if activo is not None:
        q = q.filter(UsuarioSistema.activo == activo)
    offset = (page - 1) * page_size
    return q.order_by(UsuarioSistema.fecha_creacion.desc()).offset(offset).limit(page_size).all()


# ---------------------------------------------------------------------------
# GET /usuarios/{id}
# ---------------------------------------------------------------------------

@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    return _get_or_404(db, usuario_id)


# ---------------------------------------------------------------------------
# POST /usuarios — solo administrador
# ---------------------------------------------------------------------------

@router.post("", response_model=UsuarioCreateResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    body: UsuarioCreate,
    current_user: UsuarioSistema = Depends(require_role(UserRole.administrador)),
    db: Session = Depends(get_db),
):
    # Validar username único — 409 explícito, nunca un 500 genérico
    if db.query(UsuarioSistema).filter(UsuarioSistema.username == body.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El username '{body.username}' ya está en uso",
        )

    es_rol_pin = body.rol in ROLES_PIN
    metodo_auth = "pin" if es_rol_pin else "password"

    pin_generado: Optional[str] = None
    if es_rol_pin:
        # PIN: usar el enviado o generar uno aleatorio de 6 dígitos
        raw_credencial = body.credencial if body.credencial else _generar_pin()
        pin_generado = raw_credencial  # se devuelve UNA SOLA VEZ en la respuesta
    else:
        raw_credencial = body.credencial  # ya validado como no-None por el schema

    nuevo = UsuarioSistema(
        nombre_completo=body.nombre_completo,
        username=body.username,
        rol=body.rol,
        metodo_auth=metodo_auth,
        credencial_hash=get_password_hash(raw_credencial),
        comunidad=body.comunidad,
        activo=True,
        creado_por=current_user.id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    base = UsuarioOut.model_validate(nuevo)
    return UsuarioCreateResponse(**base.model_dump(), pin_generado=pin_generado)


# ---------------------------------------------------------------------------
# PUT /usuarios/{id} — actualiza solo nombre_completo y comunidad
# ---------------------------------------------------------------------------

@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: uuid.UUID,
    body: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    usuario = _get_or_404(db, usuario_id)

    if body.nombre_completo is not None:
        usuario.nombre_completo = body.nombre_completo
    if body.comunidad is not None:
        usuario.comunidad = body.comunidad

    db.commit()
    db.refresh(usuario)
    return usuario


# ---------------------------------------------------------------------------
# PATCH /usuarios/{id}/estado — activar / desactivar (soft delete)
# ---------------------------------------------------------------------------

@router.patch("/{usuario_id}/estado", response_model=UsuarioOut)
def cambiar_estado(
    usuario_id: uuid.UUID,
    body: EstadoUpdate,
    db: Session = Depends(get_db),
):
    usuario = _get_or_404(db, usuario_id)
    usuario.activo = body.activo
    db.commit()
    db.refresh(usuario)
    return usuario


# ---------------------------------------------------------------------------
# POST /usuarios/{id}/reset-credencial
# ---------------------------------------------------------------------------

@router.post("/{usuario_id}/reset-credencial", response_model=ResetCredencialResponse)
def reset_credencial(
    usuario_id: uuid.UUID,
    body: ResetCredencialRequest,
    db: Session = Depends(get_db),
):
    usuario = _get_or_404(db, usuario_id)

    pin_generado: Optional[str] = None

    if usuario.metodo_auth == "pin":
        # Genera un PIN nuevo; se ignora cualquier valor enviado en nueva_credencial
        pin_generado = _generar_pin()
        nueva = pin_generado
    else:
        if not body.nueva_credencial:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="nueva_credencial es obligatorio para roles con autenticación por password",
            )
        nueva = body.nueva_credencial

    usuario.credencial_hash = get_password_hash(nueva)
    db.commit()

    return ResetCredencialResponse(
        mensaje="Credencial actualizada exitosamente",
        pin_generado=pin_generado,
    )
