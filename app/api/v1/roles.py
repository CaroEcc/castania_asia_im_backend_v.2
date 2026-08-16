from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas import RolOut
from app.services.roles import RolService

router = APIRouter(prefix="/roles", tags=["Roles v1"])


def _svc(db: Session = Depends(get_db)) -> RolService:
    return RolService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/roles  — cualquier rol autenticado
# ---------------------------------------------------------------------------

@router.get("", response_model=list[RolOut],
            dependencies=[Depends(get_current_user)])
def listar_roles(svc: RolService = Depends(_svc)):
    """Devuelve el catálogo completo de roles del sistema."""
    return svc.listar()


# ---------------------------------------------------------------------------
# GET /api/v1/roles/select  — cualquier rol autenticado
# ---------------------------------------------------------------------------

@router.get("/select", response_model=list[dict],
            dependencies=[Depends(get_current_user)])
def roles_para_select(svc: RolService = Depends(_svc)):
    """Lista simplificada de roles para poblar dropdowns."""
    return svc.select()


# ---------------------------------------------------------------------------
# GET /api/v1/roles/{id}  — cualquier rol autenticado
# ---------------------------------------------------------------------------

@router.get("/{rol_id}", response_model=RolOut,
            dependencies=[Depends(get_current_user)])
def obtener_rol(rol_id: int, svc: RolService = Depends(_svc)):
    return svc.obtener(rol_id)
