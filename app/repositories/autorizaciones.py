from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import AutorizacionRecolector


class AutorizacionRecolectorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, autorizacion_id: int) -> Optional[AutorizacionRecolector]:
        return self.db.query(AutorizacionRecolector).filter(
            AutorizacionRecolector.id == autorizacion_id
        ).first()

    def get_by_comunidad_cosecha_recolector(
        self, comunidad_id: int, cosecha: int, recolector_id: int
    ) -> Optional[AutorizacionRecolector]:
        return self.db.query(AutorizacionRecolector).filter(
            AutorizacionRecolector.comunidad_id == comunidad_id,
            AutorizacionRecolector.cosecha == cosecha,
            AutorizacionRecolector.recolector_id == recolector_id,
        ).first()

    def list_by_comunidad_cosecha(
        self, comunidad_id: int, cosecha: int
    ) -> list[AutorizacionRecolector]:
        return (
            self.db.query(AutorizacionRecolector)
            .filter(
                AutorizacionRecolector.comunidad_id == comunidad_id,
                AutorizacionRecolector.cosecha == cosecha,
            )
            .all()
        )

    def habilitar(
        self, comunidad_id: int, cosecha: int, recolector_id: int
    ) -> AutorizacionRecolector:
        ar = AutorizacionRecolector(
            comunidad_id=comunidad_id,
            cosecha=cosecha,
            recolector_id=recolector_id,
        )
        self.db.add(ar)
        self.db.flush()
        return ar
