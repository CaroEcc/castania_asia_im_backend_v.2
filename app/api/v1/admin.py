from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, UserRole
from app.schemas import (
    AdminResumenOut,
    AdminPipelineOut,
    LotePipelineOut,
    AdminReporteAcopioOut,
    AdminReporteProduccionOut,
    AdminReporteDespachosOut,
    TrazabilidadLoteOut,
)
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["Administrador"])

_solo_admin = Depends(require_role(UserRole.administrador))


def _svc(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)


# ---------------------------------------------------------------------------
# GET /api/v1/admin/resumen — Dashboard general
# ---------------------------------------------------------------------------

@router.get(
    "/resumen",
    response_model=AdminResumenOut,
    summary="Panel general: conteos por estado de lotes y LPTs",
    dependencies=[_solo_admin],
)
def resumen(svc: AdminService = Depends(_svc)):
    """
    Snapshot del estado de toda la cadena productiva:
    - Lotes de materia prima por estado
    - Lotes de producto terminado por estado
    - Total recolectores activos
    - Total despachos registrados
    - Stock actual en cámara de frío (kg)
    """
    return svc.get_resumen()


# ---------------------------------------------------------------------------
# GET /api/v1/admin/pipeline — Cola de trabajo global
# ---------------------------------------------------------------------------

@router.get(
    "/pipeline",
    response_model=AdminPipelineOut,
    summary="Cola de trabajo global: todos los lotes con su etapa actual",
    dependencies=[_solo_admin],
)
def pipeline(
    comunidad_id: Optional[int] = Query(None, description="Filtrar por comunidad"),
    estado: Optional[str] = Query(
        None,
        description="abierto | cerrado | en_limpieza | en_ablandamiento | en_elaboracion | completado | rechazado",
    ),
    svc: AdminService = Depends(_svc),
):
    """
    Lista todos los lotes de materia prima con comunidad, responsable, estado y totales.
    Permite al administrador ver de un vistazo qué está pasando en cada comunidad.
    """
    lotes = svc.get_pipeline(comunidad_id=comunidad_id, estado=estado)
    return AdminPipelineOut(
        total=len(lotes),
        lotes=[LotePipelineOut.model_validate(l) for l in lotes],
    )


# ---------------------------------------------------------------------------
# GET /api/v1/admin/reporte-acopio — Reporte de recepción de materia prima
# ---------------------------------------------------------------------------

@router.get(
    "/reporte-acopio",
    response_model=AdminReporteAcopioOut,
    summary="Reporte de acopio: kg y Bs recibidos por comunidad",
    dependencies=[_solo_admin],
)
def reporte_acopio(
    fecha_desde: Optional[date] = Query(None, description="Filtrar lotes abiertos desde esta fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar lotes abiertos hasta esta fecha"),
    comunidad_id: Optional[int] = Query(None, description="Filtrar por comunidad"),
    svc: AdminService = Depends(_svc),
):
    """
    Totales de materia prima recibida (kg y Bs) agrupados por comunidad.
    Incluye número de lotes y recepciones individuales por comunidad.
    """
    return svc.get_reporte_acopio(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        comunidad_id=comunidad_id,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/admin/reporte-produccion — Reporte de producción de pulpa
# ---------------------------------------------------------------------------

@router.get(
    "/reporte-produccion",
    response_model=AdminReporteProduccionOut,
    summary="Reporte de producción: rendimiento kg fruto → kg pulpa por tipo",
    dependencies=[_solo_admin],
)
def reporte_produccion(
    fecha_desde: Optional[date] = Query(None, description="Filtrar LPTs procesados desde esta fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar LPTs procesados hasta esta fecha"),
    svc: AdminService = Depends(_svc),
):
    """
    Rendimiento de producción agrupado por tipo de pulpa (premium / popular):
    kg de fruto ingresado, kg de pulpa producida, rendimiento promedio y stock actual.
    """
    return svc.get_reporte_produccion(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/admin/reporte-despachos — Reporte de despachos
# ---------------------------------------------------------------------------

@router.get(
    "/reporte-despachos",
    response_model=AdminReporteDespachosOut,
    summary="Reporte de despachos: totales y listado por periodo",
    dependencies=[_solo_admin],
)
def reporte_despachos(
    fecha_desde: Optional[date] = Query(None, description="Filtrar despachos desde esta fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar despachos hasta esta fecha"),
    svc: AdminService = Depends(_svc),
):
    """
    Listado completo de despachos con totales acumulados (kg y Bs) para el periodo indicado.
    """
    return svc.get_reporte_despachos(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/admin/trazabilidad/lote/{lote_id} — Cadena completa de un lote
# ---------------------------------------------------------------------------

@router.get(
    "/trazabilidad/lote/{numero_lote}",
    response_model=TrazabilidadLoteOut,
    summary="Trazabilidad completa de un lote de materia prima",
    dependencies=[_solo_admin],
)
def trazabilidad_lote(
    numero_lote: str,
    svc: AdminService = Depends(_svc),
):
    """
    Cadena completa de trazabilidad para un lote de materia prima.
    Identificador natural: LMP-{YYYYMMDD}-{HHMM}
    """
    return svc.get_trazabilidad_lote(numero_lote)
