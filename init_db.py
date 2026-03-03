"""
Script completo de inicialización de base de datos
Crea todas las tablas y carga datos iniciales
"""
import sys
from app.database import Base, engine, SessionLocal
from app.models import Usuario, Comunidad, Reporte

# Lista de comunidades iniciales
COMUNIDADES_INICIALES = [
    {"nombre": "Trinchera", "abreviacion": "TR", "status": "1"},
    {"nombre": "Villa Florida", "abreviacion": "VF", "status": "1"},
    {"nombre": "Puerto Oro", "abreviacion": "PR", "status": "1"},
    {"nombre": "Jerico", "abreviacion": "JE", "status": "1"},
    {"nombre": "Chive", "abreviacion": "CH", "status": "1"},
]

def init_database():
    """Inicializa la base de datos completa"""
    print("=" * 70)
    print("INICIALIZACION DE BASE DE DATOS - Sistema IM ASAI/CASTANA")
    print("=" * 70)

    # Paso 1: Crear tablas
    print("\n[1/2] Creando tablas en la base de datos...")
    try:
        Base.metadata.create_all(bind=engine)
        print("OK - Tablas creadas exitosamente")
        print("  - usuarios")
        print("  - comunidades")
        print("  - reportes")
    except Exception as e:
        print(f"ERROR - No se pudieron crear las tablas: {e}")
        sys.exit(1)

    # Paso 2: Cargar comunidades iniciales
    print("\n[2/2] Cargando datos iniciales...")
    db = SessionLocal()

    try:
        # Verificar si ya hay comunidades
        count = db.query(Comunidad).count()
        if count > 0:
            print(f"AVISO - La base de datos ya tiene {count} comunidades")
            print("Las comunidades existentes NO seran modificadas")

        comunidades_creadas = 0
        comunidades_duplicadas = 0

        for com_data in COMUNIDADES_INICIALES:
            # Verificar si ya existe
            existe = db.query(Comunidad).filter(
                Comunidad.nombre == com_data["nombre"]
            ).first()

            if existe:
                print(f"  - '{com_data['nombre']}' ya existe, omitiendo...")
                comunidades_duplicadas += 1
                continue

            # Crear nueva comunidad
            comunidad = Comunidad(**com_data)
            db.add(comunidad)
            comunidades_creadas += 1
            print(f"  + {com_data['nombre']} ({com_data['abreviacion']})")

        # Guardar cambios
        db.commit()

        print(f"\nRESUMEN:")
        print(f"  - Comunidades nuevas: {comunidades_creadas}")
        print(f"  - Comunidades existentes: {comunidades_duplicadas}")
        print(f"  - Total en base de datos: {db.query(Comunidad).count()}")
        print(f"  - Usuarios registrados: {db.query(Usuario).count()}")
        print(f"  - Reportes enviados: {db.query(Reporte).count()}")

        print("\n" + "=" * 70)
        print("INICIALIZACION COMPLETADA EXITOSAMENTE")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"\nERROR - Error al cargar datos: {e}")
        sys.exit(1)

    finally:
        db.close()

if __name__ == "__main__":
    init_database()
