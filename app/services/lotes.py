from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import LoteMateriaPrima
from app.repositories.lotes import LoteMateriaPrimaRepository


class LoteMateriaPrimaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LoteMateriaPrimaRepository(db)

    def get_activo(self, comunidad_id: int) -> LoteMateriaPrima:
        lote = self.repo.get_activo(comunidad_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay lote activo para esta comunidad",
            )
        return lote
