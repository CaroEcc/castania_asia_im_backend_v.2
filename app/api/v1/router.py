from fastapi import APIRouter

from app.api.v1 import auth, comunidades

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(comunidades.router)

# Routers adicionales se agregan aquí a medida que se implementen los módulos:
# from app.api.v1 import usuarios, lotes, sincronizacion
# router.include_router(usuarios.router)
