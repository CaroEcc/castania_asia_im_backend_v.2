from fastapi import APIRouter

from app.api.v1 import (
    auth,
    comunidades,
    roles,
    recolectores,
    parcelas,
    entregas_recolector,
    lotes,
    autorizaciones_zafra,
    items_recepcion,
    procesos_planta,
    lotes_terminado,
    choque_termico,
    camara_frio,
    matrices,
    despachos,
    usuarios,
)

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
router.include_router(procesos_planta.router)
router.include_router(lotes_terminado.router)
router.include_router(choque_termico.router)
router.include_router(camara_frio.router)
router.include_router(matrices.router)
router.include_router(despachos.router)
router.include_router(usuarios.router)
