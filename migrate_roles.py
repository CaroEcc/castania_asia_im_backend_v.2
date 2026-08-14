"""
Migración puntual: consolidar roles obsoletos → operador_planta
---------------------------------------------------------------
Convierte cualquier usuario_sistema con:
  - rol = 'jefe_planta'      →  'operador_planta'
  - rol = 'encargado_camara' →  'operador_planta'

También actualiza metodo_auth a 'password' si corresponde
(operador_planta ahora usa password, no PIN).

Ejecutar UNA sola vez:
  python migrate_roles.py
"""

from app.database import SessionLocal
from app.models import UsuarioSistema
from app.auth import get_password_hash

ROLES_OBSOLETOS = {"jefe_planta", "encargado_camara"}
ROL_DESTINO = "operador_planta"
METODO_AUTH_DESTINO = "password"


def migrar():
    db = SessionLocal()
    try:
        afectados = (
            db.query(UsuarioSistema)
            .filter(UsuarioSistema.rol.in_(ROLES_OBSOLETOS))
            .all()
        )

        if not afectados:
            print("No hay usuarios con roles obsoletos. Nada que migrar.")
            return

        print(f"Usuarios a migrar: {len(afectados)}\n")

        for u in afectados:
            rol_anterior = u.rol
            auth_anterior = u.metodo_auth
            u.rol = ROL_DESTINO
            u.metodo_auth = METODO_AUTH_DESTINO
            print(
                f"  [{u.username}] "
                f"rol: {rol_anterior} → {ROL_DESTINO} | "
                f"metodo_auth: {auth_anterior} → {METODO_AUTH_DESTINO}"
            )

        db.commit()
        print(f"\nMigración completada: {len(afectados)} usuario(s) actualizado(s).")

    except Exception as e:
        db.rollback()
        print(f"ERROR — rollback aplicado: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrar()
