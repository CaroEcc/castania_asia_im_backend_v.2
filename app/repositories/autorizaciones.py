from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import AutorizacionZafra, AutorizacionRecolector


class AutorizacionZafraRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, autorizacion_id: int) -> Optional[AutorizacionZafra]:
        return self.db.query(AutorizacionZafra).filter(AutorizacionZafra.id == autorizacion_id).first()

    def get_by_comunidad_cosecha(self, comunidad_id: int, cosecha: int) -> Optional[AutorizacionZafra]:
        return (
            self.db.query(AutorizacionZafra)
            .filter(
                AutorizacionZafra.comunidad_id == comunidad_id,
                AutorizacionZafra.cosecha == cosecha,
            )
            .first()
        )

    def create(self, **fields) -> AutorizacionZafra:
        obj = AutorizacionZafra(**fields)
        self.db.add(obj)
        self.db.flush()
        return obj

    def get_autorizacion_recolector(
        self, autorizacion_id: int, recolector_id: int
    ) -> Optional[AutorizacionRecolector]:
        return (
            self.db.query(AutorizacionRecolector)
            .filter(
                AutorizacionRecolector.autorizacion_zafra_id == autorizacion_id,
                AutorizacionRecolector.recolector_id == recolector_id,
            )
            .first()
        )

    def habilitar_recolector(self, autorizacion_id: int, recolector_id: int) -> AutorizacionRecolector:
        ar = AutorizacionRecolector(
            autorizacion_zafra_id=autorizacion_id,
            recolector_id=recolector_id,
        )
        self.db.add(ar)
        self.db.flush()
        return ar

    def list_recolectores_habilitados(self, autorizacion_id: int) -> list[AutorizacionRecolector]:
        return (
            self.db.query(AutorizacionRecolector)
            .filter(AutorizacionRecolector.autorizacion_zafra_id == autorizacion_id)
            .all()
        )
