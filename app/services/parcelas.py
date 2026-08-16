from __future__ import annotations

import math
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Parcela
from app.repositories.parcelas import ParcelaRepository
from app.schemas import ParcelaCreate, ParcelaUpdate

_ESTADOS_VALIDOS = {"activa", "inactiva"}


def _calcular_superficie_ha(poligono_gps: dict) -> Optional[Decimal]:
    """
    Calcula la superficie en hectáreas de un GeoJSON Polygon usando la fórmula
    del área esférica (shoelace + corrección por latitud).
    Devuelve None si el polígono no es válido o tiene menos de 3 vértices.
    """
    try:
        coords = poligono_gps["coordinates"][0]  # primer ring (exterior)
        if len(coords) < 4:  # GeoJSON cierra el anillo, mínimo 3 vértices únicos
            return None

        # Coordenadas: [lon, lat]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]

        # Área por fórmula shoelace en grados²
        n = len(lons)
        area_deg2 = 0.0
        for i in range(n):
            j = (i + 1) % n
            area_deg2 += lons[i] * lats[j]
            area_deg2 -= lons[j] * lats[i]
        area_deg2 = abs(area_deg2) / 2.0

        # Conversión grados² → km² usando latitud central del polígono
        lat_centro = sum(lats) / len(lats)
        km_por_lat = 110.574                           # km por grado de latitud
        km_por_lon = 111.320 * math.cos(math.radians(lat_centro))
        area_km2 = area_deg2 * km_por_lat * km_por_lon

        # 1 km² = 100 ha
        return Decimal(str(round(area_km2 * 100, 4)))
    except (KeyError, IndexError, TypeError, ValueError):
        return None


class ParcelaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ParcelaRepository(db)

    def _get_or_404(self, parcela_id: int) -> Parcela:
        parcela = self.repo.get_by_id(parcela_id)
        if not parcela:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcela {parcela_id} no encontrada",
            )
        return parcela

    def listar(self, recolector_id: int, estado: Optional[str]) -> list[Parcela]:
        if estado and estado not in _ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"estado debe ser uno de: {sorted(_ESTADOS_VALIDOS)}",
            )
        return self.repo.list_by_recolector(recolector_id, estado)

    def crear(self, recolector_id: int, body: ParcelaCreate) -> Parcela:
        superficie = None
        if body.poligono_gps:
            superficie = _calcular_superficie_ha(body.poligono_gps)

        # Si no se pudo calcular del polígono, usar el valor manual si fue enviado
        if superficie is None:
            superficie = body.superficie_ha

        return self.repo.create(
            recolector_id=recolector_id,
            codigo=body.codigo,
            poligono_gps=body.poligono_gps,
            superficie_ha=superficie,
            especie=body.especie,
            produccion_estimada_kg=body.produccion_estimada_kg,
            estado="activa",
        )

    def actualizar(
        self, parcela_id: int, recolector_id: int, body: ParcelaUpdate
    ) -> Parcela:
        parcela = self._get_or_404(parcela_id)
        if parcela.recolector_id != recolector_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para editar esta parcela",
            )

        updates: dict[str, Any] = body.model_dump(exclude_unset=True)

        if "estado" in updates and updates["estado"] not in _ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"estado debe ser uno de: {sorted(_ESTADOS_VALIDOS)}",
            )

        # Recalcular superficie si llegó un nuevo polígono
        if "poligono_gps" in updates and updates["poligono_gps"]:
            calculada = _calcular_superficie_ha(updates["poligono_gps"])
            if calculada is not None:
                updates["superficie_ha"] = calculada

        if not updates:
            return parcela
        return self.repo.update(parcela, **updates)
