from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import LoteMateriaPrima
from app.repositories.lotes import LoteMateriaPrimaRepository
from app.schemas import LoteMateriaPrimaCreate, CerrarLoteBody, RechazarLoteBody

_ESTADOS_TERMINALES = {"completado", "rechazado"}

_ESTADOS_VALIDOS = {
    "abierto", "cerrado", "en_limpieza",
    "en_ablandamiento", "en_elaboracion", "completado", "rechazado",
}


def _generar_numero_lote() -> str:
    """Formato: LMP-{YYYYMMDD}-{HHMM}"""
    ahora = datetime.utcnow()
    return f"LMP-{ahora.strftime('%Y%m%d')}-{ahora.strftime('%H%M')}"


class LoteMateriaPrimaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LoteMateriaPrimaRepository(db)

    def _get_or_404(self, lote_id: int) -> LoteMateriaPrima:
        lote = self.repo.get_by_id(lote_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lote {lote_id} no encontrado",
            )
        return lote

    def get_activo(self, comunidad_id: int) -> LoteMateriaPrima:
        lote = self.repo.get_activo(comunidad_id)
        if not lote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay lote activo para esta comunidad",
            )
        return lote

    def abrir(self, body: LoteMateriaPrimaCreate, responsable_id) -> LoteMateriaPrima:
        # Solo puede haber un lote abierto por comunidad
        existente = self.repo.get_activo(body.comunidad_id)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un lote abierto para esta comunidad: {existente.numero_lote}",
            )
        return self.repo.create(
            numero_lote=_generar_numero_lote(),
            comunidad_id=body.comunidad_id,
            responsable_id=responsable_id,
            es_organico=body.es_organico,
            fruto=body.fruto,
            fecha_apertura=datetime.utcnow(),
            total_kg=0,
            total_bs=0,
            estado="abierto",
        )

    def cerrar(self, lote_id: int, body: CerrarLoteBody) -> LoteMateriaPrima:
        lote = self._get_or_404(lote_id)
        if lote.estado != "abierto":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Solo se puede cerrar un lote en estado 'abierto' (actual: {lote.estado})",
            )
        if lote.total_kg == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se puede cerrar un lote sin recepciones (total_kg == 0)",
            )
        return self.repo.update(
            lote,
            estado="cerrado",
            fecha_cierre=datetime.utcnow(),
            vobo_control=body.vobo_control,
        )

    def rechazar(self, lote_id: int, body: RechazarLoteBody) -> LoteMateriaPrima:
        lote = self._get_or_404(lote_id)
        if lote.estado in _ESTADOS_TERMINALES:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El lote ya está en estado terminal '{lote.estado}' y no puede rechazarse",
            )
        return self.repo.update(
            lote,
            estado="rechazado",
            motivo_rechazo=body.motivo_rechazo,
            rechazado_en=datetime.utcnow(),
        )

    def listar(
        self,
        comunidad_id: int | None,
        estado: str | None,
    ) -> list[LoteMateriaPrima]:
        if estado and estado not in _ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"estado debe ser uno de: {sorted(_ESTADOS_VALIDOS)}",
            )
        return self.repo.list(comunidad_id=comunidad_id, estado=estado)
