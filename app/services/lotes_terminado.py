from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import LoteProductoTerminado
from app.repositories.lotes_terminado import LoteProductoTerminadoRepository


class LoteProductoTerminadoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LoteProductoTerminadoRepository(db)

    def listar(self, estado: Optional[str] = None) -> list[LoteProductoTerminado]:
        return self.repo.list_all(estado=estado)

    def get_by_id(self, lote_id: int) -> LoteProductoTerminado:
        lote = self.repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote de producto terminado {lote_id} no encontrado",
            )
        return lote
