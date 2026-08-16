from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Rol
from app.repositories.roles import RolRepository


class RolService:
    def __init__(self, db: Session):
        self.repo = RolRepository(db)

    def listar(self) -> list[Rol]:
        return self.repo.list()

    def select(self) -> list[dict]:
        return self.repo.list_select()

    def obtener(self, rol_id: int) -> Rol:
        rol = self.repo.get_by_id(rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol {rol_id} no encontrado",
            )
        return rol
