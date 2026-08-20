from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import InventarioCamaraFrio, LoteProductoTerminado
from app.schemas import InventarioCamaraFrioCreate


class InventarioCamaraFrioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        body: InventarioCamaraFrioCreate,
        responsable_id,
        lpt: LoteProductoTerminado,
    ) -> InventarioCamaraFrio:
        registro = InventarioCamaraFrio(
            responsable_id=responsable_id,
            lote_producto_terminado_id=body.lote_producto_terminado_id,
            tipo_pulpa=body.tipo_pulpa,
            estado=body.estado,
            tipo_envase=body.tipo_envase,
            unidad=body.unidad,
            cantidad=body.cantidad,
            fecha_ingreso=body.fecha_ingreso,
            fecha_salida=body.fecha_salida,
            observaciones=body.observaciones,
            firma_responsable_planilla=body.firma_responsable_planilla,
            vobo_planta=body.vobo_planta,
            vobo_control_calidad=body.vobo_control_calidad,
        )
        self.db.add(registro)

        lpt.estado = "camara_frio"

        self.db.commit()
        self.db.refresh(registro)
        return registro
