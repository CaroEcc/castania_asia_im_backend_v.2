from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Comunidad


class ComunidadRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, comunidad_id: int) -> Optional[Comunidad]:
        return self.db.query(Comunidad).filter(Comunidad.id_comunidad == comunidad_id).first()

    def get_by_nombre(self, nombre: str, exclude_id: Optional[int] = None) -> Optional[Comunidad]:
        q = self.db.query(Comunidad).filter(func.lower(Comunidad.nombre) == nombre.lower())
        if exclude_id is not None:
            q = q.filter(Comunidad.id_comunidad != exclude_id)
        return q.first()

    def get_by_abreviacion(self, abreviacion: str, exclude_id: Optional[int] = None) -> Optional[Comunidad]:
        q = self.db.query(Comunidad).filter(func.lower(Comunidad.abreviacion) == abreviacion.lower())
        if exclude_id is not None:
            q = q.filter(Comunidad.id_comunidad != exclude_id)
        return q.first()

    def list(
        self,
        *,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[int, list[Comunidad]]:
        q = self.db.query(Comunidad)
        if status:
            q = q.filter(Comunidad.status == status)
        if search:
            pattern = f"%{search}%"
            q = q.filter(
                Comunidad.nombre.ilike(pattern) | Comunidad.abreviacion.ilike(pattern)
            )
        total = q.count()
        items = (
            q.order_by(Comunidad.nombre)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return total, items

    def list_activas(self) -> list[Comunidad]:
        return (
            self.db.query(Comunidad)
            .filter(Comunidad.status == "Activa")
            .order_by(Comunidad.nombre)
            .all()
        )

    def create(self, nombre: str, abreviacion: str) -> Comunidad:
        comunidad = Comunidad(nombre=nombre, abreviacion=abreviacion, status="Activa")
        self.db.add(comunidad)
        self.db.commit()
        self.db.refresh(comunidad)
        return comunidad

    def update(self, comunidad: Comunidad, **fields) -> Comunidad:
        for key, value in fields.items():
            setattr(comunidad, key, value)
        self.db.commit()
        self.db.refresh(comunidad)
        return comunidad

    def count_by_status(self) -> dict:
        rows = (
            self.db.query(Comunidad.status, func.count(Comunidad.id_comunidad))
            .group_by(Comunidad.status)
            .all()
        )
        return {status: count for status, count in rows}
