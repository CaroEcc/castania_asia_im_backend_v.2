from app.database import engine, Base
from app import models

print("Creando tablas en Render...")
Base.metadata.create_all(bind=engine)
print("¡Listo!")
