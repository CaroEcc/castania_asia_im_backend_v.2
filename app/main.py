import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api.v1.router import router as v1_router
from app.routes import reports, precio_justo, comunidades, auth, usuarios

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="API Inteligencia de Mercados - Castaña y Asaí",
    description=(
        "API para el sistema de Inteligencia de Mercados que calcula precios justos "
        "para productores de Castaña y Asaí"
    ),
    version="2.2.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dashboard-asai-aceaa.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Manejo de errores centralizado — respuestas JSON consistentes
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "status_code": 422},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "status_code": 500},
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# v1 — nueva arquitectura modular
app.include_router(v1_router)

# Legacy — rutas anteriores mantenidas hasta migración completa a /api/v1/
app.include_router(reports.router)
app.include_router(precio_justo.router)
app.include_router(comunidades.router)
app.include_router(auth.router)
app.include_router(usuarios.router)


# ---------------------------------------------------------------------------
# Endpoints base
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Monitoring"])
def health():
    """Endpoint de salud para monitoreo. Sin autenticación."""
    return {"status": "ok", "environment": settings.environment}


@app.get("/")
def root():
    return {
        "message": "API de Inteligencia de Mercado activa",
        "version": "2.2.0",
        "endpoints": {
            "health": "/health",
            "auth_v1": "/api/v1/auth/login",
            "reportes": "/reportes",
            "precio_justo": "/precio-justo/calcular",
            "variables_maestras": "/precio-justo/variables-maestras",
            "comunidades": "/comunidades",
            "usuarios": "/usuarios",
            "auth_legacy": "/auth/token",
            "docs": "/docs",
        },
    }
