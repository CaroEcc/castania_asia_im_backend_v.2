from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Parcela


class ParcelaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_recolector(
        self,
        recolector_id: int,
        estado: Optional[str] = None,
    ) -> list[Parcela]:
        q = self.db.query(Parcela).filter(Parcela.recolector_id == recolector_id)
        if estado:
            q = q.filter(Parcela.estado == estado)
        return q.order_by(Parcela.id).all()

    def get_by_id(self, parcela_id: int) -> Optional[Parcela]:
        return self.db.query(Parcela).filter(Parcela.id == parcela_id).first()

    def create(self, **fields) -> Parcela:
        parcela = Parcela(**fields)
        self.db.add(parcela)
        self.db.commit()
        self.db.refresh(parcela)
        return parcela

    def update(self, parcela: Parcela, **fields) -> Parcela:
        for key, value in fields.items():
            setattr(parcela, key, value)
        self.db.commit()
        self.db.refresh(parcela)
        return parcela
