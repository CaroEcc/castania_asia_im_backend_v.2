from __future__ import annotations

from fastapi import HTTPException, status
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

            # Última entrega del recolector
            entrega = (
                self.db.query(EntregaRecolector)
                .filter(EntregaRecolector.recolector_id == rec.id)
                .order_by(EntregaRecolector.id.desc())
                .first()
            )

            # Badge de estado — busca ItemRecepcion en este lote específico
            if entrega is None:
                badge = "sin_datos"
            else:
                item = (
                    self.db.query(ItemRecepcion)
                    .filter(
                        ItemRecepcion.entrega_recolector_id == entrega.id,
                        ItemRecepcion.lote_materia_prima_id == lote_id,
                    )
                    .first()
                )
                if item is None:
                    # También puede haber recepción sin entrega vinculada
                    item = (
                        self.db.query(ItemRecepcion)
                        .filter(
                            ItemRecepcion.recolector_id == rec.id,
                            ItemRecepcion.lote_materia_prima_id == lote_id,
                        )
                        .first()
                    )

                if item is None:
                    badge = "pendiente"
                elif item.firma_entrega:
                    badge = "recibido"
                else:
                    badge = "rechazado"

            resultado.append({
                "id": rec.id,
                "codigo": rec.codigo,
                "nombre_completo": rec.nombre_completo,
                "autorizacion_recolector_id": ar.id,
                "ultima_entrega_id": entrega.id if entrega else None,
                "fecha_recoleccion": entrega.fecha_recoleccion if entrega else None,
                "fecha_entrega": entrega.fecha_entrega if entrega else None,
                "tipo_envase": entrega.tipo_envase if entrega else None,
                "peso_kg": entrega.peso_kg if entrega else None,
                "hora_cosecha": str(entrega.hora_cosecha) if entrega and entrega.hora_cosecha else None,
                "hora_recepcion": str(entrega.hora_recepcion) if entrega and entrega.hora_recepcion else None,
                "medio_transporte": entrega.medio_transporte if entrega else None,
                "estado_recepcion": entrega.estado_recepcion if entrega else None,
                "observaciones": entrega.observaciones if entrega else None,
                "badge": badge,
            })

        return resultado
