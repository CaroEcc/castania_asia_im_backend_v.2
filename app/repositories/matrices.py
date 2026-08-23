from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import MatrizProcesos, ItemMatrizProcesos
from app.schemas import MatrizProcesosCreate


class MatrizProcesosRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lpt(self, lpt_id: int) -> Optional[MatrizProcesos]:
        return (
            self.db.query(MatrizProcesos)
            .filter(MatrizProcesos.lote_producto_terminado_id == lpt_id)
            .first()
        )

    def create(
        self,
        body: MatrizProcesosCreate,
        responsable_id,
    ) -> MatrizProcesos:
        matriz = MatrizProcesos(
            lote_producto_terminado_id=body.lote_producto_terminado_id,
            responsable_id=responsable_id,
            fecha=body.fecha,
        )
        self.db.add(matriz)
        self.db.flush()

        for item_data in body.items:
            item = ItemMatrizProcesos(
                matriz_id=matriz.id,
                proceso=item_data.proceso,
                responsable_nombre=item_data.responsable_nombre,
                tareas_principales=item_data.tareas_principales,
                herramientas_equipos=item_data.herramientas_equipos,
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(matriz)
        return matriz
