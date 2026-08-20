from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    LoteMateriaPrima,
    ProcesoLimpieza,
    SubprocesoLimpieza,
    ProcesoAblandamiento,
    SubprocesoAblandamiento,
    ProcesoElaboracionPulpa,
    LoteProductoTerminado,
)
from app.schemas import (
    ProcesoLimpiezaCreate,
    ProcesoAblandamientoCreate,
    ProcesoElaboracionCreate,
)


class ProcesoLimpiezaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lote(self, lote_id: int) -> Optional[ProcesoLimpieza]:
        return (
            self.db.query(ProcesoLimpieza)
            .filter(ProcesoLimpieza.lote_materia_prima_id == lote_id)
            .first()
        )

    def create(
        self,
        lote: LoteMateriaPrima,
        body: ProcesoLimpiezaCreate,
        responsable_id,
    ) -> ProcesoLimpieza:
        proceso = ProcesoLimpieza(
            lote_materia_prima_id=lote.id,
            responsable_id=responsable_id,
            hora_inicio=body.hora_inicio,
            hora_final=body.hora_final,
            total_kg_ingreso=lote.total_kg,
            total_kg_salida=body.total_kg_salida,
            numero_procesos=body.numero_procesos,
            es_organico=lote.es_organico,
            observaciones=body.observaciones,
            firma_responsable_planilla=body.firma_responsable_planilla,
            vobo_planta=body.vobo_planta,
            vobo_control_calidad=body.vobo_control_calidad,
        )
        self.db.add(proceso)
        self.db.flush()

        for sp_data in body.subprocesos:
            subproceso = SubprocesoLimpieza(
                proceso_limpieza_id=proceso.id,
                numero_proceso=sp_data.numero_proceso,
                hora_inicio_seco=sp_data.hora_inicio_seco,
                hora_final_seco=sp_data.hora_final_seco,
                residuos_kg=sp_data.residuos_kg,
                tipo_recipiente_inmersion=sp_data.tipo_recipiente_inmersion,
                hora_inicio_lavado=sp_data.hora_inicio_lavado,
                hora_final_lavado=sp_data.hora_final_lavado,
            )
            self.db.add(subproceso)

        lote.estado = "en_limpieza"
        self.db.commit()
        self.db.refresh(proceso)
        return proceso


class ProcesoAblandamientoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lote(self, lote_id: int) -> Optional[ProcesoAblandamiento]:
        return (
            self.db.query(ProcesoAblandamiento)
            .filter(ProcesoAblandamiento.lote_materia_prima_id == lote_id)
            .first()
        )

    def create(
        self,
        lote: LoteMateriaPrima,
        proceso_limpieza: ProcesoLimpieza,
        body: ProcesoAblandamientoCreate,
        responsable_id,
        subprocesos_data: list,
    ) -> ProcesoAblandamiento:
        proceso = ProcesoAblandamiento(
            lote_materia_prima_id=lote.id,
            proceso_limpieza_id=proceso_limpieza.id,
            responsable_id=responsable_id,
            hora_inicio=body.hora_inicio,
            hora_final=body.hora_final,
            total_kg_ingreso=proceso_limpieza.total_kg_salida,
            total_kg_salida=body.total_kg_salida,
            numero_procesos=body.numero_procesos,
            es_organico=lote.es_organico,
            observaciones=body.observaciones,
            firma_responsable_planilla=body.firma_responsable_planilla,
            vobo_planta=body.vobo_planta,
            vobo_control_calidad=body.vobo_control_calidad,
        )
        self.db.add(proceso)
        self.db.flush()

        for sp_data, diferencia_temp in subprocesos_data:
            subproceso = SubprocesoAblandamiento(
                proceso_id=proceso.id,
                numero_proceso=sp_data.numero_proceso,
                tipo_recipiente_ablandamiento=sp_data.tipo_recipiente_ablandamiento,
                litros_agua_ablandamiento=sp_data.litros_agua_ablandamiento,
                tipo_recipiente_enfriado=sp_data.tipo_recipiente_enfriado,
                litros_agua_enfriado_t1000=sp_data.litros_agua_enfriado_t1000,
                litros_agua_enfriado_canastas=sp_data.litros_agua_enfriado_canastas,
                hora_inicio=sp_data.hora_inicio,
                hora_final=sp_data.hora_final,
                temp_inicio=sp_data.temp_inicio,
                temp_intermedia=sp_data.temp_intermedia,
                temp_final=sp_data.temp_final,
                diferencia_temp=diferencia_temp,
            )
            self.db.add(subproceso)

        lote.estado = "en_ablandamiento"
        self.db.commit()
        self.db.refresh(proceso)
        return proceso


class ProcesoElaboracionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_lote(self, lote_id: int) -> Optional[ProcesoElaboracionPulpa]:
        return (
            self.db.query(ProcesoElaboracionPulpa)
            .filter(ProcesoElaboracionPulpa.lote_materia_prima_id == lote_id)
            .first()
        )

    def create(
        self,
        lote: LoteMateriaPrima,
        proceso_ablandamiento: ProcesoAblandamiento,
        body: ProcesoElaboracionCreate,
        responsable_id,
        lotes_terminado_data: list,
    ) -> ProcesoElaboracionPulpa:
        proceso = ProcesoElaboracionPulpa(
            lote_materia_prima_id=lote.id,
            proceso_ablandamiento_id=proceso_ablandamiento.id,
            responsable_id=responsable_id,
            es_organico=lote.es_organico,
            observaciones=body.observaciones,
            firma_responsable_planilla=body.firma_responsable_planilla,
            vobo_planta=body.vobo_planta,
            vobo_control_calidad=body.vobo_control_calidad,
        )
        self.db.add(proceso)
        self.db.flush()

        for lpt_data, numero_lote, rendimiento_pct in lotes_terminado_data:
            lpt = LoteProductoTerminado(
                numero_lote=numero_lote,
                proceso_elaboracion_id=proceso.id,
                lote_materia_prima_id=lote.id,
                fecha_proceso=lpt_data.fecha_proceso,
                hora_inicio=lpt_data.hora_inicio,
                hora_final=lpt_data.hora_final,
                tipo_pulpa=lpt_data.tipo_pulpa,
                unidad_envase=lpt_data.unidad_envase,
                total_kg_fruto=lpt_data.total_kg_fruto,
                total_kg_pulpa=lpt_data.total_kg_pulpa,
                rendimiento_pct=rendimiento_pct,
                porcentaje_solidos=lpt_data.porcentaje_solidos,
                grados_brix=lpt_data.grados_brix,
                ph=lpt_data.ph,
                es_organico=lote.es_organico,
                total_kg=lpt_data.total_kg_pulpa,
                stock_actual_kg=lpt_data.total_kg_pulpa,
                estado="en_proceso",
            )
            self.db.add(lpt)

        lote.estado = "completado"
        self.db.commit()
        self.db.refresh(proceso)
        return proceso
