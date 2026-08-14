# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models import UsuarioSistema
from app.core.security import verify_password, create_access_token
from app.schemas_sic import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/token", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Obtiene un JWT. Funciona igual para roles PIN y password:
    se envía el username y la credencial (PIN o password).
    """
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
        rol=usuario.rol,
        nombre_completo=usuario.nombre_completo,
    )
