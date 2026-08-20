from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Despacho
from app.repositories.despachos import DespachoRepository
from app.repositories.lotes_terminado import LoteProductoTerminadoRepository
from app.schemas import DespachoCreate, RecepcionDestinoBody


class DespachoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DespachoRepository(db)
        self.lpt_repo = LoteProductoTerminadoRepository(db)

    def crear(self, body: DespachoCreate, responsable_id) -> Despacho:
        precio_bs_kg = body.precio_bs_kg or Decimal("0")

        items_data = []
        total_kg = Decimal("0")
        total_bs = Decimal("0")

        for item_body in body.items:
            lpt = self.lpt_repo.get_by_id(item_body.lote_producto_terminado_id)
            if not lpt:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Lote de producto terminado {item_body.lote_producto_terminado_id} no encontrado",
                )

            stock = lpt.stock_actual_kg or Decimal("0")
            if stock < item_body.peso_kg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente para el lote {lpt.numero_lote}: "
                        f"stock_actual={stock} kg, solicitado={item_body.peso_kg} kg"
                    ),
                )

            subtotal_bs = item_body.peso_kg * precio_bs_kg

            lpt.stock_actual_kg = stock - item_body.peso_kg
            if lpt.stock_actual_kg <= 0:
                lpt.estado = "despachado"
            else:
                lpt.estado = "parcialmente_despachado"

            total_kg += item_body.peso_kg
            total_bs += subtotal_bs
            items_data.append((item_body, lpt, subtotal_bs))

        return self.repo.create(body, responsable_id, items_data, total_kg, total_bs)

    def recepcion_destino(self, despacho_id: int, body: RecepcionDestinoBody) -> Despacho:
        despacho = self.repo.get_by_id(despacho_id)
        if not despacho:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Despacho {despacho_id} no encontrado",
            )
        return self.repo.update_recepcion_destino(despacho, body)
