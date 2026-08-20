from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import LoteMateriaPrima


class LoteMateriaPrimaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, lote_id: int) -> Optional[LoteMateriaPrima]:
        return self.db.query(LoteMateriaPrima).filter(LoteMateriaPrima.id == lote_id).first()

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

    def list(
        self,
        *,
        comunidad_id: Optional[int] = None,
        estado: Optional[str] = None,
    ) -> list[LoteMateriaPrima]:
        q = self.db.query(LoteMateriaPrima)
        if comunidad_id is not None:
            q = q.filter(LoteMateriaPrima.comunidad_id == comunidad_id)
        if estado is not None:
            q = q.filter(LoteMateriaPrima.estado == estado)
        return q.order_by(LoteMateriaPrima.fecha_apertura.desc()).all()

    def create(self, **fields) -> LoteMateriaPrima:
        lote = LoteMateriaPrima(**fields)
        self.db.add(lote)
        self.db.commit()
        self.db.refresh(lote)
        return lote

    def update(self, lote: LoteMateriaPrima, **fields) -> LoteMateriaPrima:
        for key, value in fields.items():
            setattr(lote, key, value)
        self.db.commit()
        self.db.refresh(lote)
        return lote
