from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Recolector, EntregaRecolector, AutorizacionRecolector


class RecolectorRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Recolector
    # ------------------------------------------------------------------

    def get_by_id(self, recolector_id: int) -> Optional[Recolector]:
        return self.db.query(Recolector).filter(Recolector.id == recolector_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[Recolector]:
        return self.db.query(Recolector).filter(Recolector.codigo == codigo).first()

    def get_by_usuario_id(self, usuario_id) -> Optional[Recolector]:
        return (
            self.db.query(Recolector)
            .filter(Recolector.usuario_id == usuario_id)
            .first()
        )

    def list(
        self,
        *,
        comunidad_id: Optional[int] = None,
        estado: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[int, list[Recolector]]:
        q = self.db.query(Recolector)
        if comunidad_id is not None:
            q = q.filter(Recolector.comunidad_id == comunidad_id)
        if estado:
            q = q.filter(Recolector.estado == estado)
        if search:
            pattern = f"%{search}%"
            q = q.filter(
                Recolector.nombre_completo.ilike(pattern)
                | Recolector.codigo.ilike(pattern)
                | Recolector.ci.ilike(pattern)
            )
        total = q.count()
        items = (
            q.order_by(Recolector.nombre_completo)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return total, items

    def create(self, **fields) -> Recolector:
        rec = Recolector(**fields)
        self.db.add(rec)
        self.db.flush()
        return rec

    def update(self, recolector: Recolector, **fields) -> Recolector:
        for key, value in fields.items():
            setattr(recolector, key, value)
        self.db.commit()
        self.db.refresh(recolector)
        return recolector

    # ------------------------------------------------------------------
    # EntregaRecolector
    # ------------------------------------------------------------------

    def list_entregas(self, recolector_id: int) -> list[EntregaRecolector]:
        return (
            self.db.query(EntregaRecolector)
            .filter(EntregaRecolector.recolector_id == recolector_id)
            .order_by(EntregaRecolector.id.desc())
            .all()
        )

    def create_entrega(self, **fields) -> EntregaRecolector:
        entrega = EntregaRecolector(**fields)
        self.db.add(entrega)
        self.db.commit()
        self.db.refresh(entrega)
        return entrega

    # ------------------------------------------------------------------
    # Habilitación vigente
    # ------------------------------------------------------------------

    def get_habilitacion_vigente(
        self, recolector_id: int, cosecha: int
    ) -> Optional[AutorizacionRecolector]:
        return (
            self.db.query(AutorizacionRecolector)
            .filter(
                AutorizacionRecolector.recolector_id == recolector_id,
                AutorizacionRecolector.cosecha == cosecha,
            )
            .first()
        )
