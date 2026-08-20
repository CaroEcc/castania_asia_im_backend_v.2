from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import SesionChoqueTermico, ItemChoqueTermico, LoteProductoTerminado
from app.schemas import SesionChoqueTermicoCreate


class SesionChoqueTermicoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        body: SesionChoqueTermicoCreate,
        responsable_id,
        lotes_map: dict,
    ) -> SesionChoqueTermico:
        sesion = SesionChoqueTermico(
            responsable_id=responsable_id,
            hora_inicio=body.hora_inicio,
            hora_final=body.hora_final,
            es_organico=body.es_organico,
            observaciones=body.observaciones,
            firma_responsable_planilla=body.firma_responsable_planilla,
            vobo_planta=body.vobo_planta,
            vobo_control_calidad=body.vobo_control_calidad,
        )
        self.db.add(sesion)
        self.db.flush()

        for item_data in body.items:
            item = ItemChoqueTermico(
                sesion_id=sesion.id,
                lote_producto_terminado_id=item_data.lote_producto_terminado_id,
                numero_freezer=item_data.numero_freezer,
                tipo_pulpa=item_data.tipo_pulpa,
                tipo_envase=item_data.tipo_envase,
                unidad=item_data.unidad,
                cantidad=item_data.cantidad,
                fecha_ingreso=item_data.fecha_ingreso,
                fecha_salida=item_data.fecha_salida,
            )
            self.db.add(item)

            lpt: LoteProductoTerminado = lotes_map[item_data.lote_producto_terminado_id]
            lpt.estado = "choque_termico"

        self.db.commit()
        self.db.refresh(sesion)
        return sesion
