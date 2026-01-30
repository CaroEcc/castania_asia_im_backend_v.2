"""
Script para inicializar la base de datos
Crea todas las tablas definidas en los modelos
"""
from app.database import Base, engine
from app.models import Usuario, Comunidad, Reporte

def init_database():
    """Crea todas las tablas en la base de datos"""
    try:
        print("Conectando a la base de datos...")
        print(f"Creando tablas...")

        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)

        print("✓ Tablas creadas exitosamente:")
        print("  - usuarios")
        print("  - comunidades")
        print("  - reportes")

    except Exception as e:
        print(f"✗ Error al crear las tablas: {e}")
        raise

if __name__ == "__main__":
    init_database()
