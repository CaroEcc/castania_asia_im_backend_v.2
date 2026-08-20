from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import MatrizProcesos
from app.repositories.matrices import MatrizProcesosRepository
from app.repositories.lotes_terminado import LoteProductoTerminadoRepository
from app.schemas import MatrizProcesosCreate


class MatrizProcesosService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MatrizProcesosRepository(db)
        self.lpt_repo = LoteProductoTerminadoRepository(db)

    def crear(self, body: MatrizProcesosCreate, responsable_id) -> MatrizProcesos:
        lpt = self.lpt_repo.get_by_id(body.lote_producto_terminado_id)
        if not lpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote de producto terminado {body.lote_producto_terminado_id} no encontrado",
            )

        return self.repo.create(body, responsable_id)
