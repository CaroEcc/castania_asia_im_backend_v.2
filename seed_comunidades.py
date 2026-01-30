"""
Script para poblar la tabla de comunidades con datos iniciales
"""
from app.database import SessionLocal
from app.models import Comunidad

# Lista de comunidades de la región amazónica boliviana
COMUNIDADES_INICIALES = [
    {"nombre": "Trinchera", "abreviacion": "TR", "status": "Activa"},
    {"nombre": "Villa Florida", "abreviacion": "VF", "status": "Activa"},
    {"nombre": "Puerto Oro", "abreviacion": "PR", "status": "Activa"},
    {"nombre": "Jerico", "abreviacion": "JE", "status": "Activa"},
    {"nombre": "Chive", "abreviacion": "CH", "status": "Activa"},
]

def seed_comunidades():
    """Carga datos iniciales en la tabla comunidades"""
    db = SessionLocal()

    try:
        # Verificar si ya hay comunidades
        count = db.query(Comunidad).count()
        if count > 0:
            print(f"⚠ La tabla ya tiene {count} comunidades. ¿Deseas continuar? (esto agregará más)")
            respuesta = input("Escribe 'si' para continuar: ")
            if respuesta.lower() != 'si':
                print("❌ Operación cancelada")
                return

        print(f"\n📋 Insertando {len(COMUNIDADES_INICIALES)} comunidades...")

        comunidades_creadas = 0
        comunidades_duplicadas = 0

        for com_data in COMUNIDADES_INICIALES:
            # Verificar si ya existe
            existe = db.query(Comunidad).filter(
                Comunidad.nombre == com_data["nombre"]
            ).first()

            if existe:
                print(f"  ⏭ '{com_data['nombre']}' ya existe, omitiendo...")
                comunidades_duplicadas += 1
                continue

            # Crear nueva comunidad
            comunidad = Comunidad(**com_data)
            db.add(comunidad)
            comunidades_creadas += 1
            print(f"  ✓ {com_data['nombre']} ({com_data['abreviacion']})")

        # Guardar cambios
        db.commit()

        print(f"\n✅ Proceso completado:")
        print(f"   - {comunidades_creadas} comunidades creadas")
        print(f"   - {comunidades_duplicadas} comunidades duplicadas (omitidas)")
        print(f"   - Total en BD: {db.query(Comunidad).count()}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error al cargar comunidades: {e}")
        raise

    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("CARGA DE COMUNIDADES INICIALES - Sistema IM ASAI/CASTAÑA")
    print("=" * 60)
    seed_comunidades()
