from fastapi import APIRouter

from app.api.v1 import auth, comunidades, roles, recolectores, lotes

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(comunidades.router)
router.include_router(roles.router)
router.include_router(recolectores.router)
router.include_router(lotes.router)
