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

    def get_by_lpt_or_404(self, lpt_id: int) -> MatrizProcesos:
        lpt = self.lpt_repo.get_by_id(lpt_id)
        if not lpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote de producto terminado {lpt_id} no encontrado",
            )
        matriz = self.repo.get_by_lpt(lpt_id)
        if not matriz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El LPT {lpt_id} no tiene matriz de procesos registrada",
            )
        return matriz

    def crear(self, body: MatrizProcesosCreate, responsable_id) -> MatrizProcesos:
        lpt = self.lpt_repo.get_by_id(body.lote_producto_terminado_id)
        if not lpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote de producto terminado {body.lote_producto_terminado_id} no encontrado",
            )

        return self.repo.create(body, responsable_id)
