from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import LoteMateriaPrima


class LoteMateriaPrimaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_activo(self, comunidad_id: int) -> Optional[LoteMateriaPrima]:
        """Devuelve el único lote en estado 'abierto' de la comunidad, o None."""
        return (
            self.db.query(LoteMateriaPrima)
            .filter(
                LoteMateriaPrima.comunidad_id == comunidad_id,
                LoteMateriaPrima.estado == "abierto",
            )
            .first()
        )
