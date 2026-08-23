from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import EntregaRecolector, ItemRecepcion


class ItemRecepcionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> ItemRecepcion:
        item = ItemRecepcion(**fields)
        self.db.add(item)
        self.db.flush()
        return item

    def list_by_lote(self, lote_id: int) -> list[ItemRecepcion]:
        return (
            self.db.query(ItemRecepcion)
            .filter(ItemRecepcion.lote_materia_prima_id == lote_id)
            .order_by(ItemRecepcion.id)
            .all()
        )

    def get_entregas_sin_recepcion(self, recolector_id: int) -> list[EntregaRecolector]:
        """Entregas del recolector que aún no tienen ItemRecepcion vinculado ni fueron procesadas.

        Incluye entradas con estado_recepcion = NULL (nuevas del recolector) y las que
        no están en estado 'procesado'. NULL debe tratarse explícitamente porque
        NULL != 'procesado' evalúa a NULL (falso) en SQL.
        """
        vinculadas = (
            self.db.query(ItemRecepcion.entrega_recolector_id)
            .filter(ItemRecepcion.entrega_recolector_id.isnot(None))
            .subquery()
        )
        return (
            self.db.query(EntregaRecolector)
            .filter(
                EntregaRecolector.recolector_id == recolector_id,
                EntregaRecolector.id.not_in(vinculadas),
                or_(
                    EntregaRecolector.estado_recepcion.is_(None),
                    EntregaRecolector.estado_recepcion != "procesado",
                ),
            )
            .order_by(EntregaRecolector.id.desc())
            .all()
        )
