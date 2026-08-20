from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import AutorizacionZafra, AutorizacionRecolector, Recolector
from app.repositories.autorizaciones import AutorizacionZafraRepository
from app.repositories.recolectores import RecolectorRepository
from app.schemas import AutorizacionZafraCreate, HabilitarRecolectoresBody


class AutorizacionZafraService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AutorizacionZafraRepository(db)
        self.rec_repo = RecolectorRepository(db)

    def _get_or_404(self, autorizacion_id: int) -> AutorizacionZafra:
        obj = self.repo.get_by_id(autorizacion_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Autorización de zafra {autorizacion_id} no encontrada",
            )
        return obj

    def _get_recolector_or_404(self, recolector_id: int) -> Recolector:
        rec = self.rec_repo.get_by_id(recolector_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recolector {recolector_id} no encontrado",
            )
        return rec

    def get_by_comunidad_cosecha(
        self, comunidad_id: int, cosecha: int
    ) -> AutorizacionZafra:
        obj = self.repo.get_by_comunidad_cosecha(comunidad_id, cosecha)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe autorización de zafra para comunidad {comunidad_id} y cosecha {cosecha}",
            )
        return obj

    def crear(self, body: AutorizacionZafraCreate, creado_por_id) -> AutorizacionZafra:
        # Solo puede existir una autorización por comunidad y cosecha
        existente = self.repo.get_by_comunidad_cosecha(body.comunidad_id, body.cosecha)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una autorización para la comunidad {body.comunidad_id} y cosecha {body.cosecha}",
            )

        autorizacion = self.repo.create(
            comunidad_id=body.comunidad_id,
            cosecha=body.cosecha,
            codigo_documento=body.codigo_documento,
            solicitante=body.solicitante,
            ci_solicitante=body.ci_solicitante,
            expediente=body.expediente,
            fecha_inicio_recoleccion=body.fecha_inicio_recoleccion,
            fecha_fin_recoleccion=body.fecha_fin_recoleccion,
            n_dias_recoleccion=body.n_dias_recoleccion,
            superficie_km2=body.superficie_km2,
            zona_autorizacion=body.zona_autorizacion,
            sello_sernap=body.sello_sernap,
            creado_por=creado_por_id,
        )

        # Habilitar recolectores incluidos en el body
        for recolector_id in body.recolector_ids:
            self._get_recolector_or_404(recolector_id)
            self.repo.habilitar_recolector(autorizacion.id, recolector_id)

        self.db.commit()
        self.db.refresh(autorizacion)
        return autorizacion

    def habilitar_recolectores(
        self, autorizacion_id: int, body: HabilitarRecolectoresBody, creado_por_id
    ) -> AutorizacionZafra:
        autorizacion = self._get_or_404(autorizacion_id)

        nuevos = []
        for recolector_id in body.recolector_ids:
            self._get_recolector_or_404(recolector_id)
            # Saltar si ya está habilitado
            if self.repo.get_autorizacion_recolector(autorizacion_id, recolector_id):
                continue
            nuevos.append(self.repo.habilitar_recolector(autorizacion_id, recolector_id))

        self.db.commit()
        self.db.refresh(autorizacion)
        return autorizacion

    def listar_recolectores_habilitados(
        self, comunidad_id: int, cosecha: int
    ) -> list:
        """
        Devuelve la lista de recolectores habilitados en la zafra con el badge
        de estado derivado de sus entregas e items de recepción.
        """
        from app.models import EntregaRecolector, ItemRecepcion

        autorizacion = self.repo.get_by_comunidad_cosecha(comunidad_id, cosecha)
        if not autorizacion:
            return []

        habilitados = self.repo.list_recolectores_habilitados(autorizacion.id)
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
                elif item.firma_entrega and item.estado_recepcion == "aceptado":
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
