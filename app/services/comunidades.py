from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Comunidad
from app.repositories.comunidades import ComunidadRepository
from app.schemas import ComunidadCreate, ComunidadUpdate

_STATUS_VALIDOS = {"Activa", "Inactiva"}


class ComunidadService:
    def __init__(self, db: Session):
        self.repo = ComunidadRepository(db)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _get_or_404(self, comunidad_id: int) -> Comunidad:
        comunidad = self.repo.get_by_id(comunidad_id)
        if not comunidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comunidad {comunidad_id} no encontrada",
            )
        return comunidad

    def _check_nombre_unico(self, nombre: str, exclude_id: int | None = None):
        if self.repo.get_by_nombre(nombre, exclude_id=exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una comunidad con el nombre '{nombre}'",
            )

    def _check_abreviacion_unica(self, abreviacion: str, exclude_id: int | None = None):
        if self.repo.get_by_abreviacion(abreviacion, exclude_id=exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una comunidad con la abreviación '{abreviacion}'",
            )

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------

    def crear(self, body: ComunidadCreate) -> Comunidad:
        self._check_nombre_unico(body.nombre)
        self._check_abreviacion_unica(body.abreviacion)
        return self.repo.create(nombre=body.nombre, abreviacion=body.abreviacion)

    def listar(
        self,
        *,
        status: str | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[Comunidad]]:
        if status and status not in _STATUS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"status debe ser uno de: {sorted(_STATUS_VALIDOS)}",
            )
        return self.repo.list(status=status, search=search, page=page, page_size=page_size)

    def obtener(self, comunidad_id: int) -> Comunidad:
        return self._get_or_404(comunidad_id)

    def actualizar(self, comunidad_id: int, body: ComunidadUpdate) -> Comunidad:
        comunidad = self._get_or_404(comunidad_id)
        updates: dict = {}

        if body.nombre is not None:
            self._check_nombre_unico(body.nombre, exclude_id=comunidad_id)
            updates["nombre"] = body.nombre

        if body.abreviacion is not None:
            self._check_abreviacion_unica(body.abreviacion, exclude_id=comunidad_id)
            updates["abreviacion"] = body.abreviacion

        if body.status is not None:
            if body.status not in _STATUS_VALIDOS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"status debe ser uno de: {sorted(_STATUS_VALIDOS)}",
                )
            updates["status"] = body.status

        if not updates:
            return comunidad
        return self.repo.update(comunidad, **updates)

    def cambiar_status(self, comunidad_id: int, *, activar: bool) -> Comunidad:
        comunidad = self._get_or_404(comunidad_id)
        nuevo_status = "Activa" if activar else "Inactiva"
        if comunidad.status == nuevo_status:
            return comunidad
        return self.repo.update(comunidad, status=nuevo_status)

    def eliminar(self, comunidad_id: int) -> Comunidad:
        comunidad = self._get_or_404(comunidad_id)
        if comunidad.status == "Inactiva":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La comunidad '{comunidad.nombre}' ya está inactiva",
            )
        return self.repo.update(comunidad, status="Inactiva")

    def select(self) -> list[dict]:
        return [
            {"value": c.id_comunidad, "label": c.nombre, "abreviacion": c.abreviacion}
            for c in self.repo.list_activas()
        ]

    def estadisticas(self) -> dict:
        conteo = self.repo.count_by_status()
        total = sum(conteo.values())
        return {
            "total_comunidades": total,
            "comunidades_activas": conteo.get("Activa", 0),
            "comunidades_inactivas": conteo.get("Inactiva", 0),
        }
