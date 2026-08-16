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
