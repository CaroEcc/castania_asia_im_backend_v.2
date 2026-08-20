from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import LoteProductoTerminado


class LoteProductoTerminadoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, lote_id: int) -> Optional[LoteProductoTerminado]:
        return (
            self.db.query(LoteProductoTerminado)
            .filter(LoteProductoTerminado.id == lote_id)
            .first()
        )

    def list_all(self, estado: Optional[str] = None) -> list[LoteProductoTerminado]:
        q = self.db.query(LoteProductoTerminado)
        if estado is not None:
            q = q.filter(LoteProductoTerminado.estado == estado)
        return q.order_by(LoteProductoTerminado.id.desc()).all()

    def generate_numero_lote(self, seq: Optional[int] = None) -> str:
        """Formato: LPT-{YYYYMMDD}-{HHMM} o LPT-{YYYYMMDD}-{HHMM}-{seq}"""
        ahora = datetime.utcnow()
        base = f"LPT-{ahora.strftime('%Y%m%d')}-{ahora.strftime('%H%M')}"
        if seq is not None:
            return f"{base}-{seq}"
        return base
