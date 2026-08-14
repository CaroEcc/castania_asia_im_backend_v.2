# conftest.py
# Debe estar en la raíz del proyecto y cargarse ANTES que cualquier import de app.*
# Fuerza el uso de SQLite en memoria para todos los tests, sin tocar la DB de producción.
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_sic.db"
