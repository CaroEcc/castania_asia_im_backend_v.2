from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import AutorizacionRecolector, EntregaRecolector, ItemRecepcion, Recolector
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

    def habilitar(self, body: HabilitarRecolectoresBody) -> list[AutorizacionRecolector]:
        """Habilita uno o varios recolectores para una comunidad y cosecha. Idempotente."""
        for recolector_id in body.recolector_ids:
            self._get_recolector_or_404(recolector_id)
            existente = self.repo.get_by_comunidad_cosecha_recolector(
                body.comunidad_id, body.cosecha, recolector_id
            )
            if not existente:
                self.repo.habilitar(body.comunidad_id, body.cosecha, recolector_id)

        self.db.commit()
        return self.repo.list_by_comunidad_cosecha(body.comunidad_id, body.cosecha)

    def listar_habilitados(self, comunidad_id: int, cosecha: int) -> list[dict]:
        """
        Lista de trabajo diario: recolectores habilitados con badge de estado
        derivado de sus entregas e ítems de recepción.
        """
        habilitados = self.repo.list_by_comunidad_cosecha(comunidad_id, cosecha)
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

            # Badge de estado
            if entrega is None:
                badge = "sin_datos"
            else:
                item = (
                    self.db.query(ItemRecepcion)
                    .filter(ItemRecepcion.entrega_recolector_id == entrega.id)
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
