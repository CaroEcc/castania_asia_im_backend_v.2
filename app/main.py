# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import reports, precio_justo, comunidades
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="API Inteligencia de Mercados - Castaña y Asaí",
    description="API para el sistema de Inteligencia de Mercados que calcula precios justos para productores de Castaña y Asaí",
    version="2.1.0"
)

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

# Registrar rutas
app.include_router(reports.router)
app.include_router(precio_justo.router)
app.include_router(comunidades.router)

@app.get("/")
def root():
    return {
        "message": "API de Inteligencia de Mercado activa",
        "version": "2.1.0",
        "endpoints": {
            "reportes": "/reportes",
            "precio_justo": "/precio-justo/calcular",
            "variables_maestras": "/precio-justo/variables-maestras",
            "comunidades": "/comunidades",
            "docs": "/docs"
        }
    }
