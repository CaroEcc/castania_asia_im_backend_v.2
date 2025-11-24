# API Inteligencia de Mercados - Castaña y Asaí

Sistema de Inteligencia de Mercados que calcula precios justos para productores de Castaña y Asaí en Bolivia.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic
```

### 2. Configurar Base de Datos

Editar el archivo `.env` con la URL de conexión a PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:password@host/database
```

### 3. Ejecutar el Servidor

```bash
# Modo desarrollo (con hot reload)
uvicorn app.main:app --reload

# Modo producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

### 4. Probar el Endpoint

```bash
# Ejecutar tests automatizados
python test_precio_justo.py

# O hacer un request manual
curl -X POST "http://localhost:8000/precio-justo/calcular" \
  -H "Content-Type: application/json" \
  -d '{
    "zona": "Norte amazónico",
    "costo_transporte_castana": 15.50,
    "tipo_castana": "Orgánico",
    "tiempo_recoleccion_castana": 5,
    "tiempo_venta_castana": 10
  }'
```

---

## 📊 Estructura del Proyecto

```
backend-castania-asai/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app y configuración
│   ├── database.py                  # Configuración de SQLAlchemy
│   ├── models.py                    # Modelos de base de datos
│   ├── schemas.py                   # Schemas Pydantic
│   ├── routes/
│   │   ├── reports.py              # Endpoints de reportes
│   │   └── precio_justo.py         # Endpoint Precio Justo ⭐
│   └── services/
│       └── precio_justo_service.py # Lógica de cálculo ⭐
├── .env                            # Variables de entorno
├── requirements.txt                # Dependencias
├── test_precio_justo.py           # Tests del endpoint ⭐
├── DOCUMENTACION_FORMULARIO.md    # Documentación del formulario (52 campos)
├── FIELD_MAPPING.md               # Mapeo de campos formulario → BD
├── MIGRATION_GUIDE.md             # Guía de migración SQL
├── ENDPOINT_PRECIO_JUSTO.md       # Documentación del endpoint ⭐
└── README.md                       # Este archivo
```

---

## 🎯 Endpoints Principales

### 1. Calcular Precio Justo
**POST** `/precio-justo/calcular`

Calcula el Precio Justo para Castaña y/o Asaí basándose en:
- Zona del usuario
- Costos de transporte
- Calidad del producto (certificación, frescura, deterioro)
- Variables maestras del sistema (precios promedio en planta)

**Documentación completa:** Ver [ENDPOINT_PRECIO_JUSTO.md](ENDPOINT_PRECIO_JUSTO.md)

**Ejemplo de respuesta:**
```json
{
  "castana": {
    "precio_justo": 125.40,
    "precio_minimo_zona": 95.00,
    "mensaje": "Tu Precio Justo para Castaña es 125.40 Bs. El precio mínimo observado en tu zona es 95.00 Bs."
  }
}
```

### 2. Variables Maestras del Sistema
**GET** `/precio-justo/variables-maestras`

Retorna los precios promedio en planta y parámetros del sistema.

### 3. Crear Reporte
**POST** `/reportes`

Guarda un reporte completo del formulario (52 campos).

### 4. Listar Reportes
**GET** `/reportes`

Lista todos los reportes guardados.

---

## 📐 Fórmulas del Precio Justo

### Castaña
```
PJ_Castaña = P_Base_Ajustado_C + Bono_Certificacion_C + Ajuste_Deterioro_C

Donde:
- P_Base_Ajustado_C = P_Prom_Planta_C - Costo_Transporte
- Bono_Certificacion_C = +0.40 Bs si es Orgánico
- Ajuste_Deterioro_C = Penalidad si >20 días (-0.50 Bs/día)
```

### Asaí
```
PJ_Asai = P_Base_Ajustado_A + Bono_Frescura_A + Bono_Certificacion_A

Donde:
- P_Base_Ajustado_A = P_Prom_Planta_A - Costo_Transporte
- Bono_Frescura_A = +10 Bs (<24h), +7 Bs (24-48h), +3 Bs (48-72h)
- Bono_Certificacion_A = +5.00 Bs si es Orgánico
```

**Referencia:** [app/formula_aplicar.md](app/formula_aplicar.md)

---

## 🗄️ Base de Datos

### Modelos Principales

1. **Usuario** (11 campos)
   - Sección 0: Identificación (P1-P7)
   - Nombre, rubro, actividades, género, edad, zona, GPS

2. **Reporte** (45 campos)
   - Sección 1: Precios (P8-P14)
   - Sección 2: Calidad (P15-P19)
   - Sección 3: Transporte (P22)
   - Sección 4: Mercados Grandes (P23-P25)
   - Sección 5: Feedback y Clima (P26-P27)

3. **PrecioReferencia** (tabla de apoyo)
4. **Alerta** (sistema de alertas)
5. **Boletin** (boletines informativos)

**Mapeo completo:** Ver [FIELD_MAPPING.md](FIELD_MAPPING.md)

### Migración

Si ya tienes una base de datos, ejecuta la migración:

```bash
# Ver guía detallada
cat MIGRATION_GUIDE.md

# O recrear desde cero (DESARROLLO)
python -c "from app.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

---

## 📚 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Aquí puedes:
- Ver todos los endpoints
- Probar requests directamente
- Ver schemas completos
- Descargar OpenAPI spec

---

## 🧪 Testing

### Tests Automatizados

```bash
# Ejecutar todos los tests
python test_precio_justo.py
```

### Tests Manuales

```bash
# Test 1: Castaña
curl -X POST "http://localhost:8000/precio-justo/calcular" \
  -H "Content-Type: application/json" \
  -d '{"zona": "Norte amazónico", "costo_transporte_castana": 15.50, "tipo_castana": "Orgánico", "tiempo_recoleccion_castana": 5, "tiempo_venta_castana": 10}'

# Test 2: Asaí
curl -X POST "http://localhost:8000/precio-justo/calcular" \
  -H "Content-Type: application/json" \
  -d '{"zona": "Norte amazónico", "costo_transporte_asai": 8.00, "tipo_asai": "Silvestre", "tiempo_cosecha_asai": 20}'

# Test 3: Variables Maestras
curl "http://localhost:8000/precio-justo/variables-maestras"
```

---

## 🔧 Configuración de Parámetros

Los parámetros del sistema se pueden ajustar en:

**Archivo:** `app/services/precio_justo_service.py`

```python
class PrecioJustoService:
    # CASTAÑA
    PARAM_BONO_ORGANICO_C_BS = Decimal("0.40")
    PARAM_UMBRAL_DIAS_C = 20
    PARAM_PENALIDAD_DIA_C_BS = Decimal("0.5")

    # ASAÍ
    PARAM_BONO_ORGANICO_A_BS = Decimal("5.0")
    PARAM_BONO_ASAI_FR94_BS = Decimal("10.0")
    PARAM_BONO_ASAI_FR90_BS = Decimal("7.0")
    PARAM_BONO_ASAI_FR85_BS = Decimal("3.0")
```

---

## 🌐 Integración con Frontend

### React Native / Expo

```typescript
import { API_BASE_URL } from './config';

async function calcularPrecioJusto(formData) {
  const response = await fetch(`${API_BASE_URL}/precio-justo/calcular`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      zona: formData.zona,
      costo_transporte_castana: formData.costo_transporte_castana,
      tipo_castana: formData.tipo_castana,
      tiempo_recoleccion_castana: formData.tiempo_recoleccion_castana,
      tiempo_venta_castana: formData.tiempo_venta_castana,
    }),
  });

  const data = await response.json();

  // Mostrar mensaje al usuario
  if (data.castana) {
    Alert.alert('Precio Justo', data.castana.mensaje);
  }
}
```

**Ver ejemplo completo:** [ENDPOINT_PRECIO_JUSTO.md - Integración con Frontend](ENDPOINT_PRECIO_JUSTO.md#integración-con-el-frontend)

---

## 📝 Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:password@host:5432/database

# Opcional: Configuraciones adicionales
DEBUG=True
LOG_LEVEL=INFO
```

---

## 🚨 Troubleshooting

### Error: No se puede conectar a la base de datos
```
SQLSTATE[08006] Unable to connect to database
```
**Solución:** Verificar que PostgreSQL esté corriendo y que la URL en `.env` sea correcta.

### Error: Módulo no encontrado
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solución:** Instalar dependencias: `pip install -r requirements.txt`

### Error: Precio Justo = 0
```json
{"castana": {"precio_justo": 0.00, ...}}
```
**Solución:** El sistema necesita datos históricos. Crear reportes con `nodo_precio = "En planta procesadora"` para alimentar las variables maestras.

---

## 📄 Licencia

Este proyecto es parte del sistema de Inteligencia de Mercados para productores de Castaña y Asaí en Bolivia.

---

## 👥 Contacto

Para preguntas o soporte técnico, contactar al equipo de desarrollo.

---

**Versión:** 2.0.0
**Última actualización:** 2025-11-22
