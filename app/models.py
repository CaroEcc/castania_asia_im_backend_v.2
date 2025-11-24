# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, Boolean, Date, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

from .database import Base  # <— IMPORTANTE: usar la Base única

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
    actividades = Column(JSON, nullable=False)  # ["Recolección/Cosecha", "Procesamiento", "Transporte", "Comercialización", "Otro"]

    # P4: Género
    genero = Column(String(20), nullable=False)  # Masculino, Femenino, Otro, Prefiero no decir

    # P5: Rango de edad
    edad = Column(String(20), nullable=False)  # 18-25 años, 26-35 años, 36-45 años, 46-55 años, 56-65 años, 66+ años

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
    Formularios enviados por usuarios con información de precios, calidad, transporte y mercados
    Refleja las Secciones 1 a 5 del formulario (Preguntas P8-P27)
    """
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)

    id_comunidad = Column(Integer, ForeignKey("comunidades.id_comunidad"))  # FK a tabla comunidades (dropdown searchable)
    # === SECCIÓN 1: PRECIOS (P8-P14) ===

    # CASTAÑA
    # P8: Precio recolector de castaña
    precio_recolector_castana = Column(Numeric(10, 2))
    unidad_recolector_castana = Column(String(50))  # Caja, Barrica, Kilogramo

    # P9: Precio intermediario de castaña
    precio_intermediario_castana = Column(Numeric(10, 2))
    unidad_intermediario_castana = Column(String(50))  # Caja, Barrica, Kilogramo

    # P12a: Costo transporte castaña
    costo_transporte_castana = Column(Numeric(10, 2))
    unidad_transporte_castana = Column(String(50))  # Caja, Barrica, Kilogramo
    tipo_transporte_castana = Column(String(30))  # Fluvial, Terrestre

    # ASAÍ
    # P10: Precio cosechador de asaí
    precio_cosechador_asai = Column(Numeric(10, 2))
    unidad_cosechador_asai = Column(String(50))  # lata

    # P11: Precio intermediario de asaí
    precio_intermediario_asai = Column(Numeric(10, 2))
    unidad_intermediario_asai = Column(String(50))  # lata

    # P12b: Costo transporte asaí
    costo_transporte_asai = Column(Numeric(10, 2))
    unidad_transporte_asai = Column(String(50))  # Lata, Saco, Kg, Otro
    tipo_transporte_asai = Column(String(30))  # Fluvial, Terrestre

    # COMPARTIDAS
    # P13: Punto de venta/acopio (Nodo en cadena)
    nodo_precio = Column(String(100))  # En bosque/comunidad, En ciudad/puerto, En planta procesadora, En mercado local, Otro
    nodo_precio_otro = Column(String(100))  # Si selecciona "Otro"

    # === SECCIÓN 2: CALIDAD DEL PRODUCTO (P15-P19) ===

    # CASTAÑA
    # P15: Tipo de castaña
    tipo_castana = Column(String(30))  # Orgánico, Convencional

    # P16: Tiempo desde recolección
    tiempo_recoleccion_castana = Column(Integer)  # días

    # P17: Tiempo promedio para vender
    tiempo_venta_castana = Column(Integer)  # días

    # ASAÍ
    # P18: Tipo de asaí
    tipo_asai = Column(String(30))  # Silvestre, Cultivado, Mixto

    # P19: Horas desde cosecha
    tiempo_cosecha_asai = Column(Integer)  # horas

    # === SECCIÓN 3: COSTOS DE TRANSPORTE (P20-P22) ===
    # Nota: P20 y P21 ya están capturados en Sección 1 (P12a y P12b)

    # P22: Tipo de transporte principal utilizado
    tipo_transporte_usado = Column(String(50))  # Fluvial, Terrestre, Moto/Motocar, Combinado, Otro
    tipo_transporte_usado_otro = Column(String(100))  # Si selecciona "Otro"

    # === SECCIÓN 4: PRECIOS EN MERCADOS GRANDES (P23-P25) ===

    # CASTAÑA
    # P23: Precio FOB de referencia para exportar castaña
    no_sabe_fob_castana = Column(Boolean, default=False)
    moneda_fob_castana = Column(String(10))  # USD, Bs
    precio_fob_castana = Column(Numeric(10, 2))
    unidad_fob_castana = Column(String(50))  # Kg pulpa, Kg fruto, Litro, Otro

    # P25a: Fuente del precio FOB castaña
    fuente_precio_castana = Column(String(100))  # Noticias IBCE, Compradores directos, Asociación/Cooperativa, Redes sociales, Otro
    fuente_precio_castana_otro = Column(String(100))  # Si selecciona "Otro"

    # ASAÍ
    # P24: Precio de referencia en mercados locales grandes
    no_sabe_mercado_asai = Column(Boolean, default=False)
    precio_mercado_grande_asai = Column(Numeric(10, 2))  # Bs
    unidad_mercado_grande_asai = Column(String(50))  # Kg pulpa, Kg fruto, Litro, Lata, Otro
    mercado_asai = Column(String(100))  # Villa Florida, Cobija, Riberalta, La Paz, Santa Cruz, Trinidad, Otro
    mercado_asai_otro = Column(String(100))  # Si selecciona "Otro" en mercado

    # P25b: Fuente del precio asaí
    fuente_precio_asai = Column(String(100))  # Noticias IBCE, Compradores directos, Asociación/Cooperativa, Redes sociales, Otro
    fuente_precio_asai_otro = Column(String(100))  # Si selecciona "Otro"

    # === SECCIÓN 5: FEEDBACK ===
    # NOTA: P26 (impacto_clima e impacto_clima_como) eliminada completamente según body_enviado.md

    # Comentarios adicionales (opcional)
    comentarios_adicionales = Column(Text)

    # === METADATA AUTOMÁTICA ===
    latitud = Column(Numeric(10, 6))  # Coordenada actual al enviar
    longitud = Column(Numeric(10, 6))  # Coordenada actual al enviar
    fecha_registro = Column(DateTime, default=datetime.utcnow)  # Fecha y hora del envío

    # Relaciones
    usuario = relationship("Usuario", back_populates="reportes")
    comunidad = relationship("Comunidad", back_populates="reportes")

# Dependencia para usar en rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
