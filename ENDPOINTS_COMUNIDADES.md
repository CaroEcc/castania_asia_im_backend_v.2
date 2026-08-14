# Endpoints: Comunidades

**Base URL:** `/api/v1/comunidades`

## Autenticación

Todos los endpoints requieren un JWT en el header `Authorization`:

```
Authorization: Bearer <token>
```

El token se obtiene en `POST /api/v1/auth/login`. Sin token válido todos los endpoints devuelven `401 Unauthorized`.

### Política de roles por operación

| Operación | Rol requerido |
|---|---|
| `GET /` `GET /select` `GET /stats` `GET /{id}` | Cualquier rol autenticado |
| `POST /` `PUT /{id}` `PATCH /{id}/status` `DELETE /{id}` | Solo `administrador` |

Intentar una operación de escritura con un rol distinto devuelve `403 Forbidden`.

---

## Modelos de datos

### ComunidadOut (response estándar)

```json
{
  "id_comunidad": 1,
  "nombre": "Comunidad San Pedro",
  "abreviacion": "CSP",
  "status": "Activa"
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id_comunidad` | `int` | ID autogenerado |
| `nombre` | `string` | Nombre completo (1–500 caracteres) |
| `abreviacion` | `string` | Código corto (1–50 caracteres) |
| `status` | `string` | `"Activa"` o `"Inactiva"` |

---

## Endpoints

### 1. Crear comunidad

**`POST /api/v1/comunidades`** — `administrador`

#### Request body

```json
{
  "nombre": "Comunidad San Pedro",
  "abreviacion": "CSP"
}
```

| Campo | Tipo | Requerido | Restricciones |
|---|---|---|---|
| `nombre` | `string` | Sí | 1–500 caracteres, único |
| `abreviacion` | `string` | Sí | 1–50 caracteres, única |

#### Response `201 Created`

```json
{
  "id_comunidad": 1,
  "nombre": "Comunidad San Pedro",
  "abreviacion": "CSP",
  "status": "Activa"
}
```

#### Errores

| Código | Causa |
|---|---|
| `401 Unauthorized` | Token ausente o inválido |
| `403 Forbidden` | El usuario autenticado no tiene rol `administrador` |
| `409 Conflict` | Ya existe una comunidad con ese `nombre` o esa `abreviacion` |
| `422 Unprocessable Entity` | Campos inválidos (longitud, tipos) |

---

### 2. Listar comunidades

**`GET /api/v1/comunidades`** — cualquier rol autenticado

#### Query params

| Param | Tipo | Default | Descripción |
|---|---|---|---|
| `page` | `int` | `1` | Número de página (≥ 1) |
| `page_size` | `int` | `10` | Resultados por página (1–100) |
| `status` | `string` | — | Filtrar por `"Activa"` o `"Inactiva"` |
| `search` | `string` | — | Búsqueda parcial en `nombre` o `abreviacion` (case-insensitive) |

#### Ejemplos

```
GET /api/v1/comunidades
GET /api/v1/comunidades?status=Activa
GET /api/v1/comunidades?search=san&page=1&page_size=20
```

#### Response `200 OK`

```json
{
  "total": 42,
  "page": 1,
  "page_size": 10,
  "comunidades": [
    {
      "id_comunidad": 1,
      "nombre": "Comunidad San Pedro",
      "abreviacion": "CSP",
      "status": "Activa"
    }
  ]
}
```

#### Errores

| Código | Causa |
|---|---|
| `401 Unauthorized` | Token ausente o inválido |
| `422 Unprocessable Entity` | `status` con valor distinto de `"Activa"` / `"Inactiva"` |

---

### 3. Lista para dropdown (select)

**`GET /api/v1/comunidades/select`** — cualquier rol autenticado

Devuelve solo las comunidades **Activas**, en formato mínimo para poblar un `<select>` o `Picker`. Siempre ordenado alfabéticamente.

#### Response `200 OK`

```json
[
  {
    "value": 1,
    "label": "Comunidad San Pedro",
    "abreviacion": "CSP"
  },
  {
    "value": 2,
    "label": "Comunidad Villa Florida",
    "abreviacion": "CVF"
  }
]
```

---

### 4. Estadísticas

**`GET /api/v1/comunidades/stats`** — cualquier rol autenticado

#### Response `200 OK`

```json
{
  "total_comunidades": 42,
  "comunidades_activas": 38,
  "comunidades_inactivas": 4
}
```

---

### 5. Obtener comunidad por ID

**`GET /api/v1/comunidades/{comunidad_id}`** — cualquier rol autenticado

#### Path params

| Param | Tipo | Descripción |
|---|---|---|
| `comunidad_id` | `int` | ID de la comunidad |

#### Response `200 OK`

```json
{
  "id_comunidad": 1,
  "nombre": "Comunidad San Pedro",
  "abreviacion": "CSP",
  "status": "Activa"
}
```

#### Errores

| Código | Causa |
|---|---|
| `401 Unauthorized` | Token ausente o inválido |
| `404 Not Found` | No existe una comunidad con ese ID |

---

### 6. Actualizar comunidad

**`PUT /api/v1/comunidades/{comunidad_id}`** — `administrador`

Todos los campos del body son opcionales. Solo se actualiza lo que se envía.

#### Path params

| Param | Tipo | Descripción |
|---|---|---|
| `comunidad_id` | `int` | ID de la comunidad a actualizar |

#### Request body

```json
{
  "nombre": "Comunidad San Pedro del Norte",
  "abreviacion": "CSPN",
  "status": "Inactiva"
}
```

| Campo | Tipo | Requerido | Restricciones |
|---|---|---|---|
| `nombre` | `string` | No | 1–500 caracteres, único |
| `abreviacion` | `string` | No | 1–50 caracteres, única |
| `status` | `string` | No | `"Activa"` o `"Inactiva"` |

#### Response `200 OK`

Devuelve la comunidad con los datos actualizados (mismo formato que `ComunidadOut`).

#### Errores

| Código | Causa |
|---|---|
| `401 Unauthorized` | Token ausente o inválido |
| `403 Forbidden` | El usuario autenticado no tiene rol `administrador` |
| `404 Not Found` | No existe una comunidad con ese ID |
| `409 Conflict` | El nuevo `nombre` o `abreviacion` ya lo usa otra comunidad |
| `422 Unprocessable Entity` | `status` con valor inválido |

---

### 7. Cambiar status (activar / desactivar)

**`PATCH /api/v1/comunidades/{comunidad_id}/status?activar=true`** — `administrador`

Operación idempotente: si la comunidad ya tiene el status solicitado, no se modifica y se devuelve tal cual.

#### Path params

| Param | Tipo | Descripción |
|---|---|---|
| `comunidad_id` | `int` | ID de la comunidad |

#### Query params

| Param | Tipo | Requerido | Descripción |
|---|---|---|---|
| `activar` | `bool` | Sí | `true` → pone en `"Activa"` / `false` → pone en `"Inactiva"` |

#### Ejemplos

```
PATCH /api/v1/comunidades/5/status?activar=false   # desactivar
PATCH /api/v1/comunidades/5/status?activar=true    # reactivar
```

#### Response `200 OK`

Devuelve la comunidad con el status actualizado (mismo formato que `ComunidadOut`).

#### Errores

| Código | Causa |
|---|---|
| `401 Unauthorized` | Token ausente o inválido |
| `403 Forbidden` | El usuario autenticado no tiene rol `administrador` |
| `404 Not Found` | No existe una comunidad con ese ID |
| `422 Unprocessable Entity` | Falta el query param `activar` |

---

### 8. Eliminar comunidad (soft delete)

**`DELETE /api/v1/comunidades/{comunidad_id}`** — `administrador`

**No elimina el registro físicamente.** Cambia el status a `"Inactiva"`. La comunidad sigue existiendo en la base de datos y puede reactivarse con el endpoint de status.

#### Path params

| Param | Tipo | Descripción |
|---|---|---|
| `comunidad_id` | `int` | ID de la comunidad a eliminar |

#### Response `200 OK`

Devuelve la comunidad con `"status": "Inactiva"` (mismo formato que `ComunidadOut`).

#### Errores

| Código | Causa |
|---|---|
| `401 Unauthorized` | Token ausente o inválido |
| `403 Forbidden` | El usuario autenticado no tiene rol `administrador` |
| `404 Not Found` | No existe una comunidad con ese ID |
| `409 Conflict` | La comunidad ya está en estado `"Inactiva"` |

---

## Resumen de respuestas de error

Todos los errores devuelven JSON con esta forma:

```json
{
  "detail": "Mensaje descriptivo del error",
  "status_code": 409
}
```

| Código | Cuándo ocurre |
|---|---|
| `401 Unauthorized` | Token ausente, expirado o inválido |
| `403 Forbidden` | Token válido pero el rol no tiene permiso |
| `404 Not Found` | ID no existe en la base de datos |
| `409 Conflict` | Violación de unicidad o estado ya aplicado |
| `422 Unprocessable Entity` | Datos del body o query params inválidos |
| `500 Internal Server Error` | Error inesperado del servidor |
