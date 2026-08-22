import uuid

from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# =============================================================================
# SCHEMAS PARA USUARIO (Sección 0: Identificación)
# =============================================================================

class UsuarioBase(BaseModel):
    nombre: str = Field(..., description="P1: Nombre del usuario")
    rubro: str = Field(..., description="P2: Castaña, Asaí, Ambos productos")
    actividades: List[str] = Field(..., description="P3: Array de actividades")
    genero: str = Field(..., description="P4: Masculino, Femenino, Otro, Prefiero no decir")
    edad: str = Field(..., description="P5: Rango de edad")
    gps_lat: Optional[Decimal] = Field(None, description="P7: Latitud GPS (opcional)")
    gps_lon: Optional[Decimal] = Field(None, description="P7: Longitud GPS (opcional)")


class UsuarioCreate(UsuarioBase):
    device_id: str = Field(..., description="Device unique identifier")


class UsuarioOut(UsuarioBase):
    id_usuario: int
    device_id: str
    fecha_registro: datetime
    activo: bool

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS PARA REPORTE (Secciones 1-5)
# =============================================================================

class ReporteBase(BaseModel):
    id_comunidad: Optional[int] = Field(None, description="ID de comunidad (dropdown searchable)")

    # Sección 1: Precios — Castaña
    precio_recolector_castana: Optional[Decimal] = Field(None)
    unidad_recolector_castana: Optional[str] = Field(None)
    precio_intermediario_castana: Optional[Decimal] = Field(None)
    unidad_intermediario_castana: Optional[str] = Field(None)
    costo_transporte_castana: Optional[Decimal] = Field(None)
    unidad_transporte_castana: Optional[str] = Field(None)
    tipo_transporte_castana: Optional[str] = Field(None)

    # Sección 1: Precios — Asaí
    precio_cosechador_asai: Optional[Decimal] = Field(None)
    unidad_cosechador_asai: Optional[str] = Field(None)
    precio_intermediario_asai: Optional[Decimal] = Field(None)
    unidad_intermediario_asai: Optional[str] = Field(None)
    costo_transporte_asai: Optional[Decimal] = Field(None)
    unidad_transporte_asai: Optional[str] = Field(None)
    tipo_transporte_asai: Optional[str] = Field(None)

    nodo_precio: Optional[str] = Field(None)
    nodo_precio_otro: Optional[str] = Field(None)

    # Sección 2: Calidad — Castaña
    tipo_castana: Optional[str] = Field(None)
    tiempo_recoleccion_castana: Optional[int] = Field(None)
    tiempo_venta_castana: Optional[int] = Field(None)

    # Sección 2: Calidad — Asaí
    tipo_asai: Optional[str] = Field(None)
    tiempo_cosecha_asai: Optional[int] = Field(None)

    # Sección 3: Transporte
    tipo_transporte_usado: Optional[str] = Field(None)
    tipo_transporte_usado_otro: Optional[str] = Field(None)

    # Sección 4: Mercados Grandes — Castaña
    no_sabe_fob_castana: Optional[bool] = Field(False)
    moneda_fob_castana: Optional[str] = Field(None)
    precio_fob_castana: Optional[Decimal] = Field(None)
    unidad_fob_castana: Optional[str] = Field(None)
    fuente_precio_castana: Optional[str] = Field(None)
    fuente_precio_castana_otro: Optional[str] = Field(None)

    # Sección 4: Mercados Grandes — Asaí
    no_sabe_mercado_asai: Optional[bool] = Field(False)
    precio_mercado_grande_asai: Optional[Decimal] = Field(None)
    unidad_mercado_grande_asai: Optional[str] = Field(None)
    mercado_asai: Optional[str] = Field(None)
    mercado_asai_otro: Optional[str] = Field(None)
    fuente_precio_asai: Optional[str] = Field(None)
    fuente_precio_asai_otro: Optional[str] = Field(None)

    # Sección 5: Feedback
    comentarios_adicionales: Optional[str] = Field(None)

    # Metadata
    latitud: Optional[Decimal] = Field(None)
    longitud: Optional[Decimal] = Field(None)


class ReporteCreate(ReporteBase):
    id_usuario: int = Field(..., description="ID del usuario que envía el reporte")


class ReporteOut(ReporteBase):
    id_reporte: int
    id_usuario: int
    fecha_registro: datetime

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMA COMPLETO DEL FORMULARIO
# =============================================================================

class FormularioCompletoRequest(BaseModel):
    model_config = {"populate_by_name": True}

    # Sección 0: Identificación
    device_id: str = Field(...)
    nombre: Optional[str] = Field(None)
    rubro: Optional[str] = Field(None)
    actividades: Optional[List[str]] = Field(None)
    genero: Optional[str] = Field(None)
    edad: Optional[str] = Field(None)
    comunidad_id: Optional[int] = Field(None)
    gps_lat: Optional[Decimal] = Field(None)
    gps_lon: Optional[Decimal] = Field(None)

    # Sección 1: Precios — Castaña
    precio_recolector_castana: Optional[Decimal] = Field(None, alias="precio_recolector_castania")
    unidad_recolector_castana: Optional[str] = Field(None, alias="unidad_recolector_castania")
    precio_intermediario_castana: Optional[Decimal] = Field(None, alias="precio_intermediario_castania")
    unidad_intermediario_castana: Optional[str] = Field(None, alias="unidad_intermediario_castania")

    # Sección 1: Precios — Asaí
    precio_cosechador_asai: Optional[Decimal] = Field(None)
    unidad_cosechador_asai: Optional[str] = Field(None)
    precio_intermediario_asai: Optional[Decimal] = Field(None)
    unidad_intermediario_asai: Optional[str] = Field(None)

    # Sección 1: Costos de transporte
    costo_transporte_castana: Optional[Decimal] = Field(None, alias="costo_transporte_castania")
    unidad_transporte_castana: Optional[str] = Field(None, alias="unidad_transporte_castania")
    tipo_transporte_castana: Optional[str] = Field(None, alias="tipo_transporte_castania")
    costo_transporte_asai: Optional[Decimal] = Field(None)
    unidad_transporte_asai: Optional[str] = Field(None)
    tipo_transporte_asai: Optional[str] = Field(None)

    nodo_precio: Optional[str] = Field(None)
    nodo_precio_otro: Optional[str] = Field(None)

    # Sección 2: Calidad — Castaña
    tipo_castana: Optional[str] = Field(None, alias="tipo_castania")
    tiempo_recoleccion_castana: Optional[int] = Field(None, alias="tiempo_recoleccion_castania")
    tiempo_venta_castana: Optional[int] = Field(None, alias="tiempo_venta_castania")

    # Sección 2: Calidad — Asaí
    tipo_asai: Optional[str] = Field(None)
    tiempo_cosecha_asai: Optional[int] = Field(None)

    # Sección 3: Transporte
    tipo_transporte_usado: Optional[str] = Field(None)
    tipo_transporte_usado_otro: Optional[str] = Field(None)

    # Sección 4: Mercados — Castaña
    precio_fob_castana: Optional[Decimal] = Field(None, alias="precio_fob_castania")
    moneda_fob_castana: Optional[str] = Field(None, alias="moneda_fob_castania")
    unidad_fob_castana: Optional[str] = Field(None, alias="unidad_fob_castania")
    no_sabe_fob_castana: Optional[bool] = Field(False, alias="no_sabe_fob_castania")

    # Sección 4: Mercados — Asaí
    precio_mercado_grande_asai: Optional[Decimal] = Field(None)
    unidad_mercado_grande_asai: Optional[str] = Field(None)
    mercado_asai: Optional[str] = Field(None)
    mercado_asai_otro: Optional[str] = Field(None)
    no_sabe_mercado_asai: Optional[bool] = Field(False)

    # Sección 4: Fuentes
    fuente_precio_castana: Optional[str] = Field(None, alias="fuente_precio_castania")
    fuente_precio_castana_otro: Optional[str] = Field(None, alias="fuente_precio_castania_otro")
    fuente_precio_asai: Optional[str] = Field(None)
    fuente_precio_asai_otro: Optional[str] = Field(None)

    # Sección 5: Feedback
    comentarios_adicionales: Optional[str] = Field(None)

    # Metadata
    latitud: Optional[Decimal] = Field(None)
    longitud: Optional[Decimal] = Field(None)
    fecha_registro: Optional[datetime] = Field(default_factory=datetime.utcnow)


# =============================================================================
# SCHEMAS PARA CÁLCULO DE PRECIO JUSTO
# =============================================================================

class PrecioJustoRequest(BaseModel):
    comunidad: str = Field(...)
    costo_transporte_castana: Optional[Decimal] = Field(None)
    tipo_castana: Optional[str] = Field(None)
    tiempo_recoleccion_castana: Optional[int] = Field(None)
    tiempo_venta_castana: Optional[int] = Field(None)
    costo_transporte_asai: Optional[Decimal] = Field(None)
    tipo_asai: Optional[str] = Field(None)
    tiempo_cosecha_asai: Optional[int] = Field(None)


class PrecioJustoDetalles(BaseModel):
    p_base_ajustado: Decimal
    bono_certificacion: Optional[Decimal] = None
    bono_frescura: Optional[Decimal] = None
    ajuste_deterioro: Optional[Decimal] = None
    p_prom_planta: Decimal
    costo_transporte: Decimal


class PrecioJustoResultadoCastana(BaseModel):
    precio_justo: Decimal
    precio_minimo_zona: Optional[Decimal] = None
    mensaje: str
    detalles: PrecioJustoDetalles


class PrecioJustoResultadoAsai(BaseModel):
    precio_justo: Decimal
    precio_minimo_zona: Optional[Decimal] = None
    mensaje: str
    detalles: PrecioJustoDetalles


class PrecioJustoResponse(BaseModel):
    castana: Optional[PrecioJustoResultadoCastana] = None
    asai: Optional[PrecioJustoResultadoAsai] = None
    fecha_calculo: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# SCHEMAS PARA COMUNIDADES
# =============================================================================

class ComunidadBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=500)
    abreviacion: str = Field(..., min_length=1, max_length=50)


class ComunidadCreate(ComunidadBase):
    pass


class ComunidadUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=500)
    abreviacion: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None)


class ComunidadOut(ComunidadBase):
    id_comunidad: int
    status: str

    class Config:
        from_attributes = True


class ComunidadListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    comunidades: List[ComunidadOut]


class ResponsableComunidadOut(BaseModel):
    usuario_id: uuid.UUID = Field(alias="id")
    nombre_completo: str
    username: str

    model_config = {"from_attributes": True, "populate_by_name": True}


class AsignarResponsablesBody(BaseModel):
    usuario_ids: List[uuid.UUID] = Field(..., min_length=1, description="UUIDs de usuarios con rol responsable_acopio")


class ComunidadListBody(BaseModel):
    comunidad_ids: List[int] = Field(..., min_length=1, description="IDs de comunidades a asignar")


# =============================================================================
# SCHEMAS PARA ROLES
# =============================================================================

class RolOut(BaseModel):
    id: int
    nombre: str
    descripcion: str
    metodo_auth: str

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS — MÓDULO 1: RECOLECTORES (Área A)
# =============================================================================

from datetime import date, time


class RecolectorCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=20, description="Código del recolector, ej: VF-GGS")
    nombre_completo: str = Field(..., min_length=1, max_length=200)
    ci: str = Field(..., min_length=1, max_length=20)
    comunidad_id: int
    fecha_registro: date
    credencial: Optional[str] = Field(None, min_length=6, max_length=6, pattern=r"^\d{6}$", description="PIN inicial de 6 dígitos. Si se omite, el backend genera uno automáticamente.")
    documento_tenencia: Optional[str] = Field(None, description="ej: PGIBT N° 123-2024")
    codigo_tc: Optional[str] = Field(None, description="N° TC del productor, ej: BO-BIO-6088")
    especie: Optional[str] = None


class RecolectorUpdate(BaseModel):
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=200)
    ci: Optional[str] = Field(None, min_length=1, max_length=20)
    documento_tenencia: Optional[str] = None
    codigo_tc: Optional[str] = None
    especie: Optional[str] = None
    estado: Optional[str] = Field(None, description="activo | inactivo")


class RecolectorOut(BaseModel):
    id: int
    codigo: str
    nombre_completo: str
    ci: str
    comunidad_id: int
    comunidad_nombre: Optional[str] = None
    documento_tenencia: Optional[str]
    codigo_tc: Optional[str]
    especie: Optional[str]
    fecha_registro: date
    estado: str
    usuario_id: uuid.UUID

    @model_validator(mode="before")
    @classmethod
    def _extract_comunidad_nombre(cls, data):
        if hasattr(data, "comunidad") and data.comunidad is not None:
            data.__dict__["comunidad_nombre"] = data.comunidad.nombre
        return data

    class Config:
        from_attributes = True


class RecolectorCreateResponse(RecolectorOut):
    pin_generado: Optional[str] = Field(
        None,
        description="PIN generado automáticamente. Solo visible en esta respuesta, nunca recuperable."
    )


class RecolectorListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    recolectores: List[RecolectorOut]


class EntregaRecolectorCreate(BaseModel):
    peso_kg: Decimal = Field(..., gt=0)
    parcela_id: Optional[int] = None
    fecha_recoleccion: Optional[date] = None
    fecha_entrega: Optional[date] = None
    tipo_envase: Optional[str] = Field(None, description="Saco, Tina, etc.")
    hora_cosecha: Optional[time] = None
    hora_recepcion: Optional[time] = None
    medio_transporte: Optional[str] = Field(None, description="fluvial | terrestre")
    firma_recolector: bool = False
    observaciones: Optional[str] = None


class EntregaRecolectorOut(BaseModel):
    id: int
    numero_entrega: Optional[str]
    recolector_id: int
    parcela_id: Optional[int]
    peso_kg: Decimal
    fecha_recoleccion: Optional[date]
    fecha_entrega: Optional[date]
    tipo_envase: Optional[str]
    hora_cosecha: Optional[time]
    hora_recepcion: Optional[time]
    medio_transporte: Optional[str]
    estado_recepcion: Optional[str]
    firma_recolector: bool
    firma_responsable_acopio: bool
    observaciones: Optional[str]

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS — MÓDULO 1: PARCELAS
# =============================================================================

class ParcelaCreate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    poligono_gps: Optional[dict] = Field(None, description="GeoJSON Polygon dibujado en app móvil")
    superficie_ha: Optional[Decimal] = Field(None, description="Ingresada manualmente si no hay polígono")
    especie: Optional[str] = Field(None, max_length=100)
    produccion_estimada_kg: Optional[Decimal] = Field(None, gt=0)


class ParcelaUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    poligono_gps: Optional[dict] = None
    superficie_ha: Optional[Decimal] = None
    especie: Optional[str] = Field(None, max_length=100)
    produccion_estimada_kg: Optional[Decimal] = Field(None, gt=0)
    estado: Optional[str] = Field(None, description="activa | inactiva")


class ParcelaOut(BaseModel):
    id: int
    recolector_id: int
    codigo: Optional[str]
    poligono_gps: Optional[dict]
    superficie_ha: Optional[Decimal]
    especie: Optional[str]
    produccion_estimada_kg: Optional[Decimal]
    estado: str

    class Config:
        from_attributes = True


class ParcelaListResponse(BaseModel):
    total: int
    parcelas: List[ParcelaOut]


class EntregaListResponse(BaseModel):
    total: int
    recolector_id: int
    entregas: List[EntregaRecolectorOut]


# =============================================================================
# SCHEMAS — MÓDULO 1: HABILITACIÓN VIGENTE (recolector/me)
# =============================================================================

class AutorizacionZafraResumen(BaseModel):
    id: int
    cosecha: int
    codigo_documento: Optional[str]
    zona_autorizacion: Optional[str]
    fecha_inicio_recoleccion: Optional[date]
    fecha_fin_recoleccion: Optional[date]

    class Config:
        from_attributes = True


class HabilitacionVigenteOut(BaseModel):
    id: int
    estado_recoleccion: Optional[str]
    autorizacion_zafra: AutorizacionZafraResumen

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS — MÓDULO 1: AUTORIZACIONES DE ZAFRA
# =============================================================================

class AutorizacionZafraCreate(BaseModel):
    comunidad_id: int
    cosecha: int = Field(..., ge=2000, le=2100, description="Año de cosecha, ej: 2026")
    codigo_documento: Optional[str] = Field(None, max_length=100)
    solicitante: str = Field(..., min_length=1, max_length=200)
    ci_solicitante: Optional[str] = Field(None, max_length=20)
    expediente: Optional[str] = Field(None, max_length=100)
    fecha_inicio_recoleccion: Optional[date] = None
    fecha_fin_recoleccion: Optional[date] = None
    n_dias_recoleccion: Optional[int] = None
    superficie_km2: Optional[Decimal] = None
    zona_autorizacion: Optional[str] = Field(None, max_length=200)
    sello_sernap: bool = False
    recolector_ids: List[int] = Field(default_factory=list, description="IDs de recolectores a habilitar en esta autorización")


class AutorizacionRecolectorOut(BaseModel):
    id: int
    recolector_id: int
    especie: Optional[str]
    superficie_ha: Optional[Decimal]
    produccion_estimada_kg: Optional[Decimal]
    estado_recoleccion: Optional[str]

    class Config:
        from_attributes = True


class AutorizacionZafraOut(BaseModel):
    id: int
    comunidad_id: int
    cosecha: int
    codigo_documento: Optional[str]
    solicitante: str
    ci_solicitante: Optional[str]
    expediente: Optional[str]
    fecha_inicio_recoleccion: Optional[date]
    fecha_fin_recoleccion: Optional[date]
    n_dias_recoleccion: Optional[int]
    superficie_km2: Optional[Decimal]
    zona_autorizacion: Optional[str]
    sello_sernap: bool
    recolectores: List[AutorizacionRecolectorOut] = []

    class Config:
        from_attributes = True


class HabilitarRecolectoresBody(BaseModel):
    recolector_ids: List[int] = Field(..., min_length=1)


class RecolectorHabilitadoOut(BaseModel):
    """Recolector con datos de su entrega más reciente para la lista de zafra."""
    id: int
    codigo: str
    nombre_completo: str
    autorizacion_recolector_id: int
    ultima_entrega_id: Optional[int] = None
    fecha_recoleccion: Optional[date] = None
    fecha_entrega: Optional[date] = None
    tipo_envase: Optional[str] = None
    peso_kg: Optional[Decimal] = None
    hora_cosecha: Optional[str] = None
    hora_recepcion: Optional[str] = None
    medio_transporte: Optional[str] = None
    estado_recepcion: Optional[str] = None
    observaciones: Optional[str] = None
    badge: str = Field(description="sin_datos | pendiente | recibido | rechazado")

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS — MÓDULO 2: LOTES DE MATERIA PRIMA
# =============================================================================

class LoteMateriaPrimaCreate(BaseModel):
    comunidad_id: int
    es_organico: bool
    fruto: str = "asaí"


class LoteMateriaPrimaOut(BaseModel):
    id: int
    numero_lote: str
    comunidad_id: int
    responsable_id: uuid.UUID
    es_organico: bool
    fruto: str
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime]
    total_kg: Decimal
    total_bs: Decimal
    estado: str
    motivo_rechazo: Optional[str]
    rechazado_en: Optional[datetime]
    vobo_control: bool
    vobo_planta: bool
    total_recepciones: Optional[int] = None

    class Config:
        from_attributes = True


class LoteListResponse(BaseModel):
    total: int
    lotes: List[LoteMateriaPrimaOut]


class CerrarLoteBody(BaseModel):
    vobo_control: bool = True


class RechazarLoteBody(BaseModel):
    motivo_rechazo: str = Field(..., min_length=1)


# =============================================================================
# SCHEMAS — MÓDULO 2: ITEMS DE RECEPCIÓN
# =============================================================================

class ItemRecepcionCreate(BaseModel):
    recolector_id: int
    autorizacion_recolector_id: Optional[int] = None
    entrega_recolector_id: Optional[int] = Field(None, description="FK a EntregaRecolector si el recolector ya sincronizó")
    zona_autorizacion: Optional[str] = None
    tipo_asai: Optional[str] = Field(None, description="altura | bajio")
    numero_compra: Optional[int] = None
    peso_kg: Decimal = Field(..., gt=0)
    precio_bs_kg: Decimal = Field(..., gt=0)
    firma_entrega: bool = False
    firma_pago: bool = False
    # Datos del cosechador (pueden venir de EntregaRecolector o ingresarse manualmente)
    fecha_recoleccion: Optional[date] = None
    fecha_entrega: Optional[date] = None
    tipo_envase: Optional[str] = None
    hora_cosecha: Optional[time] = None
    hora_recepcion: Optional[time] = None
    medio_transporte: Optional[str] = None
    parcela_id: Optional[int] = None


class ItemRecepcionOut(BaseModel):
    id: int
    lote_materia_prima_id: int
    recolector_id: int
    entrega_recolector_id: Optional[int]
    autorizacion_recolector_id: Optional[int]
    zona_autorizacion: Optional[str]
    tipo_asai: Optional[str]
    numero_compra: Optional[int]
    peso_kg: Decimal
    precio_bs_kg: Decimal
    precio_total_bs: Decimal
    firma_entrega: bool
    firma_pago: bool

    class Config:
        from_attributes = True


class EntregaSinRecepcionOut(BaseModel):
    """EntregaRecolector pendiente de vincular a un ItemRecepcion."""
    id: int
    numero_entrega: Optional[str]
    recolector_id: int
    parcela_id: Optional[int]
    peso_kg: Decimal
    fecha_recoleccion: Optional[date]
    fecha_entrega: Optional[date]
    tipo_envase: Optional[str]
    hora_cosecha: Optional[time]
    hora_recepcion: Optional[time]
    medio_transporte: Optional[str]
    observaciones: Optional[str]

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS — MÓDULO OPERADOR DE PLANTA
# =============================================================================

# --- Limpieza ---
class SubprocesoLimpiezaCreate(BaseModel):
    numero_proceso: int
    hora_inicio_seco: Optional[time] = None
    hora_final_seco: Optional[time] = None
    residuos_kg: Optional[Decimal] = None
    tipo_recipiente_inmersion: Optional[str] = None
    hora_inicio_lavado: Optional[time] = None
    hora_final_lavado: Optional[time] = None

class SubprocesoLimpiezaOut(SubprocesoLimpiezaCreate):
    id: int
    class Config:
        from_attributes = True

class ProcesoLimpiezaCreate(BaseModel):
    lote_materia_prima_id: int
    hora_inicio: Optional[time] = None
    hora_final: Optional[time] = None
    total_kg_salida: Optional[Decimal] = Field(None, gt=0)
    numero_procesos: Optional[int] = None
    observaciones: Optional[str] = None
    firma_responsable_planilla: bool = False
    vobo_planta: bool = False
    vobo_control_calidad: bool = False
    subprocesos: List[SubprocesoLimpiezaCreate] = Field(default_factory=list)

class ProcesoLimpiezaOut(BaseModel):
    id: int
    lote_materia_prima_id: int
    responsable_id: uuid.UUID
    hora_inicio: Optional[time]
    hora_final: Optional[time]
    total_kg_ingreso: Optional[Decimal]
    total_kg_salida: Optional[Decimal]
    numero_procesos: Optional[int]
    es_organico: bool
    observaciones: Optional[str]
    firma_responsable_planilla: bool
    vobo_planta: bool
    vobo_control_calidad: bool
    subprocesos: List[SubprocesoLimpiezaOut] = []
    class Config:
        from_attributes = True

# --- Ablandamiento ---
class SubprocesoAblandamientoCreate(BaseModel):
    numero_proceso: int
    tipo_recipiente_ablandamiento: Optional[str] = None
    litros_agua_ablandamiento: Optional[Decimal] = None
    tipo_recipiente_enfriado: Optional[str] = None
    litros_agua_enfriado_t1000: Optional[Decimal] = None
    litros_agua_enfriado_canastas: Optional[Decimal] = None
    hora_inicio: Optional[time] = None
    hora_final: Optional[time] = None
    temp_inicio: Optional[Decimal] = None
    temp_intermedia: Optional[Decimal] = None
    temp_final: Optional[Decimal] = None
    # diferencia_temp calculated by backend: temp_inicio - temp_final

class SubprocesoAblandamientoOut(SubprocesoAblandamientoCreate):
    id: int
    diferencia_temp: Optional[Decimal] = None
    class Config:
        from_attributes = True

class ProcesoAblandamientoCreate(BaseModel):
    lote_materia_prima_id: int
    hora_inicio: Optional[time] = None
    hora_final: Optional[time] = None
    total_kg_salida: Optional[Decimal] = Field(None, gt=0)
    numero_procesos: Optional[int] = None
    observaciones: Optional[str] = None
    firma_responsable_planilla: bool = False
    vobo_planta: bool = False
    vobo_control_calidad: bool = False
    subprocesos: List[SubprocesoAblandamientoCreate] = Field(default_factory=list)

class ProcesoAblandamientoOut(BaseModel):
    id: int
    lote_materia_prima_id: int
    proceso_limpieza_id: int
    responsable_id: uuid.UUID
    hora_inicio: Optional[time]
    hora_final: Optional[time]
    total_kg_ingreso: Optional[Decimal]
    total_kg_salida: Optional[Decimal]
    numero_procesos: Optional[int]
    es_organico: bool
    observaciones: Optional[str]
    firma_responsable_planilla: bool
    vobo_planta: bool
    vobo_control_calidad: bool
    subprocesos: List[SubprocesoAblandamientoOut] = []
    class Config:
        from_attributes = True

# --- Elaboración de pulpa + LPT ---
class LoteProductoTerminadoCreate(BaseModel):
    tipo_pulpa: str = Field(..., description="premium | popular")
    unidad_envase: Optional[str] = None
    fecha_proceso: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_final: Optional[time] = None
    total_kg_fruto: Optional[Decimal] = Field(None, gt=0)
    total_kg_pulpa: Optional[Decimal] = Field(None, gt=0)
    porcentaje_solidos: Optional[Decimal] = None
    grados_brix: Optional[Decimal] = None
    ph: Optional[Decimal] = None
    # rendimiento_pct calculated by backend

class LoteProductoTerminadoOut(BaseModel):
    id: int
    numero_lote: str
    proceso_elaboracion_id: int
    lote_materia_prima_id: int
    fecha_proceso: Optional[date]
    hora_inicio: Optional[time]
    hora_final: Optional[time]
    tipo_pulpa: str
    unidad_envase: Optional[str]
    total_kg_fruto: Optional[Decimal]
    total_kg_pulpa: Optional[Decimal]
    rendimiento_pct: Optional[Decimal]
    porcentaje_solidos: Optional[Decimal]
    grados_brix: Optional[Decimal]
    ph: Optional[Decimal]
    es_organico: bool
    total_kg: Optional[Decimal]
    stock_actual_kg: Optional[Decimal]
    estado: str
    class Config:
        from_attributes = True

class ProcesoElaboracionCreate(BaseModel):
    lote_materia_prima_id: int
    observaciones: Optional[str] = None
    firma_responsable_planilla: bool = False
    vobo_planta: bool = False
    vobo_control_calidad: bool = False
    lotes_producto_terminado: List[LoteProductoTerminadoCreate] = Field(..., min_length=1)

class ProcesoElaboracionOut(BaseModel):
    id: int
    lote_materia_prima_id: int
    proceso_ablandamiento_id: int
    responsable_id: uuid.UUID
    es_organico: bool
    observaciones: Optional[str]
    firma_responsable_planilla: bool
    vobo_planta: bool
    vobo_control_calidad: bool
    lotes_producto_terminado: List[LoteProductoTerminadoOut] = []
    class Config:
        from_attributes = True

# --- Choque Térmico ---
class ItemChoqueTermicoCreate(BaseModel):
    lote_producto_terminado_id: int
    numero_freezer: Optional[int] = None
    tipo_pulpa: Optional[str] = None
    tipo_envase: Optional[str] = None
    unidad: Optional[str] = None
    cantidad: Optional[Decimal] = None
    fecha_ingreso: Optional[date] = None
    fecha_salida: Optional[date] = None

class ItemChoqueTermicoOut(ItemChoqueTermicoCreate):
    id: int
    sesion_id: int
    class Config:
        from_attributes = True

class SesionChoqueTermicoCreate(BaseModel):
    hora_inicio: Optional[time] = None
    hora_final: Optional[time] = None
    es_organico: bool
    observaciones: Optional[str] = None
    firma_responsable_planilla: bool = False
    vobo_planta: bool = False
    vobo_control_calidad: bool = False
    items: List[ItemChoqueTermicoCreate] = Field(..., min_length=1)

class SesionChoqueTermicoOut(BaseModel):
    id: int
    responsable_id: uuid.UUID
    hora_inicio: Optional[time]
    hora_final: Optional[time]
    es_organico: bool
    observaciones: Optional[str]
    firma_responsable_planilla: bool
    vobo_planta: bool
    vobo_control_calidad: bool
    items: List[ItemChoqueTermicoOut] = []
    class Config:
        from_attributes = True

# --- Cámara de frío ---
class InventarioCamaraFrioCreate(BaseModel):
    lote_producto_terminado_id: int
    tipo_pulpa: Optional[str] = None
    estado: Optional[str] = Field(None, description="bueno | observado")
    tipo_envase: Optional[str] = None
    unidad: Optional[str] = None
    cantidad: Optional[Decimal] = None
    fecha_ingreso: Optional[date] = None
    fecha_salida: Optional[date] = None
    observaciones: Optional[str] = None
    firma_responsable_planilla: bool = False
    vobo_planta: bool = False
    vobo_control_calidad: bool = False

class InventarioCamaraFrioOut(InventarioCamaraFrioCreate):
    id: int
    responsable_id: uuid.UUID
    class Config:
        from_attributes = True

# --- Matriz de procesos ---
class ItemMatrizCreate(BaseModel):
    proceso: str = Field(..., description="Nombre de la etapa del proceso")
    responsable_nombre: Optional[str] = None
    tareas_principales: Optional[str] = None
    herramientas_equipos: Optional[str] = None

class ItemMatrizOut(ItemMatrizCreate):
    id: int
    class Config:
        from_attributes = True

class MatrizProcesosCreate(BaseModel):
    lote_producto_terminado_id: int
    fecha: Optional[date] = None
    items: List[ItemMatrizCreate] = Field(default_factory=list)

class MatrizProcesosOut(BaseModel):
    id: int
    lote_producto_terminado_id: Optional[int]
    responsable_id: uuid.UUID
    fecha: Optional[date]
    items: List[ItemMatrizOut] = []
    class Config:
        from_attributes = True

# --- Despacho ---
class ItemDespachoCreate(BaseModel):
    lote_producto_terminado_id: int
    peso_kg: Decimal = Field(..., gt=0)
    numero_cajas: Optional[int] = None

class ItemDespachoOut(ItemDespachoCreate):
    id: int
    despacho_id: int
    numero_lote: Optional[str]
    subtotal_bs: Optional[Decimal]
    class Config:
        from_attributes = True

class FirmaBlock(BaseModel):
    nombre: Optional[str] = None
    ci: Optional[str] = None
    cargo: Optional[str] = None

class DespachoCreate(BaseModel):
    fecha_despacho: date
    numero_lote_despacho: Optional[str] = None
    estado_producto: Optional[str] = None
    propietario_pulpa: Optional[str] = None
    origen_carga: Optional[str] = None
    destino_carga: Optional[str] = None
    detalle_transporte: Optional[str] = None
    codigo_ncoi: Optional[str] = None
    precio_bs_kg: Optional[Decimal] = Field(None, gt=0)
    estado_pulpa: Optional[str] = None
    entregado_por: Optional[FirmaBlock] = None
    conductor: Optional[FirmaBlock] = None
    autorizado_por: Optional[FirmaBlock] = None
    entregado_destino: Optional[FirmaBlock] = None
    items: List[ItemDespachoCreate] = Field(..., min_length=1)

class RecepcionDestinoBody(BaseModel):
    recibido_por_nombre: Optional[str] = None
    recibido_por_ci: Optional[str] = None
    recibido_por_cargo: Optional[str] = None
    fecha_recibido: Optional[date] = None
    cantidad_recibida_kg: Optional[Decimal] = Field(None, gt=0)

class DespachoOut(BaseModel):
    id: int
    responsable_id: uuid.UUID
    fecha_despacho: date
    numero_lote_despacho: Optional[str]
    estado_producto: Optional[str]
    propietario_pulpa: Optional[str]
    origen_carga: Optional[str]
    destino_carga: Optional[str]
    detalle_transporte: Optional[str]
    codigo_ncoi: Optional[str]
    precio_bs_kg: Optional[Decimal]
    total_kg: Optional[Decimal]
    total_bs: Optional[Decimal]
    estado_pulpa: Optional[str]
    entregado_por_nombre: Optional[str]
    entregado_por_ci: Optional[str]
    entregado_por_cargo: Optional[str]
    conductor_nombre: Optional[str]
    conductor_ci: Optional[str]
    conductor_cargo: Optional[str]
    autorizado_por_nombre: Optional[str]
    autorizado_por_ci: Optional[str]
    autorizado_por_cargo: Optional[str]
    entregado_destino_nombre: Optional[str]
    entregado_destino_ci: Optional[str]
    entregado_destino_cargo: Optional[str]
    recibido_por_nombre: Optional[str]
    recibido_por_ci: Optional[str]
    recibido_por_cargo: Optional[str]
    fecha_recibido: Optional[date]
    cantidad_recibida_kg: Optional[Decimal]
    items: List[ItemDespachoOut] = []
    class Config:
        from_attributes = True
