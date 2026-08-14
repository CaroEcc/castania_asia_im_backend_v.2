from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, DateTime,
    ForeignKey, JSON, Uuid,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base

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

# Solo recolectores usan PIN; los demás roles usan password
ROLES_PIN = {"recolector"}


class UsuarioSistema(Base):
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
