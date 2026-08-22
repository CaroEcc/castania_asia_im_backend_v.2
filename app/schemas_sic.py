# app/schemas_sic.py
"""
Schemas Pydantic para el CRUD de UsuarioSistema (SIC - Sembrando Datos v2.0).
Archivo separado de schemas.py para no colisionar con los schemas de la app móvil.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RolUsuario(str, Enum):
    recolector = "recolector"
    responsable_acopio = "responsable_acopio"
    operador_planta = "operador_planta"   # cubre Área B y C (antes: jefe_planta + encargado_camara)
    administrador = "administrador"


# Solo recolectores usan PIN; todos los demás roles usan password
ROLES_PIN = {RolUsuario.recolector}


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class UsuarioCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=2, max_length=200)
    username: str = Field(..., min_length=3, max_length=100)
    rol: RolUsuario
    comunidad: Optional[str] = Field(None, max_length=200)
    # Para roles con password (no-PIN): la contraseña inicial la define quien crea.
    # Para roles PIN: si se omite, el backend genera un PIN de 6 dígitos automáticamente.
    credencial: Optional[str] = Field(None, description="Password (roles password) o PIN inicial (roles PIN, opcional)")

    @model_validator(mode="after")
    def validar_credencial_password(self):
        if self.rol not in ROLES_PIN and not self.credencial:
            raise ValueError(
                f"El rol '{self.rol}' requiere una contraseña inicial en el campo 'credencial'"
            )
        return self


class UsuarioUpdate(BaseModel):
    """Solo permite cambiar nombre_completo y comunidad."""
    nombre_completo: Optional[str] = Field(None, min_length=2, max_length=200)
    comunidad: Optional[str] = Field(None, max_length=200)


class EstadoUpdate(BaseModel):
    activo: bool


class ResetCredencialRequest(BaseModel):
    """Para roles password: nueva_credencial es obligatoria.
       Para roles PIN: se ignora y se genera un PIN nuevo automáticamente."""
    nueva_credencial: Optional[str] = Field(None, description="Nueva contraseña (solo para roles password)")


# ---------------------------------------------------------------------------
# Output schemas — NUNCA incluyen credencial_hash
# ---------------------------------------------------------------------------

class ComunidadResumen(BaseModel):
    """Resumen mínimo de comunidad para incluir en UsuarioOut."""
    id_comunidad: int
    nombre: str
    abreviacion: str

    model_config = {"from_attributes": True}


class UsuarioOut(BaseModel):
    id: uuid.UUID
    nombre_completo: str
    username: str
    rol: str
    metodo_auth: str
    comunidad: Optional[str] = Field(
        None,
        description="Solo aplica al rol recolector: comunidad de pertenencia (texto libre)."
    )
    comunidades: List[ComunidadResumen] = Field(
        default_factory=list,
        description="Solo aplica al rol responsable_acopio: comunidades asignadas vía M:N."
    )
    activo: bool
    fecha_creacion: datetime
    creado_por: Optional[uuid.UUID]

    model_config = {"from_attributes": True}


class UsuarioCreateResponse(UsuarioOut):
    """Extiende UsuarioOut con el PIN generado UNA SOLA VEZ en la respuesta del POST.
       Solo viene populado para roles recolector/operador_planta.
       Nunca se puede recuperar después."""
    pin_generado: Optional[str] = Field(
        None,
        description="PIN de 6 dígitos generado. Solo visible en esta respuesta, nunca recuperable."
    )


class ResetCredencialResponse(BaseModel):
    mensaje: str
    pin_generado: Optional[str] = Field(
        None,
        description="Nuevo PIN generado. Solo visible en esta respuesta."
    )


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    credencial: str = Field(..., description="Password o PIN según el rol")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre_completo: str
