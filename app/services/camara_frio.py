from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import InventarioCamaraFrio
from app.repositories.camara_frio import InventarioCamaraFrioRepository
from app.repositories.lotes_terminado import LoteProductoTerminadoRepository
from app.schemas import InventarioCamaraFrioCreate


class InventarioCamaraFrioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventarioCamaraFrioRepository(db)
        self.lpt_repo = LoteProductoTerminadoRepository(db)

    def crear(self, body: InventarioCamaraFrioCreate, responsable_id) -> InventarioCamaraFrio:
        lpt = self.lpt_repo.get_by_id(body.lote_producto_terminado_id)
        if not lpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote de producto terminado {body.lote_producto_terminado_id} no encontrado",
            )

        return self.repo.create(body, responsable_id, lpt)
