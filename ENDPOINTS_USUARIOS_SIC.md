# Documentación de Endpoints — Usuarios SIC
**Sembrando Datos v2.0 / ACEAA — Sistema Interno de Control**

---

## Tabla de contenidos

1. [Modelo de datos](#1-modelo-de-datos)
2. [Sistema de roles y autenticación](#2-sistema-de-roles-y-autenticación)
3. [Autenticación — `POST /auth/token`](#3-autenticación--post-authtoken)
4. [Listar usuarios — `GET /usuarios`](#4-listar-usuarios--get-usuarios)
5. [Obtener usuario — `GET /usuarios/{id}`](#5-obtener-usuario--get-usuariosid)
6. [Crear usuario — `POST /usuarios`](#6-crear-usuario--post-usuarios)
7. [Actualizar usuario — `PUT /usuarios/{id}`](#7-actualizar-usuario--put-usuariosid)
8. [Cambiar estado — `PATCH /usuarios/{id}/estado`](#8-cambiar-estado--patch-usuariosidestado)
9. [Resetear credencial — `POST /usuarios/{id}/reset-credencial`](#9-resetear-credencial--post-usuariosidresset-credencial)
10. [Códigos de error de referencia](#10-códigos-de-error-de-referencia)
11. [Flujo completo de ejemplo](#11-flujo-completo-de-ejemplo)

---

## 1. Modelo de datos

Tabla: **`usuarios_sistema`** — separada de `usuarios` (app móvil de inteligencia de mercados).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Clave primaria, generado automáticamente |
| `nombre_completo` | string | Nombre y apellido del usuario |
| `username` | string | Identificador único de login |
| `rol` | enum | Ver tabla de roles abajo |
| `metodo_auth` | enum `pin` \| `password` | Calculado automáticamente por el backend según el rol. **Nunca viene del cliente.** |
| `credencial_hash` | string | Hash bcrypt de la credencial. **Nunca se expone en ningún response.** |
| `comunidad` | string \| null | Comunidad de origen (relevante para recolectores) |
| `activo` | bool | Estado del usuario. `false` = desactivado (soft delete) |
| `fecha_creacion` | datetime | UTC, asignado automáticamente |
| `creado_por` | UUID \| null | ID del administrador que dio de alta al usuario (auditoría) |

---

## 2. Sistema de roles y autenticación

El método de autenticación se asigna automáticamente según el rol. El cliente **nunca** envía `metodo_auth`.

| Rol | Método auth | Credencial | Descripción |
|-----|-------------|------------|-------------|
| `recolector` | `pin` | PIN 6 dígitos | Recolector silvestre de campo |
| `responsable_acopio` | `password` | Password libre | Responsable de punto de acopio |
| `operador_planta` | `password` | Password libre | Operador de planta — cubre Área B y C (antes: `jefe_planta` + `encargado_camara`) |
| `administrador` | `password` | Password libre | Acceso completo al sistema |

> **Seguridad de PIN:** aunque sea solo 6 dígitos numéricos, el PIN pasa por bcrypt igual que cualquier password. Nunca se almacena en texto plano.

### Variable de entorno requerida

Agregar al `.env` antes de producción:

```env
SECRET_KEY=tu-clave-secreta-larga-y-aleatoria
```

Los tokens JWT expiran a las **8 horas**.

---

## 3. Autenticación — `POST /auth/token`

Obtiene un JWT Bearer para usar en endpoints protegidos. Funciona igual para roles PIN y roles password.

**No requiere autenticación previa.**

### Request

```
POST /auth/token
Content-Type: application/json
```

```json
{
  "username": "german.gongora",
  "credencial": "123456"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `username` | string | Sí | Username del usuario |
| `credencial` | string | Sí | PIN (6 dígitos) o password, según el rol |

### Response `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "rol": "recolector",
  "nombre_completo": "German Góngora Soliz"
}
```

| Campo | Descripción |
|-------|-------------|
| `access_token` | JWT firmado con HS256, expira en 8 horas |
| `token_type` | Siempre `"bearer"` |
| `rol` | Rol del usuario autenticado |
| `nombre_completo` | Nombre para mostrar en el frontend |

### Errores

| Código | Causa |
|--------|-------|
| `401` | Username no existe, credencial incorrecta, o usuario inactivo |

### Uso del token

En todos los endpoints que requieren autenticación, incluir el header:

```
Authorization: Bearer <access_token>
```

---

## 4. Listar usuarios — `GET /usuarios`

Lista paginada de usuarios del sistema con filtros opcionales.

**No requiere autenticación** (endpoint de consulta abierto — restringir en producción si se necesita).

### Request

```
GET /usuarios?rol=recolector&activo=true&page=1&page_size=20
```

| Query param | Tipo | Requerido | Descripción |
|-------------|------|-----------|-------------|
| `rol` | enum | No | Filtrar por rol: `recolector`, `responsable_acopio`, `operador_planta`, `administrador` |
| `activo` | bool | No | Filtrar por estado: `true` o `false` |
| `page` | int ≥ 1 | No | Página (default: `1`) |
| `page_size` | int 1–100 | No | Registros por página (default: `20`) |

### Response `200 OK`

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "nombre_completo": "German Góngora Soliz",
    "username": "german.gongora",
    "rol": "recolector",
    "metodo_auth": "pin",
    "comunidad": "Villa Fátima",
    "activo": true,
    "fecha_creacion": "2026-08-11T14:30:00",
    "creado_por": "f0e1d2c3-b4a5-6789-0123-456789abcdef"
  }
]
```

> `credencial_hash` **nunca aparece** en este ni en ningún otro response.

---

## 5. Obtener usuario — `GET /usuarios/{id}`

Retorna los datos de un usuario por su UUID.

**No requiere autenticación.**

### Request

```
GET /usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Response `200 OK`

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nombre_completo": "German Góngora Soliz",
  "username": "german.gongora",
  "rol": "recolector",
  "metodo_auth": "pin",
  "comunidad": "Villa Fátima",
  "activo": true,
  "fecha_creacion": "2026-08-11T14:30:00",
  "creado_por": "f0e1d2c3-b4a5-6789-0123-456789abcdef"
}
```

### Errores

| Código | Causa |
|--------|-------|
| `404` | UUID no existe en la base de datos |

---

## 6. Crear usuario — `POST /usuarios`

Crea un nuevo usuario del sistema. **Solo accesible para el rol `administrador`.**

El backend determina automáticamente el `metodo_auth` y, para roles PIN, genera el PIN si no se envía uno.

### Request

```
POST /usuarios
Authorization: Bearer <token_administrador>
Content-Type: application/json
```

#### Caso A — Crear recolector (rol PIN, sin PIN propio)

```json
{
  "nombre_completo": "German Góngora Soliz",
  "username": "german.gongora",
  "rol": "recolector",
  "comunidad": "Villa Fátima"
}
```

El backend genera un PIN aleatorio de 6 dígitos.

#### Caso B — Crear recolector con PIN propio

```json
{
  "nombre_completo": "Ana Quispe",
  "username": "ana.quispe",
  "rol": "recolector",
  "credencial": "987654"
}
```

#### Caso C — Crear usuario con password

```json
{
  "nombre_completo": "Jorge Mamani",
  "username": "jorge.mamani",
  "rol": "operador_planta",
  "credencial": "MiPassword2026"
}
```

Para roles `responsable_acopio`, `operador_planta` y `administrador`, el campo `credencial` es **obligatorio**.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre_completo` | string (2–200) | Sí | Nombre completo |
| `username` | string (3–100) | Sí | Debe ser único en el sistema |
| `rol` | enum | Sí | Ver tabla de roles |
| `comunidad` | string (máx. 200) | No | Comunidad de origen |
| `credencial` | string | Condicional | Obligatorio para roles password. Opcional para roles PIN (si se omite, el backend genera uno) |

### Response `201 Created`

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nombre_completo": "German Góngora Soliz",
  "username": "german.gongora",
  "rol": "recolector",
  "metodo_auth": "pin",
  "comunidad": "Villa Fátima",
  "activo": true,
  "fecha_creacion": "2026-08-11T14:30:00",
  "creado_por": "f0e1d2c3-b4a5-6789-0123-456789abcdef",
  "pin_generado": "472819"
}
```

> **`pin_generado`** solo aparece en la respuesta del `POST /usuarios`.
> Para roles password vale `null`.
> **Una vez que el administrador cierra esta respuesta, el PIN no se puede recuperar nunca más.**
> El administrador es responsable de comunicárselo al recolector en ese momento.

### Errores

| Código | Causa |
|--------|-------|
| `401` | Token ausente o inválido |
| `403` | El usuario autenticado no tiene rol `administrador` |
| `409` | El `username` ya existe en la base de datos |
| `422` | Rol password sin `credencial`, o campos con formato inválido |

---

## 7. Actualizar usuario — `PUT /usuarios/{id}`

Actualiza `nombre_completo` y/o `comunidad`. **No permite cambiar `rol`, `username`, ni `metodo_auth`.**

**No requiere autenticación** (agregar protección según política del proyecto).

### Request

```
PUT /usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890
Content-Type: application/json
```

```json
{
  "nombre_completo": "German Góngora Soliz Actualizado",
  "comunidad": "Puerto Nuevo"
}
```

Todos los campos son opcionales. Solo se actualiza lo que se envía.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre_completo` | string (2–200) | No | Nuevo nombre completo |
| `comunidad` | string (máx. 200) | No | Nueva comunidad |

### Response `200 OK`

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nombre_completo": "German Góngora Soliz Actualizado",
  "username": "german.gongora",
  "rol": "recolector",
  "metodo_auth": "pin",
  "comunidad": "Puerto Nuevo",
  "activo": true,
  "fecha_creacion": "2026-08-11T14:30:00",
  "creado_por": "f0e1d2c3-b4a5-6789-0123-456789abcdef"
}
```

### Errores

| Código | Causa |
|--------|-------|
| `404` | UUID no existe |
| `422` | Campos con formato inválido (ej. `nombre_completo` vacío) |

---

## 8. Cambiar estado — `PATCH /usuarios/{id}/estado`

Activa o desactiva un usuario. **No hay eliminación física** — los usuarios inactivos permanecen en la base de datos para preservar la trazabilidad de lotes y entregas.

**No requiere autenticación** (agregar protección según política del proyecto).

### Request

```
PATCH /usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890/estado
Content-Type: application/json
```

```json
{
  "activo": false
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `activo` | bool | Sí | `true` = activar, `false` = desactivar |

### Response `200 OK`

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nombre_completo": "German Góngora Soliz",
  "username": "german.gongora",
  "rol": "recolector",
  "metodo_auth": "pin",
  "comunidad": "Villa Fátima",
  "activo": false,
  "fecha_creacion": "2026-08-11T14:30:00",
  "creado_por": "f0e1d2c3-b4a5-6789-0123-456789abcdef"
}
```

> Un usuario con `activo: false` no puede iniciar sesión — el endpoint `/auth/token` devuelve `401` para usuarios inactivos.

### Errores

| Código | Causa |
|--------|-------|
| `404` | UUID no existe |

---

## 9. Resetear credencial — `POST /usuarios/{id}/reset-credencial`

Genera una nueva credencial para el usuario. Es un endpoint independiente del `PUT` porque es una acción sensible de seguridad.

**El comportamiento difiere según el `metodo_auth` del usuario:**
- **Rol PIN** (`recolector`): el backend genera un nuevo PIN de 6 dígitos automáticamente. El body puede enviarse vacío.
- **Rol password**: el cuerpo debe incluir `nueva_credencial`. El backend la hashea y la guarda.

**No requiere autenticación** (agregar protección según política del proyecto — idealmente solo administrador).

### Request — Rol PIN

```
POST /usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890/reset-credencial
Content-Type: application/json
```

```json
{}
```

### Request — Rol password

```json
{
  "nueva_credencial": "NuevaPasswordSegura2026"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nueva_credencial` | string | Solo para roles password | Nueva contraseña. Se ignora para roles PIN. |

### Response `200 OK` — Rol PIN

```json
{
  "mensaje": "Credencial actualizada exitosamente",
  "pin_generado": "839201"
}
```

### Response `200 OK` — Rol password

```json
{
  "mensaje": "Credencial actualizada exitosamente",
  "pin_generado": null
}
```

> Al igual que en la creación, el `pin_generado` solo está disponible en esta respuesta. El administrador debe comunicárselo al usuario de inmediato.

### Errores

| Código | Causa |
|--------|-------|
| `404` | UUID no existe |
| `422` | Rol password y `nueva_credencial` no enviada |

---

## 10. Códigos de error de referencia

| Código HTTP | Significado en este sistema |
|-------------|----------------------------|
| `200` | Operación exitosa |
| `201` | Usuario creado exitosamente |
| `401` | Token ausente, inválido o expirado / credenciales de login incorrectas |
| `403` | Autenticado pero sin permisos para esa acción (solo admin puede crear usuarios) |
| `404` | UUID no encontrado en la base de datos |
| `409` | Conflicto: el `username` ya está en uso |
| `422` | Datos de entrada inválidos (campos obligatorios faltantes, tipos incorrectos, reglas de negocio) |

---

## 11. Flujo completo de ejemplo

### Escenario: El administrador da de alta a un nuevo recolector antes de la zafra

**Paso 1 — El administrador se autentica:**

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin.ofacc", "credencial": "AdminPass2026"}'
```

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "rol": "administrador",
  "nombre_completo": "Administrador OFACC"
}
```

**Paso 2 — Crea el recolector:**

```bash
curl -X POST http://localhost:8000/usuarios \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_completo": "German Góngora Soliz",
    "username": "german.gongora",
    "rol": "recolector",
    "comunidad": "Villa Fátima"
  }'
```

Respuesta:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nombre_completo": "German Góngora Soliz",
  "username": "german.gongora",
  "rol": "recolector",
  "metodo_auth": "pin",
  "comunidad": "Villa Fátima",
  "activo": true,
  "fecha_creacion": "2026-08-11T14:30:00",
  "creado_por": "f0e1d2c3-b4a5-6789-0123-456789abcdef",
  "pin_generado": "472819"
}
```

> El administrador anota el PIN `472819` y se lo entrega a German en persona. Después de esto, el PIN no se puede recuperar.

**Paso 3 — German se autentica con su PIN:**

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "german.gongora", "credencial": "472819"}'
```

**Paso 4 — Al finalizar la zafra, se desactiva el usuario temporalmente:**

```bash
curl -X PATCH http://localhost:8000/usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890/estado \
  -H "Content-Type: application/json" \
  -d '{"activo": false}'
```

**Paso 5 — Al inicio de la próxima zafra, se reactiva y se resetea el PIN:**

```bash
# Reactivar
curl -X PATCH http://localhost:8000/usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890/estado \
  -H "Content-Type: application/json" \
  -d '{"activo": true}'

# Nuevo PIN
curl -X POST http://localhost:8000/usuarios/a1b2c3d4-e5f6-7890-abcd-ef1234567890/reset-credencial \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Documentación interactiva

Con el servidor corriendo, la documentación Swagger completa está disponible en:

```
http://localhost:8000/docs
```

Permite probar cada endpoint directamente desde el navegador con autenticación Bearer integrada.
