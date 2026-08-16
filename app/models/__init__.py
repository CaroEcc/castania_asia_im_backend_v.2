from __future__ import annotations

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, DateTime, Time,
    ForeignKey, JSON, UniqueConstraint, Uuid,
)
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

# =============================================================================
# MIXIN DE AUDITORÍA — aplicado a todos los modelos SIC
# =============================================================================


class AuditMixin:
    """
    Campos de auditoría estándar. Se mezcla en todos los modelos SIC.
    - created_by / updated_by: username o UUID del usuario que realizó la acción
    - created_at / updated_at: timestamps automáticos
    - is_active: soft-enable (True por defecto)
    - deleted_at: soft-delete (None = no eliminado)
    """
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime, nullable=True)


# =============================================================================
# MODELOS DE BASE DE DATOS - Versión 4.2 "Sembrando Datos"
# =============================================================================


class Usuario(Base):
    """
    Tabla: usuarios
    Sección 0: Identificación del Usuario (Preguntas P1-P7)
    Información básica del productor, recolector, cosechador o intermediario
    """
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)

    # P1: Nombre
    nombre = Column(String(100), nullable=False)

    # P2: Producto que trabaja
    rubro = Column(String(20), nullable=False)  # Castaña, Asaí, Ambos productos

    # P3: Actividades que realiza (array de strings, almacenado como JSON)
    actividades = Column(JSON, nullable=False)

    # P4: Género
    genero = Column(String(20), nullable=False)

    # P5: Rango de edad
    edad = Column(String(20), nullable=False)

    # P7: Ubicación GPS (opcional)
    gps_lat = Column(Numeric(10, 6))
    gps_lon = Column(Numeric(10, 6))

    # Metadata automática
    device_id = Column(String(255), unique=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    # Relaciones
    reportes = relationship("Reporte", back_populates="usuario")


class Comunidad(Base):
    __tablename__ = "comunidades"
    id_comunidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(500), nullable=False)
    abreviacion = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)  # Activa, Inactiva

    reportes = relationship("Reporte", back_populates="comunidad")


class Reporte(Base):
    """
    Tabla: reportes
    Formularios enviados por usuarios con información de precios, calidad,
    transporte y mercados. Refleja las Secciones 1 a 5 del formulario (P8-P27).
    """
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_comunidad = Column(Integer, ForeignKey("comunidades.id_comunidad"))

    # === SECCIÓN 1: PRECIOS (P8-P14) ===
    precio_recolector_castana = Column(Numeric(10, 2))
    unidad_recolector_castana = Column(String(50))
    precio_intermediario_castana = Column(Numeric(10, 2))
    unidad_intermediario_castana = Column(String(50))
    costo_transporte_castana = Column(Numeric(10, 2))
    unidad_transporte_castana = Column(String(50))
    tipo_transporte_castana = Column(String(30))

    precio_cosechador_asai = Column(Numeric(10, 2))
    unidad_cosechador_asai = Column(String(50))
    precio_intermediario_asai = Column(Numeric(10, 2))
    unidad_intermediario_asai = Column(String(50))
    costo_transporte_asai = Column(Numeric(10, 2))
    unidad_transporte_asai = Column(String(50))
    tipo_transporte_asai = Column(String(30))

    nodo_precio = Column(String(100))
    nodo_precio_otro = Column(String(100))

    # === SECCIÓN 2: CALIDAD DEL PRODUCTO (P15-P19) ===
    tipo_castana = Column(String(30))
    tiempo_recoleccion_castana = Column(Integer)
    tiempo_venta_castana = Column(Integer)
    tipo_asai = Column(String(30))
    tiempo_cosecha_asai = Column(Integer)

    # === SECCIÓN 3: COSTOS DE TRANSPORTE (P22) ===
    tipo_transporte_usado = Column(String(50))
    tipo_transporte_usado_otro = Column(String(100))

    # === SECCIÓN 4: PRECIOS EN MERCADOS GRANDES (P23-P25) ===
    no_sabe_fob_castana = Column(Boolean, default=False)
    moneda_fob_castana = Column(String(10))
    precio_fob_castana = Column(Numeric(10, 2))
    unidad_fob_castana = Column(String(50))
    fuente_precio_castana = Column(String(100))
    fuente_precio_castana_otro = Column(String(100))

    no_sabe_mercado_asai = Column(Boolean, default=False)
    precio_mercado_grande_asai = Column(Numeric(10, 2))
    unidad_mercado_grande_asai = Column(String(50))
    mercado_asai = Column(String(100))
    mercado_asai_otro = Column(String(100))
    fuente_precio_asai = Column(String(100))
    fuente_precio_asai_otro = Column(String(100))

    # === SECCIÓN 5: FEEDBACK ===
    comentarios_adicionales = Column(Text)

    # === METADATA AUTOMÁTICA ===
    latitud = Column(Numeric(10, 6))
    longitud = Column(Numeric(10, 6))
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="reportes")
    comunidad = relationship("Comunidad", back_populates="reportes")


# =============================================================================
# MODELOS SIC - Sembrando Datos v2.0
# =============================================================================


class Rol(Base):
    """
    Tabla: roles
    Catálogo fijo de los 4 roles del sistema. Solo lectura vía API.
    Se puebla una vez con el script seed_roles.py y no se modifica.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)        # recolector | responsable_acopio | operador_planta | administrador
    descripcion = Column(String(200), nullable=False)
    metodo_auth = Column(String(20), nullable=False)                # pin | password

# Solo recolectores usan PIN; los demás roles usan password
ROLES_PIN = {"recolector"}


class UsuarioSistema(AuditMixin, Base):
    """
    Tabla: usuarios_sistema
    Usuarios del Sistema Interno de Control (SIC) con autenticación JWT.
    Tabla separada de 'usuarios' (app móvil de inteligencia de mercados).
    """
    __tablename__ = "usuarios_sistema"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo = Column(String(200), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)

    # recolector | responsable_acopio | operador_planta | administrador
    rol = Column(String(50), nullable=False)

    # pin | password — calculado automáticamente según el rol
    metodo_auth = Column(String(20), nullable=False)

    # Hash bcrypt del PIN o password — NUNCA se expone en ningún response
    credencial_hash = Column(String(255), nullable=False)

    # Solo relevante para recolectores
    comunidad = Column(String(200), nullable=True)

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)

    # FK a sí mismo: quién dio de alta este usuario (auditoría)
    creado_por = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=True)


# =============================================================================
# MÓDULO 1 — RECOLECTORES (Área A)
# =============================================================================


class Recolector(AuditMixin, Base):
    """
    Tabla: recolectores
    Registro base del recolector/cosechador. Datos estables que no cambian por zafra.
    Formulario 1.2 cabecera (datos fijos del productor).
    """
    __tablename__ = "recolectores"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Vínculo con cuenta de sistema (1:1, todo recolector tiene una cuenta)
    usuario_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), unique=True, nullable=False)

    # Comunidad a la que pertenece
    comunidad_id = Column(Integer, ForeignKey("comunidades.id_comunidad"), nullable=False)

    # Auditoría: quién registró al recolector
    creado_por = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    # Datos del productor
    codigo = Column(String(20), nullable=False)             # ej: VF-GGS
    nombre_completo = Column(String(200), nullable=False)
    ci = Column(String(20), nullable=False)
    documento_tenencia = Column(Text, nullable=True)        # ej: "PGIBT N° 123-2024"
    codigo_tc = Column(Text, nullable=True)                 # N° TC productor (ej: BO-BIO-6088)
    especie = Column(String(100), nullable=True)            # especie(s) aprovechada(s)

    fecha_registro = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False, default="activo")  # activo | inactivo

    # Relaciones
    usuario = relationship("UsuarioSistema", foreign_keys=[usuario_id])
    creado_por_usuario = relationship("UsuarioSistema", foreign_keys=[creado_por])
    comunidad = relationship("Comunidad")
    autorizaciones = relationship("AutorizacionRecolector", back_populates="recolector")


class AutorizacionZafra(AuditMixin, Base):
    """
    Tabla: autorizaciones_zafra
    Cabecera del Formulario 1.1 (SERNAP) — autorización por comunidad y temporada.
    Una autorización habilita a N recolectores de esa comunidad para esa zafra.
    """
    __tablename__ = "autorizaciones_zafra"

    id = Column(Integer, primary_key=True, autoincrement=True)

    comunidad_id = Column(Integer, ForeignKey("comunidades.id_comunidad"), nullable=False)
    creado_por = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    codigo_documento = Column(String(100), nullable=True)   # ej: COD-C.C. N° DIR-RRNM-N° 004/2026
    solicitante = Column(String(200), nullable=False)
    ci_solicitante = Column(String(20), nullable=True)
    expediente = Column(String(100), nullable=True)
    cosecha = Column(Integer, nullable=False)               # año de cosecha, ej: 2026
    fecha_inicio_recoleccion = Column(Date, nullable=True)
    fecha_fin_recoleccion = Column(Date, nullable=True)
    n_dias_recoleccion = Column(Integer, nullable=True)
    superficie_km2 = Column(Numeric(10, 4), nullable=True)
    zona_autorizacion = Column(String(200), nullable=True)  # zona geográfica autorizada
    sello_sernap = Column(Boolean, nullable=False, default=False)

    # Relaciones
    comunidad = relationship("Comunidad")
    creado_por_usuario = relationship("UsuarioSistema", foreign_keys=[creado_por])
    recolectores = relationship("AutorizacionRecolector", back_populates="autorizacion_zafra")


class AutorizacionRecolector(AuditMixin, Base):
    """
    Tabla: autorizaciones_recolector
    Pivot N:M entre AutorizacionZafra y Recolector.
    Almacena los datos por zafra del recolector (Formulario 1.2):
    polígono GPS, superficie, producción estimada y estado de certificación.
    """
    __tablename__ = "autorizaciones_recolector"
    __table_args__ = (
        UniqueConstraint("autorizacion_zafra_id", "recolector_id", name="uq_autorizacion_recolector"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    autorizacion_zafra_id = Column(Integer, ForeignKey("autorizaciones_zafra.id"), nullable=False)
    recolector_id = Column(Integer, ForeignKey("recolectores.id"), nullable=False)

    # Datos por zafra (pueden cambiar cada temporada)
    especie = Column(String(100), nullable=True)            # especie(s) para esta zafra
    poligono_gps = Column(JSON, nullable=True)              # GeoJSON Polygon de la parcela
    superficie_ha = Column(Numeric(10, 4), nullable=True)   # calculada del polígono o manual
    produccion_estimada_kg = Column(Numeric(10, 2), nullable=True)
    estado_recoleccion = Column(String(100), nullable=True) # ej: "Recolector Orgánico - Habilitado"

    # Relaciones
    autorizacion_zafra = relationship("AutorizacionZafra", back_populates="recolectores")
    recolector = relationship("Recolector", back_populates="autorizaciones")
    items_recepcion = relationship("ItemRecepcion", back_populates="autorizacion_recolector")


# =============================================================================
# MÓDULO 1 — ÁREA A (continuación)
# =============================================================================


class EntregaRecolector(AuditMixin, Base):
    """
    Tabla: entregas_recolector
    Filas del Formulario 1.2 — cada entrega individual de un recolector a acopio.
    """
    __tablename__ = "entregas_recolector"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_entrega = Column(String(50), nullable=True)
    recolector_id = Column(Integer, ForeignKey("recolectores.id"), nullable=False)
    lote_materia_prima_id = Column(Integer, ForeignKey("lotes_materia_prima.id"), nullable=True)

    fecha_recoleccion = Column(Date, nullable=True)
    fecha_entrega = Column(Date, nullable=True)
    tipo_envase = Column(String(50), nullable=True)          # Saco, Tina, etc.
    peso_kg = Column(Numeric(10, 3), nullable=False)
    hora_cosecha = Column(Time, nullable=True)
    hora_recepcion = Column(Time, nullable=True)
    medio_transporte = Column(String(50), nullable=True)     # Fluvial | Terrestre
    estado_recepcion = Column(String(20), nullable=True)     # Aceptado | Rechazado
    firma_recolector = Column(Boolean, nullable=False, default=False)
    firma_responsable_acopio = Column(Boolean, nullable=False, default=False)
    observaciones = Column(Text, nullable=True)

    # Relaciones
    recolector = relationship("Recolector")
    lote_materia_prima = relationship("LoteMateriaPrima", back_populates="entregas")
    items_recepcion = relationship("ItemRecepcion", back_populates="entrega_recolector")


# =============================================================================
# MÓDULO 2 — RECEPCIÓN DE MATERIA PRIMA (Área B)
# =============================================================================


class LoteMateriaPrima(AuditMixin, Base):
    """
    Tabla: lotes_materia_prima
    Cabecera del Formulario 2.1 — lote de acopio abierto por el responsable.
    Máquina de estados: abierto → cerrado → en_limpieza → en_ablandamiento
                        → en_elaboracion → completado | rechazado
    """
    __tablename__ = "lotes_materia_prima"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_lote = Column(String(50), unique=True, nullable=False)   # LMP-{YYYYMMDD}-{HHMM}
    comunidad_id = Column(Integer, ForeignKey("comunidades.id_comunidad"), nullable=False)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    es_organico = Column(Boolean, nullable=False)
    fruto = Column(String(50), nullable=False, default="asaí")
    fecha_apertura = Column(DateTime, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
    total_kg = Column(Numeric(10, 3), nullable=False, default=0)
    total_bs = Column(Numeric(12, 2), nullable=False, default=0)

    estado = Column(String(30), nullable=False, default="abierto")
    # abierto | cerrado | en_limpieza | en_ablandamiento | en_elaboracion | completado | rechazado
    motivo_rechazo = Column(Text, nullable=True)
    rechazado_en = Column(DateTime, nullable=True)

    vobo_control = Column(Boolean, nullable=False, default=False)
    vobo_planta = Column(Boolean, nullable=False, default=False)

    # Relaciones
    comunidad = relationship("Comunidad")
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    entregas = relationship("EntregaRecolector", back_populates="lote_materia_prima")
    items_recepcion = relationship("ItemRecepcion", back_populates="lote_materia_prima")
    proceso_limpieza = relationship("ProcesoLimpieza", back_populates="lote_materia_prima", uselist=False)
    proceso_ablandamiento = relationship("ProcesoAblandamiento", back_populates="lote_materia_prima", uselist=False)
    proceso_elaboracion = relationship("ProcesoElaboracionPulpa", back_populates="lote_materia_prima", uselist=False)
    lotes_producto_terminado = relationship("LoteProductoTerminado", back_populates="lote_materia_prima")


class ItemRecepcion(AuditMixin, Base):
    """
    Tabla: items_recepcion
    Filas del Formulario 2.1 — una fila por recolector dentro del lote.
    """
    __tablename__ = "items_recepcion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_materia_prima_id = Column(Integer, ForeignKey("lotes_materia_prima.id"), nullable=False)
    recolector_id = Column(Integer, ForeignKey("recolectores.id"), nullable=False)
    entrega_recolector_id = Column(Integer, ForeignKey("entregas_recolector.id"), nullable=True)
    autorizacion_recolector_id = Column(Integer, ForeignKey("autorizaciones_recolector.id"), nullable=True)

    zona_autorizacion = Column(String(100), nullable=True)
    tipo_asai = Column(String(20), nullable=True)            # altura | bajio
    numero_compra = Column(Integer, nullable=True)
    peso_kg = Column(Numeric(10, 3), nullable=False)
    precio_bs_kg = Column(Numeric(10, 2), nullable=False)
    precio_total_bs = Column(Numeric(12, 2), nullable=False)
    firma_entrega = Column(Boolean, nullable=False, default=False)
    firma_pago = Column(Boolean, nullable=False, default=False)

    # Relaciones
    lote_materia_prima = relationship("LoteMateriaPrima", back_populates="items_recepcion")
    recolector = relationship("Recolector")
    entrega_recolector = relationship("EntregaRecolector", back_populates="items_recepcion")
    autorizacion_recolector = relationship("AutorizacionRecolector", back_populates="items_recepcion")


# =============================================================================
# MÓDULO 3A — PROCESO DE LIMPIEZA
# =============================================================================


class ProcesoLimpieza(AuditMixin, Base):
    """
    Tabla: procesos_limpieza
    Cabecera del Formulario B2.2 — un proceso por lote (UNIQUE).
    """
    __tablename__ = "procesos_limpieza"
    __table_args__ = (
        UniqueConstraint("lote_materia_prima_id", name="uq_limpieza_lote"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_materia_prima_id = Column(Integer, ForeignKey("lotes_materia_prima.id"), nullable=False)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    hora_inicio = Column(Time, nullable=True)
    hora_final = Column(Time, nullable=True)
    total_kg_ingreso = Column(Numeric(10, 3), nullable=True)   # debe == LoteMateriaPrima.total_kg
    total_kg_salida = Column(Numeric(10, 3), nullable=True)    # ingreso − suma residuos subprocesos
    numero_procesos = Column(Integer, nullable=True)
    es_organico = Column(Boolean, nullable=False)
    observaciones = Column(Text, nullable=True)
    firma_responsable_planilla = Column(Boolean, nullable=False, default=False)
    vobo_planta = Column(Boolean, nullable=False, default=False)
    vobo_control_calidad = Column(Boolean, nullable=False, default=False)

    # Relaciones
    lote_materia_prima = relationship("LoteMateriaPrima", back_populates="proceso_limpieza")
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    subprocesos = relationship("SubprocesoLimpieza", back_populates="proceso_limpieza")
    proceso_ablandamiento = relationship("ProcesoAblandamiento", back_populates="proceso_limpieza", uselist=False)


class SubprocesoLimpieza(AuditMixin, Base):
    """
    Tabla: subprocesos_limpieza
    Filas del Formulario B2.2 — un subproceso por ronda de limpieza.
    """
    __tablename__ = "subprocesos_limpieza"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proceso_limpieza_id = Column(Integer, ForeignKey("procesos_limpieza.id"), nullable=False)
    numero_proceso = Column(Integer, nullable=False)

    hora_inicio_seco = Column(Time, nullable=True)
    hora_final_seco = Column(Time, nullable=True)
    residuos_kg = Column(Numeric(10, 3), nullable=True)
    tipo_recipiente_inmersion = Column(String(50), nullable=True)   # ej: T1000
    hora_inicio_lavado = Column(Time, nullable=True)
    hora_final_lavado = Column(Time, nullable=True)

    # Relaciones
    proceso_limpieza = relationship("ProcesoLimpieza", back_populates="subprocesos")


# =============================================================================
# MÓDULO 3B — PROCESO DE ABLANDAMIENTO
# =============================================================================


class ProcesoAblandamiento(AuditMixin, Base):
    """
    Tabla: procesos_ablandamiento
    Cabecera del Formulario B2.3 — un proceso por lote (UNIQUE).
    Encadenado a ProcesoLimpieza para balance de masa.
    """
    __tablename__ = "procesos_ablandamiento"
    __table_args__ = (
        UniqueConstraint("lote_materia_prima_id", name="uq_ablandamiento_lote"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_materia_prima_id = Column(Integer, ForeignKey("lotes_materia_prima.id"), nullable=False)
    proceso_limpieza_id = Column(Integer, ForeignKey("procesos_limpieza.id"), nullable=False)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    hora_inicio = Column(Time, nullable=True)
    hora_final = Column(Time, nullable=True)
    total_kg_ingreso = Column(Numeric(10, 3), nullable=True)   # debe == ProcesoLimpieza.total_kg_salida
    total_kg_salida = Column(Numeric(10, 3), nullable=True)
    numero_procesos = Column(Integer, nullable=True)
    es_organico = Column(Boolean, nullable=False)
    observaciones = Column(Text, nullable=True)
    firma_responsable_planilla = Column(Boolean, nullable=False, default=False)
    vobo_planta = Column(Boolean, nullable=False, default=False)
    vobo_control_calidad = Column(Boolean, nullable=False, default=False)

    # Relaciones
    lote_materia_prima = relationship("LoteMateriaPrima", back_populates="proceso_ablandamiento")
    proceso_limpieza = relationship("ProcesoLimpieza", back_populates="proceso_ablandamiento")
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    subprocesos = relationship("SubprocesoAblandamiento", back_populates="proceso_ablandamiento")
    proceso_elaboracion = relationship("ProcesoElaboracionPulpa", back_populates="proceso_ablandamiento", uselist=False)


class SubprocesoAblandamiento(AuditMixin, Base):
    """
    Tabla: subprocesos_ablandamiento
    Filas del Formulario B2.3 — un subproceso por ronda de ablandamiento.
    """
    __tablename__ = "subprocesos_ablandamiento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proceso_id = Column(Integer, ForeignKey("procesos_ablandamiento.id"), nullable=False)
    numero_proceso = Column(Integer, nullable=False)

    tipo_recipiente_ablandamiento = Column(String(50), nullable=True)
    litros_agua_ablandamiento = Column(Numeric(10, 2), nullable=True)
    tipo_recipiente_enfriado = Column(String(50), nullable=True)
    litros_agua_enfriado_t1000 = Column(Numeric(10, 2), nullable=True)
    litros_agua_enfriado_canastas = Column(Numeric(10, 2), nullable=True)
    hora_inicio = Column(Time, nullable=True)
    hora_final = Column(Time, nullable=True)
    temp_inicio = Column(Numeric(5, 2), nullable=True)
    temp_intermedia = Column(Numeric(5, 2), nullable=True)
    temp_final = Column(Numeric(5, 2), nullable=True)
    diferencia_temp = Column(Numeric(5, 2), nullable=True)

    # Relaciones
    proceso_ablandamiento = relationship("ProcesoAblandamiento", back_populates="subprocesos")


# =============================================================================
# MÓDULO 3C — PROCESO DE ELABORACIÓN DE PULPA
# =============================================================================


class ProcesoElaboracionPulpa(AuditMixin, Base):
    """
    Tabla: procesos_elaboracion_pulpa
    Cabecera del Formulario B2.4 — un proceso por lote (UNIQUE).
    Encadenado a ProcesoAblandamiento para balance de masa.
    """
    __tablename__ = "procesos_elaboracion_pulpa"
    __table_args__ = (
        UniqueConstraint("lote_materia_prima_id", name="uq_elaboracion_lote"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_materia_prima_id = Column(Integer, ForeignKey("lotes_materia_prima.id"), nullable=False)
    proceso_ablandamiento_id = Column(Integer, ForeignKey("procesos_ablandamiento.id"), nullable=False)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    es_organico = Column(Boolean, nullable=False)
    observaciones = Column(Text, nullable=True)
    firma_responsable_planilla = Column(Boolean, nullable=False, default=False)
    vobo_planta = Column(Boolean, nullable=False, default=False)
    vobo_control_calidad = Column(Boolean, nullable=False, default=False)

    # Relaciones
    lote_materia_prima = relationship("LoteMateriaPrima", back_populates="proceso_elaboracion")
    proceso_ablandamiento = relationship("ProcesoAblandamiento", back_populates="proceso_elaboracion")
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    lotes_producto_terminado = relationship("LoteProductoTerminado", back_populates="proceso_elaboracion")


class LoteProductoTerminado(AuditMixin, Base):
    """
    Tabla: lotes_producto_terminado
    Filas del Formulario B2.4 — N lotes por proceso de elaboración.
    Máquina de estados: en_proceso → choque_termico → camara_frio
                        → parcialmente_despachado → despachado
    """
    __tablename__ = "lotes_producto_terminado"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_lote = Column(String(50), unique=True, nullable=False)   # LPT-{YYYYMMDD}-{HHMM}
    proceso_elaboracion_id = Column(Integer, ForeignKey("procesos_elaboracion_pulpa.id"), nullable=False)
    lote_materia_prima_id = Column(Integer, ForeignKey("lotes_materia_prima.id"), nullable=False)  # redundante

    fecha_proceso = Column(Date, nullable=True)
    hora_inicio = Column(Time, nullable=True)
    hora_final = Column(Time, nullable=True)
    tipo_pulpa = Column(String(20), nullable=False)             # premium | popular
    unidad_envase = Column(String(20), nullable=True)
    total_kg_fruto = Column(Numeric(10, 3), nullable=True)
    total_kg_pulpa = Column(Numeric(10, 3), nullable=True)
    rendimiento_pct = Column(Numeric(5, 2), nullable=True)
    porcentaje_solidos = Column(Numeric(5, 2), nullable=True)
    grados_brix = Column(Numeric(5, 2), nullable=True)
    ph = Column(Numeric(4, 2), nullable=True)
    es_organico = Column(Boolean, nullable=False)
    total_kg = Column(Numeric(10, 3), nullable=True)
    stock_actual_kg = Column(Numeric(10, 3), nullable=True)

    estado = Column(String(30), nullable=False, default="en_proceso")
    # en_proceso | choque_termico | camara_frio | parcialmente_despachado | despachado

    # Relaciones
    proceso_elaboracion = relationship("ProcesoElaboracionPulpa", back_populates="lotes_producto_terminado")
    lote_materia_prima = relationship("LoteMateriaPrima", back_populates="lotes_producto_terminado")
    items_choque_termico = relationship("ItemChoqueTermico", back_populates="lote_producto_terminado")
    items_inventario = relationship("InventarioCamaraFrio", back_populates="lote_producto_terminado")
    matriz_procesos = relationship("MatrizProcesos", back_populates="lote_producto_terminado", uselist=False)
    items_despacho = relationship("ItemDespacho", back_populates="lote_producto_terminado")


# =============================================================================
# MÓDULO 3D — CHOQUE TÉRMICO
# =============================================================================


class SesionChoqueTermico(AuditMixin, Base):
    """
    Tabla: sesiones_choque_termico
    Cabecera del Formulario B2.5 — una sesión agrupa N lotes en freezer.
    Las sesiones son homogéneas (todo orgánico o todo convencional).
    """
    __tablename__ = "sesiones_choque_termico"

    id = Column(Integer, primary_key=True, autoincrement=True)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    hora_inicio = Column(Time, nullable=True)
    hora_final = Column(Time, nullable=True)
    es_organico = Column(Boolean, nullable=False)
    observaciones = Column(Text, nullable=True)
    firma_responsable_planilla = Column(Boolean, nullable=False, default=False)
    vobo_planta = Column(Boolean, nullable=False, default=False)
    vobo_control_calidad = Column(Boolean, nullable=False, default=False)

    # Relaciones
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    items = relationship("ItemChoqueTermico", back_populates="sesion")


class ItemChoqueTermico(AuditMixin, Base):
    """
    Tabla: items_choque_termico
    Filas del Formulario B2.5 — un ítem por lote de producto terminado en la sesión.
    """
    __tablename__ = "items_choque_termico"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_choque_termico.id"), nullable=False)
    lote_producto_terminado_id = Column(Integer, ForeignKey("lotes_producto_terminado.id"), nullable=False)

    numero_freezer = Column(Integer, nullable=True)
    tipo_pulpa = Column(String(20), nullable=True)
    tipo_envase = Column(String(50), nullable=True)
    unidad = Column(String(20), nullable=True)
    cantidad = Column(Numeric(10, 3), nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    fecha_salida = Column(Date, nullable=True)

    # Relaciones
    sesion = relationship("SesionChoqueTermico", back_populates="items")
    lote_producto_terminado = relationship("LoteProductoTerminado", back_populates="items_choque_termico")


# =============================================================================
# MÓDULO 4A — INVENTARIO CÁMARA FRÍO
# =============================================================================


class InventarioCamaraFrio(AuditMixin, Base):
    """
    Tabla: inventario_camara_frio
    Registro de ingreso/salida de pulpa en cámara fría.
    """
    __tablename__ = "inventario_camara_frio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)
    lote_producto_terminado_id = Column(Integer, ForeignKey("lotes_producto_terminado.id"), nullable=False)

    tipo_pulpa = Column(String(20), nullable=True)
    estado = Column(String(20), nullable=True)               # bueno | observado
    tipo_envase = Column(String(50), nullable=True)
    unidad = Column(String(20), nullable=True)
    cantidad = Column(Numeric(10, 3), nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    fecha_salida = Column(Date, nullable=True)
    observaciones = Column(Text, nullable=True)
    firma_responsable_planilla = Column(Boolean, nullable=False, default=False)
    vobo_planta = Column(Boolean, nullable=False, default=False)
    vobo_control_calidad = Column(Boolean, nullable=False, default=False)

    # Relaciones
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    lote_producto_terminado = relationship("LoteProductoTerminado", back_populates="items_inventario")


# =============================================================================
# MÓDULO 4B — MATRIZ DE PROCESOS
# =============================================================================


class MatrizProcesos(AuditMixin, Base):
    """
    Tabla: matrices_procesos
    Cabecera del Formulario C3.2 — una por LPT (opcional, se llena en paralelo).
    """
    __tablename__ = "matrices_procesos"
    __table_args__ = (
        UniqueConstraint("lote_producto_terminado_id", name="uq_matriz_lpt"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    lote_producto_terminado_id = Column(Integer, ForeignKey("lotes_producto_terminado.id"), nullable=True)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)
    fecha = Column(Date, nullable=True)

    # Relaciones
    lote_producto_terminado = relationship("LoteProductoTerminado", back_populates="matriz_procesos")
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    items = relationship("ItemMatrizProcesos", back_populates="matriz")


class ItemMatrizProcesos(AuditMixin, Base):
    """
    Tabla: items_matriz_procesos
    Filas del Formulario C3.2 — 10 filas fijas por matriz (una por proceso).
    """
    __tablename__ = "items_matriz_procesos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    matriz_id = Column(Integer, ForeignKey("matrices_procesos.id"), nullable=False)

    proceso = Column(String(50), nullable=False)             # enum: recoleccion, transporte_entrada, etc.
    responsable_nombre = Column(String(200), nullable=True)
    tareas_principales = Column(Text, nullable=True)
    herramientas_equipos = Column(Text, nullable=True)

    # Relaciones
    matriz = relationship("MatrizProcesos", back_populates="items")


# =============================================================================
# MÓDULO 4C — DESPACHO
# =============================================================================


class Despacho(AuditMixin, Base):
    """
    Tabla: despachos
    Cabecera del Formulario C3.3 — un despacho puede incluir N lotes (N:M via ItemDespacho).
    """
    __tablename__ = "despachos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    responsable_id = Column(Uuid(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    fecha_despacho = Column(Date, nullable=False)
    numero_lote_despacho = Column(String(50), nullable=True)    # ej: AASN02-18-07-25
    estado_producto = Column(String(50), nullable=True)
    propietario_pulpa = Column(String(200), nullable=True)
    origen_carga = Column(String(200), nullable=True)
    destino_carga = Column(String(200), nullable=True)
    detalle_transporte = Column(Text, nullable=True)
    codigo_ncoi = Column(String(100), nullable=True)            # N° NCoI transacción (ej: BO-6640)

    precio_bs_kg = Column(Numeric(10, 2), nullable=True)
    total_kg = Column(Numeric(10, 3), nullable=True)
    total_bs = Column(Numeric(12, 2), nullable=True)
    estado_pulpa = Column(String(20), nullable=True)            # bueno | congelado

    # Tramo 1: Planta → Conductor
    entregado_por_nombre = Column(String(200), nullable=True)
    entregado_por_ci = Column(String(20), nullable=True)
    entregado_por_cargo = Column(String(100), nullable=True)
    conductor_nombre = Column(String(200), nullable=True)
    conductor_ci = Column(String(20), nullable=True)
    conductor_cargo = Column(String(100), nullable=True)
    autorizado_por_nombre = Column(String(200), nullable=True)
    autorizado_por_ci = Column(String(20), nullable=True)
    autorizado_por_cargo = Column(String(100), nullable=True)

    # Tramo 2: En destino
    entregado_destino_nombre = Column(String(200), nullable=True)
    entregado_destino_ci = Column(String(20), nullable=True)
    entregado_destino_cargo = Column(String(100), nullable=True)
    recibido_por_nombre = Column(String(200), nullable=True)
    recibido_por_ci = Column(String(20), nullable=True)
    recibido_por_cargo = Column(String(100), nullable=True)
    fecha_recibido = Column(Date, nullable=True)
    cantidad_recibida_kg = Column(Numeric(10, 3), nullable=True)

    # Relaciones
    responsable = relationship("UsuarioSistema", foreign_keys=[responsable_id])
    items = relationship("ItemDespacho", back_populates="despacho")


class ItemDespacho(AuditMixin, Base):
    """
    Tabla: items_despacho
    Filas del Formulario C3.3 — un ítem por LPT incluido en el despacho (N:M).
    """
    __tablename__ = "items_despacho"

    id = Column(Integer, primary_key=True, autoincrement=True)
    despacho_id = Column(Integer, ForeignKey("despachos.id"), nullable=False)
    lote_producto_terminado_id = Column(Integer, ForeignKey("lotes_producto_terminado.id"), nullable=False)

    fecha_despacho = Column(Date, nullable=True)
    numero_lote = Column(String(50), nullable=True)          # snapshot del número de lote
    peso_kg = Column(Numeric(10, 3), nullable=True)
    numero_cajas = Column(Integer, nullable=True)
    subtotal_bs = Column(Numeric(12, 2), nullable=True)

    # Relaciones
    despacho = relationship("Despacho", back_populates="items")
    lote_producto_terminado = relationship("LoteProductoTerminado", back_populates="items_despacho")
