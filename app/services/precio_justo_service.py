# app/services/precio_justo_service.py
"""
Servicio para calcular el Precio Justo según las fórmulas del documento formula_aplicar.md
"""
import logging
from decimal import Decimal
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Reporte, Usuario

logger = logging.getLogger(__name__)

class PrecioJustoService:
    """
    Servicio para calcular el Precio Justo para Castaña y Asaí
    basado en las fórmulas oficiales del sistema
    """

    # Parámetros del sistema (configurables)
    # CASTAÑA
    PARAM_BONO_ORGANICO_C_BS = Decimal("0.40")  # Bs por certificación orgánica castaña
    PARAM_BONO_COMERCIO_JUSTO_C_BS = Decimal("0.36")  # Bs por certificación comercio justo castaña
    PARAM_UMBRAL_DIAS_C = 30  # Días umbral para deterioro castaña
    PARAM_PENALIDAD_DIA_C_BS = Decimal("0.5")  # Bs penalidad por día sobre umbral

    # ASAÍ
    PARAM_BONO_ORGANICO_A_BS = Decimal("5.0")  # Bs por certificación orgánica asaí
    PARAM_BONO_COMERCIO_JUSTO_A_BS = Decimal("0.36")  # Bs por certificación comercio justo asaí
    PARAM_BONO_ASAI_FR94_BS = Decimal("10.0")  # Bono frescura < 24h (FR 94)
    PARAM_BONO_ASAI_FR90_BS = Decimal("7.0")   # Bono frescura 24-48h (FR 90)
    PARAM_BONO_ASAI_FR85_BS = Decimal("3.0")   # Bono frescura 48-72h (FR 85)

    VAR_CALIDAD_TIPO_ORGANICO = "Organico"
    VAR_CALIDAD_TIPO_CONVENCIONAL = "Convencional"
    VAR_CALIDAD_TIPO_COMERCIO_JUSTO = "Comercio Justo"
    VAR_CALIDAD_TIPO_ORGANICO_COMERCIO_JUSTO = "Organico y Comercio Justo"

    UNIDAD_CATANIA_CAJA = "caja (aproximadamente 23 kg.)"
    UNIDAD_CATANIA_BARRICA = "barrica (aproximadamente 69 kg.)"
    UNIDAD_CATANIA_KG = "kg"

    UNIDAD_ASAI_LATA = "lata (aproximadamente 14.5 a 15 kg.)"

    VALOR_UNIDAD_CATANIA_CAJA = Decimal("23")  # kg por caja 
    VALOR_UNIDAD_CATANIA_BARRICA = Decimal("69")  # kg por barrica
    VALOR_UNIDAD_CATANIA_KG = Decimal("1")  # kg por kg

    VALOR_UNIDAD_ASAI_LATA = Decimal("14.5")  # lata

    TIPO_CAMBIO_USD_BS = Decimal("6.69")
    UNIDAD_BONO_ORGANICO = Decimal("2.2")

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # VARIABLES MAESTRAS DEL SISTEMA
    # =========================================================================

    def calcular_p_prom_planta_castana(self) -> Decimal:
        """
        Calcula P_Prom_Planta_C: Precio Promedio Ponderado de Castaña en Planta
        Usa reportes P9 (precio_intermediario_castana) donde nodo_precio == "En planta procesadora"
        """
        resultado = self.db.query(
            func.avg(Reporte.precio_intermediario_castana)
        ).scalar()

        """resultado = self.db.query(
            func.avg(Reporte.precio_intermediario_castana)
        ).filter(
            Reporte.precio_intermediario_castana.isnot(None),
            Reporte.nodo_precio == "En planta procesadora"
        ).scalar()"""

        return Decimal(str(resultado)) if resultado else Decimal("0")

    def calcular_p_prom_planta_asai(self) -> Decimal:
        """
        Calcula P_Prom_Planta_A: Precio Promedio Ponderado de Asaí en Planta
        Usa reportes P11 (precio_intermediario_asai) donde nodo_precio == "En planta procesadora"
        """
        resultado = self.db.query(
            func.avg(Reporte.precio_intermediario_asai)
        ).scalar()

        """
        resultado = self.db.query(
                    func.avg(Reporte.precio_intermediario_asai)
                ).filter(
                    Reporte.precio_intermediario_asai.isnot(None),
                    Reporte.nodo_precio == "En planta procesadora"
                ).scalar()
        """

        return Decimal(str(resultado)) if resultado else Decimal("0")

    def calcular_p_min_obs_castana_zona(self, zona: str) -> Decimal:
        """
        Calcula P_Min_Obs_C_Zona: Precio Mínimo Observado de Castaña en la zona del usuario
        Busca en reportes de la misma comunidad (usando el nombre de la comunidad como zona)
        """
        from app.models import Comunidad

        # Buscar el mínimo precio reportado (recolector o intermediario) en la zona/comunidad
        min_recolector = self.db.query(
            func.min(Reporte.precio_recolector_castana)
        ).join(
            Comunidad, Reporte.id_comunidad == Comunidad.id_comunidad
        ).filter(
            Comunidad.nombre == zona,
            Reporte.precio_recolector_castana.isnot(None)
        ).scalar()

        min_intermediario = self.db.query(
            func.min(Reporte.precio_intermediario_castana)
        ).join(
            Comunidad, Reporte.id_comunidad == Comunidad.id_comunidad
        ).filter(
            Comunidad.nombre == zona,
            Reporte.precio_intermediario_castana.isnot(None)
        ).scalar()

        # Retornar el menor de los dos (si existen)
        valores = [Decimal(str(v)) for v in [min_recolector, min_intermediario] if v is not None]
        return min(valores) if valores else Decimal("0")

    def calcular_p_min_obs_asai_zona(self, zona: str) -> Decimal:
        """
        Calcula P_Min_Obs_A_Zona: Precio Mínimo Observado de Asaí en la zona del usuario
        Busca en reportes de la misma comunidad (usando el nombre de la comunidad como zona)
        """
        from app.models import Comunidad

        min_cosechador = self.db.query(
            func.min(Reporte.precio_cosechador_asai)
        ).join(
            Comunidad, Reporte.id_comunidad == Comunidad.id_comunidad
        ).filter(
            Comunidad.nombre == zona,
            Reporte.precio_cosechador_asai.isnot(None)
        ).scalar()

        min_intermediario = self.db.query(
            func.min(Reporte.precio_intermediario_asai)
        ).join(
            Comunidad, Reporte.id_comunidad == Comunidad.id_comunidad
        ).filter(
            Comunidad.nombre == zona,
            Reporte.precio_intermediario_asai.isnot(None)
        ).scalar()

        valores = [Decimal(str(v)) for v in [min_cosechador, min_intermediario] if v is not None]
        return min(valores) if valores else Decimal("0")

    # =========================================================================
    # FÓRMULA PRECIO JUSTO CASTAÑA
    # =========================================================================

    def calcular_precio_justo_castana(
        self,
        costo_transporte: Optional[Decimal],
        tipo_castana: Optional[str],
        tiempo_recoleccion: Optional[int],
        tiempo_venta: Optional[int],
        unidad: Optional[str],
        zona: str
    ) -> Dict[str, Decimal]:
        """
        Calcula el Precio Justo para Castaña según la fórmula:
        PJ_Castaña = P_Base_Ajustado_C + Bono_Certificacion_C + Ajuste_Deterioro_C

        Returns:
            Dict con 'precio_justo' y 'precio_minimo_zona'
        """
        logger.debug("Iniciando cálculo de precio justo de castaña")
        logger.debug(f"Inputs recibidos: costo_transporte={costo_transporte}, "
                 f"tipo_castana='{tipo_castana}', tiempo_recoleccion={tiempo_recoleccion}, "
                 f"tiempo_venta={tiempo_venta}, zona='{zona}'")

        # 1. P_Base_Ajustado_C = P_Prom_Planta_C - Costo_Transporte
        p_prom_planta_c = self.calcular_p_prom_planta_castana()
        logger.debug(f"Precio promedio planta (p_prom_planta_c): {p_prom_planta_c}")

        costo_transporte_c = costo_transporte or Decimal("0")
        p_base_ajustado_c = p_prom_planta_c - costo_transporte_c

        # 2. Bono_Certificacion_C
        bono_certificacion_c = Decimal("0")
        if tipo_castana and self.VAR_CALIDAD_TIPO_ORGANICO.lower() in tipo_castana.lower():
            match unidad:
                case self.UNIDAD_CATANIA_CAJA:
                    bono_certificacion_c = self.VALOR_UNIDAD_CATANIA_CAJA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case self.UNIDAD_CATANIA_BARRICA:
                    bono_certificacion_c = self.VALOR_UNIDAD_CATANIA_BARRICA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case self.UNIDAD_CATANIA_KG:
                    bono_certificacion_c = self.VALOR_UNIDAD_CATANIA_KG * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case _:
                    bono_certificacion_c = Decimal("0")

        if tipo_castana and self.VAR_CALIDAD_TIPO_COMERCIO_JUSTO.lower() in tipo_castana.lower():
            match unidad:
                case self.UNIDAD_CATANIA_CAJA:
                    bono_certificacion_c = self.VALOR_UNIDAD_CATANIA_CAJA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case self.UNIDAD_CATANIA_BARRICA:
                    bono_certificacion_c = self.VALOR_UNIDAD_CATANIA_BARRICA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case self.UNIDAD_CATANIA_KG:
                    bono_certificacion_c = self.VALOR_UNIDAD_CATANIA_KG * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case _:
                    bono_certificacion_c = Decimal("0")

        if tipo_castana and self.VAR_CALIDAD_TIPO_ORGANICO_COMERCIO_JUSTO.lower() in tipo_castana.lower():
            match unidad:
                case self.UNIDAD_CATANIA_CAJA:
                    bono_organico = self.VALOR_UNIDAD_CATANIA_CAJA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_comercio_justo = self.VALOR_UNIDAD_CATANIA_CAJA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_certificacion_c = bono_organico + bono_comercio_justo
                case self.UNIDAD_CATANIA_BARRICA:
                    bono_organico = self.VALOR_UNIDAD_CATANIA_BARRICA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_comercio_justo = self.VALOR_UNIDAD_CATANIA_BARRICA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_certificacion_c = bono_organico + bono_comercio_justo
                case self.UNIDAD_CATANIA_KG:
                    bono_organico = self.VALOR_UNIDAD_CATANIA_KG * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_comercio_justo = self.VALOR_UNIDAD_CATANIA_KG * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_C_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_certificacion_c = bono_organico + bono_comercio_justo
                case _:
                    bono_certificacion_c = Decimal("0")

        # 3. Ajuste_Deterioro_C
        ajuste_deterioro_c = Decimal("0")
        if tiempo_recoleccion is not None and tiempo_venta is not None:
            tiempo_total_c = tiempo_recoleccion + tiempo_venta
            if tiempo_total_c > self.PARAM_UMBRAL_DIAS_C:
                dias_sobre_umbral = tiempo_total_c - self.PARAM_UMBRAL_DIAS_C
                ajuste_deterioro_c = -1 * (Decimal(str(dias_sobre_umbral)) * self.PARAM_PENALIDAD_DIA_C_BS)

        # Cálculo final
        pj_castana = p_base_ajustado_c + bono_certificacion_c + ajuste_deterioro_c

        # Precio mínimo observado en la zona
        #p_min_obs_c_zona = self.calcular_p_min_obs_castana_zona(zona)

        return {
            "precio_justo": max(pj_castana, Decimal("0")),  # No puede ser negativo
            #"precio_minimo_zona": p_min_obs_c_zona,
            "detalles": {
                "p_base_ajustado": p_base_ajustado_c,
                "bono_certificacion": bono_certificacion_c,
                "ajuste_deterioro": ajuste_deterioro_c,
                "p_prom_planta": p_prom_planta_c,
                "costo_transporte": costo_transporte_c
            }
        }

    # =========================================================================
    # FÓRMULA PRECIO JUSTO ASAÍ
    # =========================================================================

    def calcular_precio_justo_asai(
        self,
        costo_transporte: Optional[Decimal],
        tipo_asai: Optional[str],
        horas_desde_cosecha: Optional[int],
        zona: str,
        unidad: Optional[str]
    ) -> Dict[str, Decimal]:
        """
        Calcula el Precio Justo para Asaí según la fórmula:
        PJ_Asai = P_Base_Ajustado_A + Bono_Frescura_A + Bono_Certificacion_A

        Returns:
            Dict con 'precio_justo' y 'precio_minimo_zona'
        """
        # 1. P_Base_Ajustado_A = P_Prom_Planta_A - Costo_Transporte
        p_prom_planta_a = self.calcular_p_prom_planta_asai()
        costo_transporte_a = costo_transporte or Decimal("0")
        p_base_ajustado_a = p_prom_planta_a - costo_transporte_a

        # 2. Bono_Frescura_A (según horas desde cosecha)
        bono_frescura_a = Decimal("0")
        if horas_desde_cosecha is not None:
            if horas_desde_cosecha < 24:
                bono_frescura_a = self.PARAM_BONO_ASAI_FR94_BS
            elif horas_desde_cosecha < 48:
                bono_frescura_a = self.PARAM_BONO_ASAI_FR90_BS
            elif horas_desde_cosecha < 72:
                bono_frescura_a = self.PARAM_BONO_ASAI_FR85_BS

        # 3. Bono_Certificacion_A
        bono_certificacion_a = Decimal("0")
        if tipo_asai and self.VAR_CALIDAD_TIPO_ORGANICO.lower() in tipo_asai.lower():
            match unidad:
                case self.UNIDAD_ASAI_LATA:
                    bono_certificacion_a = self.VALOR_UNIDAD_ASAI_LATA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_A_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case _:
                    bono_certificacion_a = Decimal("0")

        if tipo_asai and self.VAR_CALIDAD_TIPO_COMERCIO_JUSTO.lower() in tipo_asai.lower():
            match unidad:
                case self.UNIDAD_ASAI_LATA:
                    bono_certificacion_a = self.VALOR_UNIDAD_ASAI_LATA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_A_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                case _:
                    bono_certificacion_a = Decimal("0")

        if tipo_asai and self.VAR_CALIDAD_TIPO_ORGANICO_COMERCIO_JUSTO.lower() in tipo_asai.lower():
            match unidad:
                case self.UNIDAD_ASAI_LATA:
                    bono_organico = self.VALOR_UNIDAD_ASAI_LATA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_ORGANICO_A_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_comercio_justo = self.VALOR_UNIDAD_ASAI_LATA * (((self.TIPO_CAMBIO_USD_BS * self.PARAM_BONO_COMERCIO_JUSTO_A_BS)*1)/self.UNIDAD_BONO_ORGANICO)
                    bono_certificacion_a = bono_organico + bono_comercio_justo
                case _:
                    bono_certificacion_a = Decimal("0")


        # Cálculo final
        pj_asai = p_base_ajustado_a + bono_frescura_a + bono_certificacion_a

        # Precio mínimo observado en la zona
        #p_min_obs_a_zona = self.calcular_p_min_obs_asai_zona(zona)

        return {
            "precio_justo": max(pj_asai, Decimal("0")),  # No puede ser negativo
            "detalles": {
                "p_base_ajustado": p_base_ajustado_a,
                "bono_frescura": bono_frescura_a,
                "bono_certificacion": bono_certificacion_a,
                "p_prom_planta": p_prom_planta_a,
                "costo_transporte": costo_transporte_a
            }
        }
