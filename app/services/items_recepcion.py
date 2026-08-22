from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import EntregaRecolector, LoteMateriaPrima
from app.repositories.items_recepcion import ItemRecepcionRepository
from app.repositories.lotes import LoteMateriaPrimaRepository
from app.schemas import ItemRecepcionCreate, ItemRecepcionOut

_TIPOS_ASAI_VALIDOS = {"altura", "bajio"}


class ItemRecepcionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ItemRecepcionRepository(db)
        self.lote_repo = LoteMateriaPrimaRepository(db)

    def _get_lote_abierto_or_404(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.lote_repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        if lote.estado != "abierto":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El lote '{lote.numero_lote}' no está abierto (estado: {lote.estado})",
            )
        return lote

    def registrar(self, lote_id: int, body: ItemRecepcionCreate) -> dict:
        lote = self._get_lote_abierto_or_404(lote_id)

        if body.tipo_asai and body.tipo_asai not in _TIPOS_ASAI_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"tipo_asai debe ser uno de: {sorted(_TIPOS_ASAI_VALIDOS)}",
            )

        precio_total = body.peso_kg * body.precio_bs_kg

        # Advertencia si los pesos difieren del estimado de campo
        advertencias = []
        if body.entrega_recolector_id:
            entrega = self.db.query(EntregaRecolector).filter(
                EntregaRecolector.id == body.entrega_recolector_id
            ).first()
            if entrega and entrega.peso_kg != body.peso_kg:
                diff = abs(body.peso_kg - entrega.peso_kg)
                advertencias.append(
                    f"El peso registrado ({body.peso_kg} kg) difiere del peso declarado "
                    f"por el recolector ({entrega.peso_kg} kg). Diferencia: {diff} kg."
                )

        item = self.repo.create(
            lote_materia_prima_id=lote_id,
            recolector_id=body.recolector_id,
            entrega_recolector_id=body.entrega_recolector_id,
            autorizacion_recolector_id=body.autorizacion_recolector_id,
            zona_autorizacion=body.zona_autorizacion,
            tipo_asai=body.tipo_asai,
            numero_compra=body.numero_compra,
            peso_kg=body.peso_kg,
            precio_bs_kg=body.precio_bs_kg,
            precio_total_bs=precio_total,
            firma_entrega=body.firma_entrega,
            firma_pago=body.firma_pago,
        )

        # Actualizar totales del lote
        nuevo_total_kg = lote.total_kg + body.peso_kg
        nuevo_total_bs = lote.total_bs + precio_total
        self.lote_repo.update(lote, total_kg=nuevo_total_kg, total_bs=nuevo_total_bs)

        self.db.commit()
        self.db.refresh(item)

        out = ItemRecepcionOut.model_validate(item)
        if advertencias:
            return {**out.model_dump(), "advertencias": advertencias}
        return out

    def listar_por_lote(self, lote_id: int):
        return self.repo.list_by_lote(lote_id)

    def entregas_sin_recepcion(self, recolector_id: int):
        return self.repo.get_entregas_sin_recepcion(recolector_id)
