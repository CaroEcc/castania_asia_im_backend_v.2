from fastapi import APIRouter

from app.api.v1 import auth, comunidades, roles, recolectores

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(comunidades.router)
router.include_router(roles.router)
router.include_router(recolectores.router)

# Routers adicionales se agregan aquí a medida que se implementen los módulos:
# from app.api.v1 import lotes, sincronizacion
# router.include_router(lotes.router)
