from fastapi import APIRouter

from app.api.v1 import auth, comunidades, roles, recolectores, parcelas, entregas_recolector, lotes, autorizaciones_zafra, items_recepcion

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(comunidades.router)
router.include_router(roles.router)
router.include_router(recolectores.router)
router.include_router(parcelas.router)
router.include_router(entregas_recolector.router)
router.include_router(lotes.router)
router.include_router(autorizaciones_zafra.router)
router.include_router(items_recepcion.router)
