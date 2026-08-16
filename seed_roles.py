"""
seed_roles.py — Puebla la tabla 'roles' con los 4 roles del sistema.

Uso:
    python seed_roles.py

Es idempotente: si un rol ya existe (por nombre) lo omite sin error.
"""
from app.core.database import SessionLocal
from app.models import Rol

ROLES = [
    {
        "nombre": "recolector",
        "descripcion": "Productor o cosechador de campo. Opera la app móvil offline. Se autentica con PIN de 6 dígitos.",
        "metodo_auth": "pin",
    },
    {
        "nombre": "responsable_acopio",
        "descripcion": "Encargado del punto de acopio. Registra y gestiona la recepción de producto. Se autentica con password.",
        "metodo_auth": "password",
    },
    {
        "nombre": "operador_planta",
        "descripcion": "Operaciones de planta (Área B y C). Gestiona procesamiento y cámara. Se autentica con password.",
        "metodo_auth": "password",
    },
    {
        "nombre": "administrador",
        "descripcion": "Acceso total al sistema. Puede crear y gestionar usuarios, comunidades y configuración. Se autentica con password.",
        "metodo_auth": "password",
    },
]


def seed():
    db = SessionLocal()
    try:
        creados = 0
        for data in ROLES:
            existe = db.query(Rol).filter(Rol.nombre == data["nombre"]).first()
            if existe:
                print(f"  [omitido]  {data['nombre']} — ya existe")
                continue
            db.add(Rol(**data))
            creados += 1
            print(f"  [creado]   {data['nombre']}")
        db.commit()
        print(f"\nSeed completado: {creados} roles insertados.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
