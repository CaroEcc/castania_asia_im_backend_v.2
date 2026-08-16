from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Rol


class RolRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Rol]:
        return self.db.query(Rol).order_by(Rol.id).all()

    def get_by_id(self, rol_id: int) -> Optional[Rol]:
        return self.db.query(Rol).filter(Rol.id == rol_id).first()

    def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        return self.db.query(Rol).filter(Rol.nombre == nombre).first()

    def list_select(self) -> list[dict]:
        rows = self.db.query(Rol.id, Rol.nombre, Rol.metodo_auth).order_by(Rol.id).all()
        return [{"value": r.id, "label": r.nombre, "metodo_auth": r.metodo_auth} for r in rows]
