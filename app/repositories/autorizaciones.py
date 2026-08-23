from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import AutorizacionRecolector


class AutorizacionRecolectorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, autorizacion_id: int) -> Optional[AutorizacionRecolector]:
        return self.db.query(AutorizacionRecolector).filter(
            AutorizacionRecolector.id == autorizacion_id
        ).first()

    def get_by_lote_recolector(
        self, lote_id: int, recolector_id: int
    ) -> Optional[AutorizacionRecolector]:
        return self.db.query(AutorizacionRecolector).filter(
            AutorizacionRecolector.lote_materia_prima_id == lote_id,
            AutorizacionRecolector.recolector_id == recolector_id,
        ).first()

    def list_by_lote(self, lote_id: int) -> list[AutorizacionRecolector]:
        return (
            self.db.query(AutorizacionRecolector)
            .filter(AutorizacionRecolector.lote_materia_prima_id == lote_id)
            .all()
        )

    def habilitar(self, lote_id: int, recolector_id: int) -> AutorizacionRecolector:
        ar = AutorizacionRecolector(
            lote_materia_prima_id=lote_id,
            recolector_id=recolector_id,
        )
        self.db.add(ar)
        self.db.flush()
        return ar
