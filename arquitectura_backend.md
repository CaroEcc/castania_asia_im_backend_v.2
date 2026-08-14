Contexto del proyecto:
"Sembrando Datos v2.0" — sistema de trazabilidad para ACEAA (recolectores de 
asaí silvestre en Pando, Bolivia). Este es el backend, consumido tanto por un 
dashboard web (React) como por una app móvil (Expo) que opera offline en 
campo y sincroniza al recuperar conectividad.

Tarea: armar la arquitectura base del proyecto backend desde cero (todavía 
no hay código). No implementes ningún CRUD de negocio todavía — esto es 
solo el esqueleto, la configuración y los primeros endpoints de salud/auth.

Stack obligatorio:
- FastAPI
- SQLAlchemy 2.x (estilo declarativo moderno, no el legacy)
- Alembic para migraciones
- PostgreSQL con extensión PostGIS
- Pydantic v2 para schemas
- passlib con bcrypt para hasheo de credenciales (PIN y password)
- JWT para autenticación (python-jose o pyjwt, elegí uno y sé consistente)
- pytest para tests

Arquitectura a implementar: monolito modular en capas (routers → services → 
repositories → models), NO Clean Architecture completa ni microservicios — 
es una decisión ya tomada, no la cuestiones ni propongas alternativas.

Estructura de carpetas exacta a crear:

app/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── router.py          # agrega todos los routers de v1
│       └── (routers individuales se agregan después, por módulo)
├── schemas/                   # Pydantic, uno por dominio
├── services/                  # lógica de negocio, uno por dominio
├── repositories/               # acceso a datos, uno por dominio
├── models/                    # SQLAlchemy ORM
├── core/
│   ├── config.py              # settings con pydantic-settings, lee .env
│   ├── security.py            # hasheo, creación/validación de JWT
│   ├── deps.py                # dependencies compartidas (get_db, get_current_user, 
│   │                             require_role)
│   └── database.py            # engine, sessionmaker
├── sync/                      # módulo aparte para resolución de sincronización 
│   │                             offline de la app móvil (todavía vacío, solo 
│   │                             crear el paquete con un README explicando su 
│   │                             propósito)
├── tests/
│   ├── conftest.py            # fixtures: cliente de test, DB de test 
│   │                             (usar una base separada o transacciones 
│   │                             con rollback, no la DB de desarrollo)
│   └── (tests se agregan por módulo)
└── main.py

Requerimientos específicos de esta tarea:

1. Configuración por entorno (.env) usando pydantic-settings: 
   DATABASE_URL, JWT_SECRET, JWT_EXPIRATION_MINUTES, ENVIRONMENT
2. Conexión a PostgreSQL con SQLAlchemy async si es viable (asyncpg) — 
   si preferís sync por simplicidad, decime el trade-off antes de decidir 
   vos solo, porque afecta todo el resto del proyecto
3. Versionado de API bajo /api/v1/ desde el día uno — endpoints nuevos 
   siempre van dentro de v1 hasta que exista una razón real de romper 
   compatibilidad
4. core/deps.py debe incluir:
   - get_db(): sesión de base de datos
   - get_current_user(): decodifica JWT y devuelve el usuario autenticado
   - require_role(*roles): dependency factory que restringe un endpoint 
     a ciertos roles (los roles válidos son: "recolector", 
     "responsable_acopio", "operador_planta", "administrador" — 
     definilo como Enum de Python, no como strings sueltos)
5. Endpoint de salud: GET /health, sin autenticación, para monitoreo
6. Endpoint base de auth: POST /api/v1/auth/login, que reciba username 
   + credencial (pin o password) y devuelva un JWT. No implementes 
   todavía el modelo de usuario completo (eso es tarea aparte) — para 
   este endpoint podés dejar un TODO claro de dónde se conecta con el 
   modelo real
7. Manejo de errores centralizado: un exception handler que devuelva 
   respuestas JSON consistentes (no el HTML default de FastAPI) para 
   404, 401, 403, 409, 422 y 500
8. CORS configurado para permitir el origen del dashboard (dejalo como 
   variable de entorno, no hardcodeado)
9. Migraciones de Alembic configuradas y funcionando (alembic init, 
   conectado al mismo DATABASE_URL de core/config.py) — incluí la 
   migración inicial vacía para confirmar que corre
10. requirements.txt o pyproject.toml (preguntame cuál preferís si no 
    es obvio por el resto del proyecto) con todas las dependencias fijadas

Restricciones importantes:
- No implementes modelos de negocio (usuarios, lotes, etc.) en esta tarea — 
  eso viene en prompts separados. Esta tarea es solo el esqueleto.
- No inventes convenciones nuevas de nombres de carpetas — respetá 
  exactamente la estructura de arriba.
- Si algo del stack (ej. sync vs async SQLAlchemy) tiene un trade-off 
  importante, preguntame antes de decidir en silencio.
- Al terminar, mostrame cómo correr el proyecto localmente (comando exacto) 
  y cómo correr los tests.