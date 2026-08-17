from pydantic import BaseModel, Field
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

import uuid
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
    documento_tenencia: Optional[str]
    codigo_tc: Optional[str]
    especie: Optional[str]
    fecha_registro: date
    estado: str
    usuario_id: uuid.UUID

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
# SCHEMAS — MÓDULO 2: LOTES DE MATERIA PRIMA
# =============================================================================

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

    class Config:
        from_attributes = True
