from enum import Enum

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token


class UserRole(str, Enum):
    recolector = "recolector"
    responsable_acopio = "responsable_acopio"
    operador_planta = "operador_planta"
    administrador = "administrador"


_bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
):
    # TODO: move this import to a proper repository once the users domain
    # is wired up under app/api/v1/usuarios.py + app/repositories/usuarios.py
    from app.models import UsuarioSistema

    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise exc
    except JWTError:
        raise exc

    usuario = db.query(UsuarioSistema).filter(
        UsuarioSistema.id == user_id,
        UsuarioSistema.activo == True,
    ).first()
    if usuario is None:
        raise exc
    return usuario


def require_role(*roles: UserRole):
    """Dependency factory: restricts an endpoint to users with one of the given roles."""
    def _check(current_user=Depends(get_current_user)):
        try:
            user_role = UserRole(current_user.rol)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol no reconocido",
            )
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {[r.value for r in roles]}",
            )
        return current_user
    return _check
