from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Comunidad,
    Despacho,
    ItemChoqueTermico,
    ItemRecepcion,
    LoteMateriaPrima,
    LoteProductoTerminado,
    Recolector,
    SesionChoqueTermico,
)


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # Resumen / Dashboard
    # -------------------------------------------------------------------------

    def get_resumen(self) -> dict:
        """Snapshot de conteos por estado para el panel principal del administrador."""
        lotes_mp_raw = (
            self.db.query(LoteMateriaPrima.estado, func.count(LoteMateriaPrima.id))
            .group_by(LoteMateriaPrima.estado)
            .all()
        )
        lotes_mp = {estado: cnt for estado, cnt in lotes_mp_raw}

        lpts_raw = (
            self.db.query(LoteProductoTerminado.estado, func.count(LoteProductoTerminado.id))
            .group_by(LoteProductoTerminado.estado)
            .all()
        )
        lpts = {estado: cnt for estado, cnt in lpts_raw}

        total_recolectores = (
            self.db.query(func.count(Recolector.id))
            .filter(Recolector.estado == "activo")
            .scalar()
            or 0
        )
        total_despachos = self.db.query(func.count(Despacho.id)).scalar() or 0

        stock_camara_frio = (
            self.db.query(func.sum(LoteProductoTerminado.stock_actual_kg))
            .filter(LoteProductoTerminado.estado == "camara_frio")
            .scalar()
        )

        return {
            "lotes_materia_prima": {
                "abierto": lotes_mp.get("abierto", 0),
                "cerrado": lotes_mp.get("cerrado", 0),
                "en_limpieza": lotes_mp.get("en_limpieza", 0),
                "en_ablandamiento": lotes_mp.get("en_ablandamiento", 0),
                "en_elaboracion": lotes_mp.get("en_elaboracion", 0),
                "completado": lotes_mp.get("completado", 0),
                "rechazado": lotes_mp.get("rechazado", 0),
            },
            "lotes_producto_terminado": {
                "en_proceso": lpts.get("en_proceso", 0),
                "choque_termico": lpts.get("choque_termico", 0),
                "camara_frio": lpts.get("camara_frio", 0),
                "parcialmente_despachado": lpts.get("parcialmente_despachado", 0),
                "despachado": lpts.get("despachado", 0),
            },
            "total_recolectores_activos": total_recolectores,
            "total_despachos": total_despachos,
            "stock_camara_frio_kg": stock_camara_frio,
        }

    # -------------------------------------------------------------------------
    # Pipeline — todos los lotes MP con su etapa actual
    # -------------------------------------------------------------------------

    def get_pipeline(
        self,
        comunidad_id: Optional[int],
        estado: Optional[str],
    ) -> list[LoteMateriaPrima]:
        q = self.db.query(LoteMateriaPrima)
        if comunidad_id is not None:
            q = q.filter(LoteMateriaPrima.comunidad_id == comunidad_id)
        if estado is not None:
            q = q.filter(LoteMateriaPrima.estado == estado)
        return q.order_by(LoteMateriaPrima.fecha_apertura.desc()).all()

    # -------------------------------------------------------------------------
    # Reporte de acopio — totales por comunidad
    # -------------------------------------------------------------------------

    def get_reporte_acopio(
        self,
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
        comunidad_id: Optional[int],
    ) -> dict:
        q = (
            self.db.query(
                Comunidad.id_comunidad,
                Comunidad.nombre,
                func.count(LoteMateriaPrima.id.distinct()).label("total_lotes"),
                func.count(ItemRecepcion.id).label("total_recepciones"),
                func.coalesce(func.sum(ItemRecepcion.peso_kg), 0).label("total_kg"),
                func.coalesce(func.sum(ItemRecepcion.precio_total_bs), 0).label("total_bs"),
            )
            .join(LoteMateriaPrima, LoteMateriaPrima.comunidad_id == Comunidad.id_comunidad)
            .join(ItemRecepcion, ItemRecepcion.lote_materia_prima_id == LoteMateriaPrima.id)
        )

        if fecha_desde:
            q = q.filter(LoteMateriaPrima.fecha_apertura >= fecha_desde)
        if fecha_hasta:
            q = q.filter(LoteMateriaPrima.fecha_apertura <= fecha_hasta)
        if comunidad_id:
            q = q.filter(Comunidad.id_comunidad == comunidad_id)

        rows = q.group_by(Comunidad.id_comunidad, Comunidad.nombre).all()

        por_comunidad = [
            {
                "comunidad_id": r.id_comunidad,
                "comunidad_nombre": r.nombre,
                "total_lotes": r.total_lotes or 0,
                "total_recepciones": r.total_recepciones or 0,
                "total_kg": Decimal(str(r.total_kg or 0)),
                "total_bs": Decimal(str(r.total_bs or 0)),
            }
            for r in rows
        ]

        total_kg = sum(c["total_kg"] for c in por_comunidad)
        total_bs = sum(c["total_bs"] for c in por_comunidad)
        total_recepciones = sum(c["total_recepciones"] for c in por_comunidad)

        return {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "total_kg": total_kg,
            "total_bs": total_bs,
            "total_recepciones": total_recepciones,
            "por_comunidad": por_comunidad,
        }

    # -------------------------------------------------------------------------
    # Reporte de producción — rendimiento por tipo de pulpa
    # -------------------------------------------------------------------------

    def get_reporte_produccion(
        self,
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
    ) -> dict:
        q = self.db.query(
            LoteProductoTerminado.tipo_pulpa,
            func.count(LoteProductoTerminado.id).label("total_lotes"),
            func.sum(LoteProductoTerminado.total_kg_fruto).label("total_kg_fruto"),
            func.sum(LoteProductoTerminado.total_kg_pulpa).label("total_kg_pulpa"),
            func.avg(LoteProductoTerminado.rendimiento_pct).label("rendimiento_promedio"),
            func.sum(LoteProductoTerminado.stock_actual_kg).label("stock_actual_kg"),
        )
        if fecha_desde:
            q = q.filter(LoteProductoTerminado.fecha_proceso >= fecha_desde)
        if fecha_hasta:
            q = q.filter(LoteProductoTerminado.fecha_proceso <= fecha_hasta)

        rows = q.group_by(LoteProductoTerminado.tipo_pulpa).all()

        por_tipo_pulpa = [
            {
                "tipo_pulpa": r.tipo_pulpa,
                "total_lotes": r.total_lotes or 0,
                "total_kg_fruto": r.total_kg_fruto,
                "total_kg_pulpa": r.total_kg_pulpa,
                "rendimiento_promedio_pct": (
                    Decimal(str(r.rendimiento_promedio)).quantize(Decimal("0.01"))
                    if r.rendimiento_promedio is not None
                    else None
                ),
                "stock_actual_kg": r.stock_actual_kg,
            }
            for r in rows
        ]

        total_kg_fruto = (
            sum(r["total_kg_fruto"] for r in por_tipo_pulpa if r["total_kg_fruto"])
            or None
        )
        total_kg_pulpa = (
            sum(r["total_kg_pulpa"] for r in por_tipo_pulpa if r["total_kg_pulpa"])
            or None
        )

        return {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "por_tipo_pulpa": por_tipo_pulpa,
            "total_kg_fruto": total_kg_fruto,
            "total_kg_pulpa": total_kg_pulpa,
        }

    # -------------------------------------------------------------------------
    # Reporte de despachos
    # -------------------------------------------------------------------------

    def get_reporte_despachos(
        self,
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
    ) -> dict:
        q = self.db.query(Despacho)
        if fecha_desde:
            q = q.filter(Despacho.fecha_despacho >= fecha_desde)
        if fecha_hasta:
            q = q.filter(Despacho.fecha_despacho <= fecha_hasta)

        despachos = q.order_by(Despacho.fecha_despacho.desc()).all()

        total_kg = sum((d.total_kg or Decimal("0")) for d in despachos) or None
        total_bs = sum((d.total_bs or Decimal("0")) for d in despachos) or None

        return {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "total_despachos": len(despachos),
            "total_kg": total_kg,
            "total_bs": total_bs,
            "despachos": despachos,
        }

    # -------------------------------------------------------------------------
    # Trazabilidad completa de un lote de materia prima
    # -------------------------------------------------------------------------

    def get_trazabilidad_lote(self, numero_lote: str) -> dict:
        lote = (
            self.db.query(LoteMateriaPrima)
            .filter(LoteMateriaPrima.numero_lote == numero_lote)
            .first()
        )
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {numero_lote} no encontrado",
            )

        recepciones = [
            {
                "id": item.id,
                "recolector_id": item.recolector_id,
                "recolector_nombre": (
                    item.recolector.nombre_completo if item.recolector else ""
                ),
                "recolector_codigo": (
                    item.recolector.codigo if item.recolector else ""
                ),
                "peso_kg": item.peso_kg,
                "precio_bs_kg": item.precio_bs_kg,
                "precio_total_bs": item.precio_total_bs,
                "fecha_entrega": (
                    item.entrega_recolector.fecha_entrega
                    if item.entrega_recolector
                    else None
                ),
                "parcela": (
                    item.entrega_recolector.parcela
                    if item.entrega_recolector and item.entrega_recolector.parcela_id
                    else item.parcela
                ),
            }
            for item in lote.items_recepcion
        ]

        lote_out = {
            "id": lote.id,
            "numero_lote": lote.numero_lote,
            "comunidad_id": lote.comunidad_id,
            "responsable_id": lote.responsable_id,
            "es_organico": lote.es_organico,
            "fruto": lote.fruto,
            "fecha_apertura": lote.fecha_apertura,
            "fecha_cierre": lote.fecha_cierre,
            "total_kg": lote.total_kg,
            "total_bs": lote.total_bs,
            "estado": lote.estado,
            "motivo_rechazo": lote.motivo_rechazo,
            "rechazado_en": lote.rechazado_en,
            "vobo_control": lote.vobo_control,
            "vobo_planta": lote.vobo_planta,
            "total_recepciones": len(lote.items_recepcion),
        }

        # Choque térmico, cámara fría y despachos — agregados desde los LPTs
        lpts = []
        if lote.proceso_elaboracion:
            lpts = lote.proceso_elaboracion.lotes_producto_terminado

        # Sesiones de choque térmico únicas para los LPTs de este lote
        lpt_ids = [lpt.id for lpt in lpts]
        sesiones_choque = []
        if lpt_ids:
            items_choque = (
                self.db.query(ItemChoqueTermico)
                .filter(ItemChoqueTermico.lote_producto_terminado_id.in_(lpt_ids))
                .all()
            )
            sesion_ids = list({i.sesion_id for i in items_choque})
            if sesion_ids:
                sesiones_choque = (
                    self.db.query(SesionChoqueTermico)
                    .filter(SesionChoqueTermico.id.in_(sesion_ids))
                    .all()
                )

        # Inventarios de cámara fría
        camara_frio = [item for lpt in lpts for item in lpt.items_inventario]

        # Ítems de despacho enriquecidos con datos del despacho padre
        items_despacho = []
        for lpt in lpts:
            for item in lpt.items_despacho:
                items_despacho.append({
                    "id": item.id,
                    "despacho_id": item.despacho_id,
                    "numero_lote": item.numero_lote,
                    "peso_kg": item.peso_kg,
                    "numero_cajas": item.numero_cajas,
                    "subtotal_bs": item.subtotal_bs,
                    "fecha_despacho": item.fecha_despacho,
                    "numero_lote_despacho": item.despacho.numero_lote_despacho if item.despacho else None,
                    "destino_carga": item.despacho.destino_carga if item.despacho else None,
                })

        return {
            "lote": lote_out,
            "comunidad_nombre": lote.comunidad.nombre if lote.comunidad else "",
            "responsable_nombre": (
                lote.responsable.nombre_completo if lote.responsable else ""
            ),
            "recepciones": recepciones,
            "proceso_limpieza": lote.proceso_limpieza,
            "proceso_ablandamiento": lote.proceso_ablandamiento,
            "proceso_elaboracion": lote.proceso_elaboracion,
            "choque_termico": sesiones_choque or None,
            "camara_frio": camara_frio or None,
            "despachos": items_despacho or None,
        }
