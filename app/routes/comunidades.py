# app/routes/comunidades.py
"""
Endpoints CRUD para administrar comunidades
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import schemas
from app.core.deps import get_db
from app.models import Comunidad

router = APIRouter(prefix="/comunidades", tags=["Comunidades"])


# =============================================================================
# CREATE - Crear nueva comunidad
# =============================================================================

@router.post("/", response_model=schemas.ComunidadOut, status_code=201)
def crear_comunidad(
    comunidad: schemas.ComunidadCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva comunidad.

    **Campos requeridos:**
    - `nombre`: Nombre completo de la comunidad (1-500 caracteres)
    - `abreviacion`: Abreviación de la comunidad (1-50 caracteres)

    **Ejemplo:**
    ```json
    {
      "nombre": "Comunidad San Pedro",
      "abreviacion": "CSP"
    }
    ```

    **Retorna:** La comunidad creada con su ID y status "Activa"
    """
    # Verificar si ya existe una comunidad con el mismo nombre
    comunidad_existente = db.query(Comunidad).filter(
        Comunidad.nombre == comunidad.nombre
    ).first()

    if comunidad_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una comunidad con el nombre '{comunidad.nombre}'"
        )

    # Verificar si ya existe una comunidad con la misma abreviación
    abreviacion_existente = db.query(Comunidad).filter(
        Comunidad.abreviacion == comunidad.abreviacion
    ).first()

    if abreviacion_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una comunidad con la abreviación '{comunidad.abreviacion}'"
        )

    # Crear nueva comunidad
    nueva_comunidad = Comunidad(
        nombre=comunidad.nombre,
        abreviacion=comunidad.abreviacion,
        status="Activa"  # Por defecto activa
    )

    db.add(nueva_comunidad)
    db.commit()
    db.refresh(nueva_comunidad)

    return nueva_comunidad


# =============================================================================
# READ - Listar todas las comunidades (con paginación y filtros)
# =============================================================================

@router.get("/", response_model=schemas.ComunidadListResponse)
def listar_comunidades(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página (máx 100)"),
    status: Optional[str] = Query(None, description="Filtrar por status: 'Activa' o 'Inactiva'"),
    search: Optional[str] = Query(None, description="Buscar por nombre o abreviación"),
    db: Session = Depends(get_db)
):
    """
    Lista todas las comunidades con paginación y filtros opcionales.

    **Query Parameters:**
    - `page`: Número de página (default: 1)
    - `page_size`: Tamaño de página (default: 10, máx: 100)
    - `status`: Filtrar por status ("Activa" o "Inactiva")
    - `search`: Buscar en nombre o abreviación (case-insensitive)

    **Ejemplos:**
    - `/comunidades?page=1&page_size=20`
    - `/comunidades?status=Activa`
    - `/comunidades?search=San`

    **Retorna:** Lista paginada de comunidades
    """
    # Construir query base
    query = db.query(Comunidad)

    # Filtro por status
    if status:
        if status not in ["Activa", "Inactiva"]:
            raise HTTPException(
                status_code=400,
                detail="El status debe ser 'Activa' o 'Inactiva'"
            )
        query = query.filter(Comunidad.status == status)

    # Filtro de búsqueda
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Comunidad.nombre.ilike(search_pattern)) |
            (Comunidad.abreviacion.ilike(search_pattern))
        )

    # Contar total de resultados
    total = query.count()

    # Aplicar paginación
    offset = (page - 1) * page_size
    comunidades = query.order_by(Comunidad.nombre).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "comunidades": comunidades
    }


# =============================================================================
# SELECT - Obtener comunidades para componente select (dropdown)
# =============================================================================

@router.get("/select", response_model=List[dict])
def obtener_comunidades_select(db: Session = Depends(get_db)):
    """
    Obtiene lista simplificada de comunidades para poblar un componente select/dropdown.

    **Query Parameters:**
    - `activas_solo`: Si es `true` (default), solo retorna comunidades activas

    **Retorna:** Array de objetos con estructura simple para select:
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

    **Uso en frontend:**
    ```typescript
    // React Native / Expo
    const [comunidades, setComunidades] = useState([]);

    useEffect(() => {
      fetch('https://api.ejemplo.com/comunidades/select')
        .then(res => res.json())
        .then(data => setComunidades(data));
    }, []);

    // Uso en Picker/Select
    <Picker
      selectedValue={selectedComunidad}
      onValueChange={(value) => setSelectedComunidad(value)}
    >
      {comunidades.map(com => (
        <Picker.Item key={com.value} label={com.label} value={com.value} />
      ))}
    </Picker>
    ```

    **Ordenamiento:** Por nombre alfabéticamente
    """
    # Construir query - solo comunidades activas
    query = db.query(Comunidad)
    query = query.filter(Comunidad.status == "1")

    # Obtener comunidades ordenadas por nombre
    comunidades = query.order_by(Comunidad.nombre).all()

    # Transformar a formato select
    return [
        {
            "value": com.id_comunidad,
            "label": com.nombre,
            "abreviacion": com.abreviacion
        }
        for com in comunidades
    ]


# =============================================================================
# READ - Obtener una comunidad por ID
# =============================================================================

@router.get("/{id_comunidad}", response_model=schemas.ComunidadOut)
def obtener_comunidad(
    id_comunidad: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una comunidad específica por su ID.

    **Path Parameter:**
    - `id_comunidad`: ID de la comunidad

    **Retorna:** Datos de la comunidad

    **Errores:**
    - `404`: Comunidad no encontrada
    """
    comunidad = db.query(Comunidad).filter(Comunidad.id_comunidad == id_comunidad).first()

    if not comunidad:
        raise HTTPException(
            status_code=404,
            detail=f"Comunidad con ID {id_comunidad} no encontrada"
        )

    return comunidad


# =============================================================================
# UPDATE - Actualizar una comunidad
# =============================================================================

@router.put("/{id_comunidad}", response_model=schemas.ComunidadOut)
def actualizar_comunidad(
    id_comunidad: int,
    comunidad_update: schemas.ComunidadUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una comunidad existente.

    **Path Parameter:**
    - `id_comunidad`: ID de la comunidad a actualizar

    **Body (todos opcionales):**
    - `nombre`: Nuevo nombre
    - `abreviacion`: Nueva abreviación
    - `status`: Nuevo status ("Activa" o "Inactiva")

    **Ejemplo:**
    ```json
    {
      "nombre": "Comunidad San Pedro del Norte",
      "abreviacion": "CSPN",
      "status": "Activa"
    }
    ```

    **Retorna:** La comunidad actualizada

    **Errores:**
    - `404`: Comunidad no encontrada
    - `400`: Nombre o abreviación ya existe en otra comunidad
    """
    # Buscar comunidad
    comunidad = db.query(Comunidad).filter(Comunidad.id_comunidad == id_comunidad).first()

    if not comunidad:
        raise HTTPException(
            status_code=404,
            detail=f"Comunidad con ID {id_comunidad} no encontrada"
        )

    # Validar y actualizar nombre
    if comunidad_update.nombre is not None:
        # Verificar si el nuevo nombre ya existe en otra comunidad
        nombre_existente = db.query(Comunidad).filter(
            Comunidad.nombre == comunidad_update.nombre,
            Comunidad.id_comunidad != id_comunidad
        ).first()

        if nombre_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otra comunidad con el nombre '{comunidad_update.nombre}'"
            )

        comunidad.nombre = comunidad_update.nombre

    # Validar y actualizar abreviación
    if comunidad_update.abreviacion is not None:
        # Verificar si la nueva abreviación ya existe en otra comunidad
        abreviacion_existente = db.query(Comunidad).filter(
            Comunidad.abreviacion == comunidad_update.abreviacion,
            Comunidad.id_comunidad != id_comunidad
        ).first()

        if abreviacion_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otra comunidad con la abreviación '{comunidad_update.abreviacion}'"
            )

        comunidad.abreviacion = comunidad_update.abreviacion

    # Validar y actualizar status
    if comunidad_update.status is not None:
        if comunidad_update.status not in ["Activa", "Inactiva"]:
            raise HTTPException(
                status_code=400,
                detail="El status debe ser 'Activa' o 'Inactiva'"
            )
        comunidad.status = comunidad_update.status

    db.commit()
    db.refresh(comunidad)

    return comunidad


# =============================================================================
# PATCH - Activar/Desactivar comunidad (cambio de status)
# =============================================================================

@router.patch("/{id_comunidad}/status", response_model=schemas.ComunidadOut)
def cambiar_status_comunidad(
    id_comunidad: int,
    activar: bool = Query(..., description="true para activar, false para desactivar"),
    db: Session = Depends(get_db)
):
    """
    Activa o desactiva una comunidad (soft delete).

    **Path Parameter:**
    - `id_comunidad`: ID de la comunidad

    **Query Parameter:**
    - `activar`: `true` para activar, `false` para desactivar

    **Ejemplos:**
    - `PATCH /comunidades/5/status?activar=false` (desactivar)
    - `PATCH /comunidades/5/status?activar=true` (activar)

    **Retorna:** La comunidad con el status actualizado

    **Errores:**
    - `404`: Comunidad no encontrada
    """
    comunidad = db.query(Comunidad).filter(Comunidad.id_comunidad == id_comunidad).first()

    if not comunidad:
        raise HTTPException(
            status_code=404,
            detail=f"Comunidad con ID {id_comunidad} no encontrada"
        )

    # Cambiar status
    comunidad.status = "Activa" if activar else "Inactiva"

    db.commit()
    db.refresh(comunidad)

    return comunidad


# =============================================================================
# DELETE - Eliminar lógicamente una comunidad
# =============================================================================

@router.delete("/{id_comunidad}", status_code=200)
def eliminar_comunidad(
    id_comunidad: int,
    db: Session = Depends(get_db)
):
    """
    Elimina lógicamente una comunidad (cambia status a "Inactiva").

    **IMPORTANTE:** Esta es una eliminación lógica (soft delete).
    La comunidad no se borra de la base de datos, solo se marca como "Inactiva".

    **Path Parameter:**
    - `id_comunidad`: ID de la comunidad a eliminar

    **Retorna:**
    ```json
    {
      "message": "Comunidad eliminada (inactivada) exitosamente",
      "id_comunidad": 5,
      "nombre": "Comunidad San Pedro"
    }
    ```

    **Errores:**
    - `404`: Comunidad no encontrada
    - `400`: La comunidad ya está inactiva
    """
    comunidad = db.query(Comunidad).filter(Comunidad.id_comunidad == id_comunidad).first()

    if not comunidad:
        raise HTTPException(
            status_code=404,
            detail=f"Comunidad con ID {id_comunidad} no encontrada"
        )

    # Verificar si ya está inactiva
    if comunidad.status == "Inactiva":
        raise HTTPException(
            status_code=400,
            detail=f"La comunidad '{comunidad.nombre}' ya está inactiva"
        )

    # Cambiar status a Inactiva (soft delete)
    comunidad.status = "Inactiva"

    db.commit()

    return {
        "message": "Comunidad eliminada (inactivada) exitosamente",
        "id_comunidad": comunidad.id_comunidad,
        "nombre": comunidad.nombre
    }


# =============================================================================
# EXTRA - Estadísticas de comunidades
# =============================================================================

@router.get("/stats/resumen", response_model=dict)
def estadisticas_comunidades(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de las comunidades.

    **Retorna:**
    ```json
    {
      "total_comunidades": 50,
      "comunidades_activas": 45,
      "comunidades_inactivas": 5,
      "total_reportes": 1250
    }
    ```
    """
    total = db.query(Comunidad).count()
    activas = db.query(Comunidad).filter(Comunidad.status == "Activa").count()
    inactivas = db.query(Comunidad).filter(Comunidad.status == "Inactiva").count()

    # Contar reportes relacionados
    from app.models import Reporte
    total_reportes = db.query(Reporte).filter(Reporte.id_comunidad.isnot(None)).count()

    return {
        "total_comunidades": total,
        "comunidades_activas": activas,
        "comunidades_inactivas": inactivas,
        "total_reportes": total_reportes
    }
