from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import AutorizacionRecolector, EntregaRecolector, ItemRecepcion, Recolector, LoteMateriaPrima
from app.repositories.autorizaciones import AutorizacionRecolectorRepository
from app.repositories.recolectores import RecolectorRepository
from app.schemas import HabilitarRecolectoresBody


class AutorizacionRecolectorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AutorizacionRecolectorRepository(db)
        self.rec_repo = RecolectorRepository(db)

    def _get_recolector_or_404(self, recolector_id: int) -> Recolector:
        rec = self.rec_repo.get_by_id(recolector_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recolector {recolector_id} no encontrado",
            )
        return rec

    def _get_lote_abierto_or_404(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.db.query(LoteMateriaPrima).filter(LoteMateriaPrima.id == lote_id).first()
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        if lote.estado != "abierto":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El lote '{lote.numero_lote}' no está abierto (estado: {lote.estado}). Solo se pueden habilitar recolectores en lotes abiertos.",
            )
        return lote

    def habilitar(self, body: HabilitarRecolectoresBody) -> list[AutorizacionRecolector]:
        """Habilita uno o varios recolectores para un lote activo. Idempotente."""
        self._get_lote_abierto_or_404(body.lote_id)

        for recolector_id in body.recolector_ids:
            self._get_recolector_or_404(recolector_id)
            existente = self.repo.get_by_lote_recolector(body.lote_id, recolector_id)
            if not existente:
                self.repo.habilitar(body.lote_id, recolector_id)

        self.db.commit()
        return self.repo.list_by_lote(body.lote_id)

    def listar_habilitados(self, lote_id: int) -> list[dict]:
        """
        Lista de trabajo diario: recolectores habilitados para el lote con badge de estado
        derivado de sus entregas e ítems de recepción en ese mismo lote.
        """
        habilitados = self.repo.list_by_lote(lote_id)
        resultado = []

        for ar in habilitados:
            rec = ar.recolector

            # ¿Existe ItemRecepcion para este recolector en este lote?
            item = (
                self.db.query(ItemRecepcion)
                .filter(
                    ItemRecepcion.recolector_id == rec.id,
                    ItemRecepcion.lote_materia_prima_id == lote_id,
                )
                .first()
            )

            # Entregas disponibles: sin ItemRecepcion vinculado y no procesadas
            vinculadas_ids = (
                self.db.query(ItemRecepcion.entrega_recolector_id)
                .filter(ItemRecepcion.entrega_recolector_id.isnot(None))
                .subquery()
            )
            entregas_disponibles = (
                self.db.query(EntregaRecolector)
                .filter(
                    EntregaRecolector.recolector_id == rec.id,
                    EntregaRecolector.id.not_in(vinculadas_ids),
                    or_(
                        EntregaRecolector.estado_recepcion.is_(None),
                        EntregaRecolector.estado_recepcion != "procesado",
                    ),
                )
                .order_by(EntregaRecolector.id.desc())
                .all()
            )
            entregas_pendientes_count = len(entregas_disponibles)
            ultima_entrega = entregas_disponibles[0] if entregas_disponibles else None

            if item is not None:
                # Ya tiene recepción registrada en este lote
                badge = "recibido" if item.firma_entrega else "rechazado"
            else:
                badge = "pendiente" if ultima_entrega is not None else "sin_datos"

            resultado.append({
                "id": rec.id,
                "codigo": rec.codigo,
                "nombre_completo": rec.nombre_completo,
                "autorizacion_recolector_id": ar.id,
                # Datos de la entrega más reciente disponible (o None si badge = sin_datos/recibido)
                "entregas_pendientes_count": entregas_pendientes_count,
                "ultima_entrega_id": ultima_entrega.id if ultima_entrega else None,
                "fecha_recoleccion": ultima_entrega.fecha_recoleccion if ultima_entrega else None,
                "fecha_entrega": ultima_entrega.fecha_entrega if ultima_entrega else None,
                "tipo_envase": ultima_entrega.tipo_envase if ultima_entrega else None,
                "peso_kg": ultima_entrega.peso_kg if ultima_entrega else None,
                "hora_cosecha": str(ultima_entrega.hora_cosecha) if ultima_entrega and ultima_entrega.hora_cosecha else None,
                "hora_recepcion": str(ultima_entrega.hora_recepcion) if ultima_entrega and ultima_entrega.hora_recepcion else None,
                "medio_transporte": ultima_entrega.medio_transporte if ultima_entrega else None,
                "observaciones": ultima_entrega.observaciones if ultima_entrega else None,
                "badge": badge,
            })

        return resultado
