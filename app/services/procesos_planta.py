from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import LoteMateriaPrima, ProcesoLimpieza, ProcesoAblandamiento
from app.repositories.lotes import LoteMateriaPrimaRepository
from app.repositories.procesos_planta import (
    ProcesoLimpiezaRepository,
    ProcesoAblandamientoRepository,
    ProcesoElaboracionRepository,
)
from app.repositories.lotes_terminado import LoteProductoTerminadoRepository
from app.schemas import (
    ProcesoLimpiezaCreate,
    ProcesoAblandamientoCreate,
    ProcesoElaboracionCreate,
)


class ProcesoLimpiezaService:
    def __init__(self, db: Session):
        self.db = db
        self.lote_repo = LoteMateriaPrimaRepository(db)
        self.repo = ProcesoLimpiezaRepository(db)

    def _get_lote_or_404(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.lote_repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        return lote

    def get_by_lote_or_404(self, lote_id: int) -> ProcesoLimpieza:
        proceso = self.repo.get_by_lote(lote_id)
        if not proceso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe proceso de limpieza para el lote {lote_id}",
            )
        return proceso

    def crear(self, body: ProcesoLimpiezaCreate, responsable_id):
        lote = self._get_lote_or_404(body.lote_materia_prima_id)

        if lote.estado != "cerrado" or not lote.vobo_planta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote debe estar cerrado con VoBo de planta",
            )

        return self.repo.create(lote, body, responsable_id)


class ProcesoAblandamientoService:
    def __init__(self, db: Session):
        self.db = db
        self.lote_repo = LoteMateriaPrimaRepository(db)
        self.limpieza_repo = ProcesoLimpiezaRepository(db)
        self.repo = ProcesoAblandamientoRepository(db)

    def _get_lote_or_404(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.lote_repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        return lote

    def get_by_lote_or_404(self, lote_id: int) -> ProcesoAblandamiento:
        proceso = self.repo.get_by_lote(lote_id)
        if not proceso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe proceso de ablandamiento para el lote {lote_id}",
            )
        return proceso

    def crear(self, body: ProcesoAblandamientoCreate, responsable_id):
        lote = self._get_lote_or_404(body.lote_materia_prima_id)

        if lote.estado != "en_limpieza":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El lote debe estar en estado 'en_limpieza' (actual: {lote.estado})",
            )

        proceso_limpieza = self.limpieza_repo.get_by_lote(lote.id)
        if not proceso_limpieza:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe proceso de limpieza para este lote",
            )

        subprocesos_data = []
        for sp in body.subprocesos:
            if sp.temp_inicio is not None and sp.temp_final is not None:
                diferencia_temp = sp.temp_inicio - sp.temp_final
            else:
                diferencia_temp = None
            subprocesos_data.append((sp, diferencia_temp))

        return self.repo.create(lote, proceso_limpieza, body, responsable_id, subprocesos_data)


class ProcesoElaboracionService:
    def __init__(self, db: Session):
        self.db = db
        self.lote_repo = LoteMateriaPrimaRepository(db)
        self.ablandamiento_repo = ProcesoAblandamientoRepository(db)
        self.repo = ProcesoElaboracionRepository(db)
        self.lpt_repo = LoteProductoTerminadoRepository(db)

    def _get_lote_or_404(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.lote_repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        return lote

    def crear(self, body: ProcesoElaboracionCreate, responsable_id):
        lote = self._get_lote_or_404(body.lote_materia_prima_id)

        if lote.estado != "en_ablandamiento":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El lote debe estar en estado 'en_ablandamiento' (actual: {lote.estado})",
            )

        proceso_ablandamiento = self.ablandamiento_repo.get_by_lote(lote.id)
        if not proceso_ablandamiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe proceso de ablandamiento para este lote",
            )

        n = len(body.lotes_producto_terminado)
        lotes_terminado_data = []
        for idx, lpt_data in enumerate(body.lotes_producto_terminado):
            if lpt_data.total_kg_pulpa is not None and lpt_data.total_kg_fruto is not None and lpt_data.total_kg_fruto > 0:
                rendimiento_pct = (lpt_data.total_kg_pulpa / lpt_data.total_kg_fruto) * 100
            else:
                rendimiento_pct = None

            if n > 1:
                numero_lote = self.lpt_repo.generate_numero_lote(seq=idx + 1)
            else:
                numero_lote = self.lpt_repo.generate_numero_lote()

            lotes_terminado_data.append((lpt_data, numero_lote, rendimiento_pct))

        return self.repo.create(lote, proceso_ablandamiento, body, responsable_id, lotes_terminado_data)


class VoboPlantaService:
    def __init__(self, db: Session):
        self.db = db
        self.lote_repo = LoteMateriaPrimaRepository(db)

    def dar_vobo(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.lote_repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        if lote.estado != "cerrado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se puede dar VoBo a un lote en estado 'cerrado' (actual: {lote.estado})",
            )
        return self.lote_repo.update(lote, vobo_planta=True)
