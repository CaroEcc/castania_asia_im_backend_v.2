# crear_admin.py
# Ejecutar una sola vez para crear el usuario administrador inicial.
# Uso: venv/Scripts/python.exe crear_admin.py

import uuid
from datetime import datetime
from app.database import SessionLocal, engine
from app.models import Base, UsuarioSistema
from app.auth import get_password_hash

# ── Configurá estos valores antes de ejecutar ──────────────────────────────
NOMBRE    = "Administrador OFACC"
USERNAME  = "admin"
PASSWORD  = "Contraseña2026!"   # cambiá esto antes de ejecutar
# ───────────────────────────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)   # crea la tabla si no existe

db = SessionLocal()

if db.query(UsuarioSistema).filter(UsuarioSistema.username == USERNAME).first():
    print(f"Ya existe un usuario con username '{USERNAME}'. No se creó nada.")
else:
    admin = UsuarioSistema(
        id=uuid.uuid4(),
        nombre_completo=NOMBRE,
        username=USERNAME,
        rol="administrador",
        metodo_auth="password",
        credencial_hash=get_password_hash(PASSWORD),
        activo=True,
        fecha_creacion=datetime.utcnow(),
        creado_por=None,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Admin creado exitosamente.")
    print(f"  ID:       {admin.id}")
    print(f"  Username: {admin.username}")
    print(f"  Password: {PASSWORD}")

db.close()
