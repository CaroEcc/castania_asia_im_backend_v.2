from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import SesionChoqueTermico
from app.repositories.choque_termico import SesionChoqueTermicoRepository
from app.repositories.lotes_terminado import LoteProductoTerminadoRepository
from app.schemas import SesionChoqueTermicoCreate


class SesionChoqueTermicoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SesionChoqueTermicoRepository(db)
        self.lpt_repo = LoteProductoTerminadoRepository(db)

    def crear(self, body: SesionChoqueTermicoCreate, responsable_id) -> SesionChoqueTermico:
        lotes_map = {}
        for item_data in body.items:
            lpt_id = item_data.lote_producto_terminado_id
            if lpt_id not in lotes_map:
                lpt = self.lpt_repo.get_by_id(lpt_id)
                if not lpt:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Lote de producto terminado {lpt_id} no encontrado",
                    )
                lotes_map[lpt_id] = lpt

        return self.repo.create(body, responsable_id, lotes_map)
