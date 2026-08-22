from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth v1"])


class LoginRequest(BaseModel):
    username: str
    credencial: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: str
    rol: str
    nombre_completo: str


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticación unificada para todos los roles del sistema.
    Acepta username + credencial (PIN de 6 dígitos para recolectores,
    password para los demás roles).

    TODO: reemplazar el acceso directo al modelo por una llamada al
    repositorio de usuarios una vez que app/repositories/usuarios.py
    esté implementado (tarea separada).
    """
    from app.models import UsuarioSistema

    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.username == body.username,
        UsuarioSistema.activo == True,
    ).first()

    if not usuario or not verify_password(body.credencial, usuario.credencial_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(usuario.id), "rol": usuario.rol})
    return TokenResponse(
        access_token=token,
        usuario_id=str(usuario.id),
        rol=usuario.rol,
        nombre_completo=usuario.nombre_completo,
    )
