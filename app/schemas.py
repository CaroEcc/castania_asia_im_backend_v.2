# app/schemas.py
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# =============================================================================
# SCHEMAS PARA USUARIO (Sección 0: Identificación)
# =============================================================================

class UsuarioBase(BaseModel):
    """Base schema for Usuario with all P1-P7 fields"""
    nombre: str = Field(..., description="P1: Nombre del usuario")
    rubro: str = Field(..., description="P2: Castaña, Asaí, Ambos productos")
    actividades: List[str] = Field(..., description="P3: Array de actividades")
    genero: str = Field(..., description="P4: Masculino, Femenino, Otro, Prefiero no decir")
    edad: str = Field(..., description="P5: Rango de edad")
    gps_lat: Optional[Decimal] = Field(None, description="P7: Latitud GPS (opcional)")
    gps_lon: Optional[Decimal] = Field(None, description="P7: Longitud GPS (opcional)")

class UsuarioCreate(UsuarioBase):
    """Schema for creating a new usuario"""
    device_id: str = Field(..., description="Device unique identifier")

class UsuarioOut(UsuarioBase):
    """Schema for usuario output"""
    id_usuario: int
    device_id: str
    fecha_registro: datetime
    activo: bool

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2


# =============================================================================
# SCHEMAS PARA REPORTE (Secciones 1-5: Precios, Calidad, Transporte, Mercados, Feedback)
# =============================================================================

class ReporteBase(BaseModel):
    """Base schema for Reporte with all P8-P27 fields"""

    # === UBICACIÓN DEL REPORTE ===
    id_comunidad: Optional[int] = Field(None, description="ID de comunidad (dropdown searchable)")

    # === SECCIÓN 1: PRECIOS (P8-P14) ===
    # Castaña
    precio_recolector_castana: Optional[Decimal] = Field(None, description="P8: Precio recolector castaña")
    unidad_recolector_castana: Optional[str] = Field(None, description="P8: Unidad (Caja, Barrica, Kilogramo)")
    precio_intermediario_castana: Optional[Decimal] = Field(None, description="P9: Precio intermediario castaña")
    unidad_intermediario_castana: Optional[str] = Field(None, description="P9: Unidad")
    costo_transporte_castana: Optional[Decimal] = Field(None, description="P12a: Costo transporte castaña")
    unidad_transporte_castana: Optional[str] = Field(None, description="P12a: Unidad transporte")
    tipo_transporte_castana: Optional[str] = Field(None, description="P12a: Fluvial, Terrestre")

    # Asaí
    precio_cosechador_asai: Optional[Decimal] = Field(None, description="P10: Precio cosechador asaí")
    unidad_cosechador_asai: Optional[str] = Field(None, description="P10: Unidad (lata)")
    precio_intermediario_asai: Optional[Decimal] = Field(None, description="P11: Precio intermediario asaí")
    unidad_intermediario_asai: Optional[str] = Field(None, description="P11: Unidad")
    costo_transporte_asai: Optional[Decimal] = Field(None, description="P12b: Costo transporte asaí")
    unidad_transporte_asai: Optional[str] = Field(None, description="P12b: Unidad transporte")
    tipo_transporte_asai: Optional[str] = Field(None, description="P12b: Fluvial, Terrestre")

    # Compartidas
    nodo_precio: Optional[str] = Field(None, description="P13: Punto de venta/acopio")
    nodo_precio_otro: Optional[str] = Field(None, description="P13: Especificar si Otro")

    # === SECCIÓN 2: CALIDAD (P15-P19) ===
    # Castaña
    tipo_castana: Optional[str] = Field(None, description="P15: Orgánico, Convencional")
    tiempo_recoleccion_castana: Optional[int] = Field(None, description="P16: Días desde recolección")
    tiempo_venta_castana: Optional[int] = Field(None, description="P17: Días promedio para vender")

    # Asaí
    tipo_asai: Optional[str] = Field(None, description="P18: Silvestre, Cultivado, Mixto")
    tiempo_cosecha_asai: Optional[int] = Field(None, description="P19: Horas desde cosecha")

    # === SECCIÓN 3: TRANSPORTE (P22) ===
    tipo_transporte_usado: Optional[str] = Field(None, description="P22: Tipo principal de transporte")
    tipo_transporte_usado_otro: Optional[str] = Field(None, description="P22: Especificar si Otro")

    # === SECCIÓN 4: MERCADOS GRANDES (P23-P25) ===
    # Castaña
    no_sabe_fob_castana: Optional[bool] = Field(False, description="P23: Checkbox No sé")
    moneda_fob_castana: Optional[str] = Field(None, description="P23: USD o Bs")
    precio_fob_castana: Optional[Decimal] = Field(None, description="P23: Precio FOB castaña")
    unidad_fob_castana: Optional[str] = Field(None, description="P23: Unidad FOB")
    fuente_precio_castana: Optional[str] = Field(None, description="P25a: Fuente del precio FOB")
    fuente_precio_castana_otro: Optional[str] = Field(None, description="P25a: Especificar si Otro")

    # Asaí
    no_sabe_mercado_asai: Optional[bool] = Field(False, description="P24: Checkbox No sé")
    precio_mercado_grande_asai: Optional[Decimal] = Field(None, description="P24: Precio mercado grande")
    unidad_mercado_grande_asai: Optional[str] = Field(None, description="P24: Unidad")
    mercado_asai: Optional[str] = Field(None, description="P24: Mercado (Villa Florida, etc.)")
    mercado_asai_otro: Optional[str] = Field(None, description="P24: Especificar si Otro mercado")
    fuente_precio_asai: Optional[str] = Field(None, description="P25b: Fuente del precio asaí")
    fuente_precio_asai_otro: Optional[str] = Field(None, description="P25b: Especificar si Otro")

    # === SECCIÓN 5: FEEDBACK ===
    # NOTA: P26 (impacto_clima) eliminada completamente según body_enviado.md
    comentarios_adicionales: Optional[str] = Field(None, description="Comentarios adicionales opcionales")

    # === METADATA ===
    latitud: Optional[Decimal] = Field(None, description="Coordenada latitud al enviar")
    longitud: Optional[Decimal] = Field(None, description="Coordenada longitud al enviar")

class ReporteCreate(ReporteBase):
    """Schema for creating a new reporte"""
    id_usuario: int = Field(..., description="ID del usuario que envía el reporte")

class ReporteOut(ReporteBase):
    """Schema for reporte output"""
    id_reporte: int
    id_usuario: int
    fecha_registro: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2


# =============================================================================
# SCHEMA COMPLETO DEL FORMULARIO (body_form_1.md)
# =============================================================================

class FormularioCompletoRequest(BaseModel):
    """
    Schema completo del formulario que recibe todos los datos de las 5 secciones
    Basado en ReportePayload de body_form_1.md
    """
    model_config = {"populate_by_name": True}  # Permite usar tanto el nombre del campo como el alias
    # Section 0: User identification
    device_id: str = Field(..., description="Device unique identifier")
    nombre: Optional[str] = Field(None, description="P1: Nombre del usuario")
    rubro: Optional[str] = Field(None, description="P2: Castaña, Asaí, Ambos productos")
    actividades: Optional[List[str]] = Field(None, description="P3: Array de actividades")
    genero: Optional[str] = Field(None, description="P4: Género")
    edad: Optional[str] = Field(None, description="P5: Rango de edad")
    comunidad_id: Optional[int] = Field(None, description="ID de comunidad (dropdown searchable)")
    gps_lat: Optional[Decimal] = Field(None, description="Latitud GPS")
    gps_lon: Optional[Decimal] = Field(None, description="Longitud GPS")

    # Section 1: Prices - Castaña
    precio_recolector_castana: Optional[Decimal] = Field(None, description="P8: Precio recolector castaña", alias="precio_recolector_castania")
    unidad_recolector_castana: Optional[str] = Field(None, description="P8: Unidad", alias="unidad_recolector_castania")
    precio_intermediario_castana: Optional[Decimal] = Field(None, description="P9: Precio intermediario castaña", alias="precio_intermediario_castania")
    unidad_intermediario_castana: Optional[str] = Field(None, description="P9: Unidad", alias="unidad_intermediario_castania")

    # Section 1: Prices - Asaí
    precio_cosechador_asai: Optional[Decimal] = Field(None, description="P10: Precio cosechador asaí")
    unidad_cosechador_asai: Optional[str] = Field(None, description="P10: Unidad")
    precio_intermediario_asai: Optional[Decimal] = Field(None, description="P11: Precio intermediario asaí")
    unidad_intermediario_asai: Optional[str] = Field(None, description="P11: Unidad")

    # Section 1: Transport costs per product
    costo_transporte_castana: Optional[Decimal] = Field(None, description="P12a: Costo transporte castaña", alias="costo_transporte_castania")
    unidad_transporte_castana: Optional[str] = Field(None, description="P12a: Unidad transporte castaña", alias="unidad_transporte_castania")
    tipo_transporte_castana: Optional[str] = Field(None, description="P12a: Tipo transporte castaña", alias="tipo_transporte_castania")
    costo_transporte_asai: Optional[Decimal] = Field(None, description="P12b: Costo transporte asaí")
    unidad_transporte_asai: Optional[str] = Field(None, description="P12b: Unidad transporte asaí")
    tipo_transporte_asai: Optional[str] = Field(None, description="P12b: Tipo transporte asaí")

    # Section 1: Shared fields
    nodo_precio: Optional[str] = Field(None, description="P13: Punto de venta/acopio")
    nodo_precio_otro: Optional[str] = Field(None, description="P13: Especificar si Otro")

    # Section 2: Quality - Castaña
    tipo_castana: Optional[str] = Field(None, description="P15: Tipo de castaña", alias="tipo_castania")
    tiempo_recoleccion_castana: Optional[int] = Field(None, description="P16: Días desde recolección", alias="tiempo_recoleccion_castania")
    tiempo_venta_castana: Optional[int] = Field(None, description="P17: Días promedio para vender", alias="tiempo_venta_castania")

    # Section 2: Quality - Asaí
    tipo_asai: Optional[str] = Field(None, description="P18: Tipo de asaí")
    tiempo_cosecha_asai: Optional[int] = Field(None, description="P19: Horas desde cosecha")

    # Section 3: Transport
    tipo_transporte_usado: Optional[str] = Field(None, description="P22: Tipo principal de transporte")
    tipo_transporte_usado_otro: Optional[str] = Field(None, description="P22: Especificar si Otro")

    # Section 4: Big Market Prices - Castaña
    precio_fob_castana: Optional[Decimal] = Field(None, description="P23: Precio FOB castaña", alias="precio_fob_castania")
    moneda_fob_castana: Optional[str] = Field(None, description="P23: Moneda (USD/Bs)", alias="moneda_fob_castania")
    unidad_fob_castana: Optional[str] = Field(None, description="P23: Unidad FOB", alias="unidad_fob_castania")
    no_sabe_fob_castana: Optional[bool] = Field(False, description="P23: No sé checkbox", alias="no_sabe_fob_castania")

    # Section 4: Big Market Prices - Asaí
    precio_mercado_grande_asai: Optional[Decimal] = Field(None, description="P24: Precio mercado grande asaí")
    unidad_mercado_grande_asai: Optional[str] = Field(None, description="P24: Unidad")
    mercado_asai: Optional[str] = Field(None, description="P24: Mercado")
    mercado_asai_otro: Optional[str] = Field(None, description="P24: Especificar si Otro")
    no_sabe_mercado_asai: Optional[bool] = Field(False, description="P24: No sé checkbox")

    # Section 4: Price sources
    fuente_precio_castana: Optional[str] = Field(None, description="P25a: Fuente precio castaña", alias="fuente_precio_castania")
    fuente_precio_castana_otro: Optional[str] = Field(None, description="P25a: Especificar si Otro", alias="fuente_precio_castania_otro")
    fuente_precio_asai: Optional[str] = Field(None, description="P25b: Fuente precio asaí")
    fuente_precio_asai_otro: Optional[str] = Field(None, description="P25b: Especificar si Otro")

    # Section 5: Feedback
    # NOTA: P26 (impacto_clima) eliminada completamente según body_enviado.md
    comentarios_adicionales: Optional[str] = Field(None, description="Comentarios adicionales")

    # Metadata
    latitud: Optional[Decimal] = Field(None, description="Latitud al enviar")
    longitud: Optional[Decimal] = Field(None, description="Longitud al enviar")
    fecha_registro: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha de registro")


# =============================================================================
# SCHEMAS PARA CÁLCULO DE PRECIO JUSTO
# =============================================================================

class PrecioJustoRequest(BaseModel):
    """
    Schema para request de cálculo de Precio Justo
    Incluye solo los campos necesarios para el cálculo
    """
    # Datos del usuario
    comunidad: str = Field(..., description="P6: Comunidad de trabajo del usuario")

    # Datos de Castaña (opcionales, según rubro)
    costo_transporte_castana: Optional[Decimal] = Field(None, description="P12a: Costo transporte castaña")
    tipo_castana: Optional[str] = Field(None, description="P15: Tipo de castaña (Orgánico/Convencional)")
    tiempo_recoleccion_castana: Optional[int] = Field(None, description="P16: Días desde recolección")
    tiempo_venta_castana: Optional[int] = Field(None, description="P17: Días promedio para vender")

    # Datos de Asaí (opcionales, según rubro)
    costo_transporte_asai: Optional[Decimal] = Field(None, description="P12b: Costo transporte asaí")
    tipo_asai: Optional[str] = Field(None, description="P18: Tipo de asaí (Silvestre/Cultivado/Mixto)")
    tiempo_cosecha_asai: Optional[int] = Field(None, description="P19: Horas desde cosecha")


class PrecioJustoDetalles(BaseModel):
    """Detalles del cálculo del precio justo"""
    p_base_ajustado: Decimal = Field(..., description="Precio base ajustado por ubicación")
    bono_certificacion: Optional[Decimal] = Field(None, description="Bonificación por certificación orgánica")
    bono_frescura: Optional[Decimal] = Field(None, description="Bonificación por frescura (solo asaí)")
    ajuste_deterioro: Optional[Decimal] = Field(None, description="Ajuste por deterioro (solo castaña)")
    p_prom_planta: Decimal = Field(..., description="Precio promedio en planta (variable maestra)")
    costo_transporte: Decimal = Field(..., description="Costo de transporte reportado")


class PrecioJustoResultadoCastana(BaseModel):
    """Resultado del cálculo de Precio Justo para Castaña"""
    precio_justo: Decimal = Field(..., description="Precio Justo calculado en Bs")
    precio_minimo_zona: Optional[Decimal] = Field(None, description="Precio mínimo observado en la zona en Bs")
    mensaje: str = Field(..., description="Mensaje formateado para mostrar al usuario")
    detalles: PrecioJustoDetalles = Field(..., description="Detalles del cálculo")


class PrecioJustoResultadoAsai(BaseModel):
    """Resultado del cálculo de Precio Justo para Asaí"""
    precio_justo: Decimal = Field(..., description="Precio Justo calculado en Bs")
    precio_minimo_zona: Optional[Decimal] = Field(None, description="Precio mínimo observado en la zona en Bs")
    mensaje: str = Field(..., description="Mensaje formateado para mostrar al usuario")
    detalles: PrecioJustoDetalles = Field(..., description="Detalles del cálculo")


class PrecioJustoResponse(BaseModel):
    """
    Schema para response del cálculo de Precio Justo
    Incluye resultados para Castaña y/o Asaí según los datos proporcionados
    """
    castana: Optional[PrecioJustoResultadoCastana] = Field(None, description="Resultado para Castaña")
    asai: Optional[PrecioJustoResultadoAsai] = Field(None, description="Resultado para Asaí")
    fecha_calculo: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora del cálculo")


# =============================================================================
# SCHEMAS PARA COMUNIDADES (CRUD)
# =============================================================================

class ComunidadBase(BaseModel):
    """Base schema para Comunidad"""
    nombre: str = Field(..., min_length=1, max_length=500, description="Nombre de la comunidad")
    abreviacion: str = Field(..., min_length=1, max_length=50, description="Abreviación de la comunidad")


class ComunidadCreate(ComunidadBase):
    """Schema para crear una nueva comunidad"""
    pass


class ComunidadUpdate(BaseModel):
    """Schema para actualizar una comunidad (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=500, description="Nombre de la comunidad")
    abreviacion: Optional[str] = Field(None, min_length=1, max_length=50, description="Abreviación de la comunidad")
    status: Optional[str] = Field(None, description="Estado: 'Activa' o 'Inactiva'")


class ComunidadOut(ComunidadBase):
    """Schema para respuesta de comunidad"""
    id_comunidad: int
    status: str

    class Config:
        from_attributes = True


class ComunidadListResponse(BaseModel):
    """Schema para lista de comunidades con paginación"""
    total: int = Field(..., description="Total de comunidades")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    comunidades: List[ComunidadOut] = Field(..., description="Lista de comunidades")
