# app/routes/precio_justo.py
"""
Endpoint para calcular el Precio Justo basado en los datos del formulario
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.core.deps import get_db
from app.services.precio_justo_service import PrecioJustoService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/precio-justo", tags=["Precio Justo"])


@router.post("/calcular", response_model=schemas.PrecioJustoResponse)
def calcular_precio_justo(
    request: schemas.FormularioCompletoRequest,
    db: Session = Depends(get_db)
):
    """
    Recibe el formulario completo, guarda los datos en la BD y calcula el Precio Justo.

    **Flujo:**
    1. Crea o actualiza el usuario en la tabla `usuarios`
    2. Guarda el reporte completo en la tabla `reportes`
    3. Calcula el Precio Justo según el rubro:
       - Si rubro = "Castaña": Solo retorna precio justo de castaña
       - Si rubro = "Asaí": Solo retorna precio justo de asaí
       - Si rubro = "Ambos productos": Retorna precios de ambos

    **Request Body:** FormularioCompletoRequest (todos los campos del formulario)

    **Response:** PrecioJustoResponse con resultados según rubro
    """
    from app.models import Usuario, Reporte
    import json

    # =========================================================================
    # PASO 1: CREAR O ACTUALIZAR USUARIO
    # =========================================================================
    usuario = db.query(Usuario).filter(Usuario.device_id == request.device_id).first()

    if usuario:
        # Actualizar usuario existente
        if request.nombre:
            usuario.nombre = request.nombre
        if request.rubro:
            usuario.rubro = request.rubro
        if request.actividades:
            usuario.actividades = json.dumps(request.actividades)  # Guardar como JSON
        if request.genero:
            usuario.genero = request.genero
        if request.edad:
            usuario.edad = request.edad
        if request.gps_lat:
            usuario.gps_lat = request.gps_lat
        if request.gps_lon:
            usuario.gps_lon = request.gps_lon
    else:
        # Crear nuevo usuario
        usuario = Usuario(
            device_id=request.device_id,
            nombre=request.nombre or "Usuario",
            rubro=request.rubro or "Ambos productos",
            actividades=json.dumps(request.actividades) if request.actividades else json.dumps([]),
            genero=request.genero or "Prefiero no decir",
            edad=request.edad or "18-25 años",
            gps_lat=request.gps_lat,
            gps_lon=request.gps_lon,
            fecha_registro=datetime.utcnow()
        )
        db.add(usuario)

    db.commit()
    db.refresh(usuario)

    # =========================================================================
    # PASO 2: CREAR REPORTE
    # =========================================================================
    reporte = Reporte(
        id_usuario=usuario.id_usuario,
        # Ubicación del reporte
        id_comunidad=request.comunidad_id,
        # Sección 1: Precios
        precio_recolector_castana=request.precio_recolector_castana,
        unidad_recolector_castana=request.unidad_recolector_castana,
        precio_intermediario_castana=request.precio_intermediario_castana,
        unidad_intermediario_castana=request.unidad_intermediario_castana,
        precio_cosechador_asai=request.precio_cosechador_asai,
        unidad_cosechador_asai=request.unidad_cosechador_asai,
        precio_intermediario_asai=request.precio_intermediario_asai,
        unidad_intermediario_asai=request.unidad_intermediario_asai,
        costo_transporte_castana=request.costo_transporte_castana,
        unidad_transporte_castana=request.unidad_transporte_castana,
        tipo_transporte_castana=request.tipo_transporte_castana,
        costo_transporte_asai=request.costo_transporte_asai,
        unidad_transporte_asai=request.unidad_transporte_asai,
        tipo_transporte_asai=request.tipo_transporte_asai,
        nodo_precio=request.nodo_precio,
        nodo_precio_otro=request.nodo_precio_otro,
        # Sección 2: Calidad
        tipo_castana=request.tipo_castana,
        tiempo_recoleccion_castana=request.tiempo_recoleccion_castana,
        tiempo_venta_castana=request.tiempo_venta_castana,
        tipo_asai=request.tipo_asai,
        tiempo_cosecha_asai=request.tiempo_cosecha_asai,
        # Sección 3: Transporte
        tipo_transporte_usado=request.tipo_transporte_usado,
        tipo_transporte_usado_otro=request.tipo_transporte_usado_otro,
        # Sección 4: Mercados Grandes
        no_sabe_fob_castana=request.no_sabe_fob_castana,
        moneda_fob_castana=request.moneda_fob_castana,
        precio_fob_castana=request.precio_fob_castana,
        unidad_fob_castana=request.unidad_fob_castana,
        fuente_precio_castana=request.fuente_precio_castana,
        fuente_precio_castana_otro=request.fuente_precio_castana_otro,
        no_sabe_mercado_asai=request.no_sabe_mercado_asai,
        precio_mercado_grande_asai=request.precio_mercado_grande_asai,
        unidad_mercado_grande_asai=request.unidad_mercado_grande_asai,
        mercado_asai=request.mercado_asai,
        mercado_asai_otro=request.mercado_asai_otro,
        fuente_precio_asai=request.fuente_precio_asai,
        fuente_precio_asai_otro=request.fuente_precio_asai_otro,
        # Sección 5: Feedback
        comentarios_adicionales=request.comentarios_adicionales,
        # Metadata
        latitud=request.latitud,
        longitud=request.longitud,
        fecha_registro=datetime.utcnow()
    )

    db.add(reporte)
    db.commit()
    db.refresh(reporte)

    # =========================================================================
    # PASO 3: CALCULAR PRECIO JUSTO SEGÚN RUBRO
    # =========================================================================
    service = PrecioJustoService(db)
    response = schemas.PrecioJustoResponse(fecha_calculo=datetime.utcnow())

    # Determinar qué producto(s) calcular según el rubro
    rubro = usuario.rubro or "Ambos productos"

    # Normalizar rubro para comparación (case-insensitive, sin acentos)
    rubro_lower = rubro.lower().replace("ñ", "n").replace("í", "i")

    logger.info(f"Rubro original: '{rubro}', Rubro normalizado: '{rubro_lower}'")

    # Obtener zona desde la comunidad si existe
    zona = "Norte amazónico"  # Valor por defecto
    if reporte.id_comunidad:
        from app.models import Comunidad
        comunidad = db.query(Comunidad).filter(Comunidad.id_comunidad == reporte.id_comunidad).first()
        if comunidad:
            # Usar el nombre de la comunidad como zona
            zona = comunidad.nombre
            logger.info(f"Zona obtenida de comunidad ID {reporte.id_comunidad}: '{zona}'")
    else:
        logger.warning(f"No se especificó comunidad, usando zona por defecto: '{zona}'")

    # =========================================================================
    # CALCULAR PRECIO JUSTO PARA CASTAÑA
    # Solo si: rubro == "Castaña" O rubro == "Ambos productos"
    # =========================================================================
    if rubro_lower in ["castana", "castania", "ambos productos"]:
        logger.info(f"Calculando precio justo para CASTAÑA (rubro: {rubro})")
        try:
            resultado_castana = service.calcular_precio_justo_castana(
                costo_transporte=request.costo_transporte_castana,
                tipo_castana=request.tipo_castana,
                tiempo_recoleccion=request.tiempo_recoleccion_castana,
                tiempo_venta=request.tiempo_venta_castana,
                unidad=request.unidad_recolector_castana,
                zona=zona
            )

            # Formatear mensaje según especificación
            pj_castana = resultado_castana["precio_justo"]
            mensaje = f"Tu precio para {request.unidad_recolector_castana} de Castaña es {pj_castana:.2f} Bs."

            # Crear detalles
            detalles_dict = resultado_castana["detalles"]
            detalles = schemas.PrecioJustoDetalles(
                p_base_ajustado=detalles_dict["p_base_ajustado"],
                bono_certificacion=detalles_dict["bono_certificacion"],
                ajuste_deterioro=detalles_dict["ajuste_deterioro"],
                p_prom_planta=detalles_dict["p_prom_planta"],
                costo_transporte=detalles_dict["costo_transporte"]
            )

            response.castana = schemas.PrecioJustoResultadoCastana(
                precio_justo=pj_castana,
                mensaje=mensaje,
                detalles=detalles
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al calcular Precio Justo para Castaña: {str(e)}"
            )

    # =========================================================================
    # CALCULAR PRECIO JUSTO PARA ASAÍ
    # Solo si: rubro == "Asaí" O rubro == "Ambos productos"
    # =========================================================================
    if rubro_lower in ["asai", "asaí", "ambos productos"]:
        try:
            resultado_asai = service.calcular_precio_justo_asai(
                costo_transporte=request.costo_transporte_asai,
                tipo_asai=request.tipo_asai,
                horas_desde_cosecha=request.tiempo_cosecha_asai,
                unidad=request.unidad_cosechador_asai,
                zona=zona
            )

            # Formatear mensaje según especificación
            pj_asai = resultado_asai["precio_justo"]
            mensaje = f"Tu precio para {request.unidad_cosechador_asai} de Asaí es {pj_asai:.2f} Bs."

            # Crear detalles
            detalles_dict = resultado_asai["detalles"]
            detalles = schemas.PrecioJustoDetalles(
                p_base_ajustado=detalles_dict["p_base_ajustado"],
                bono_certificacion=detalles_dict["bono_certificacion"],
                bono_frescura=detalles_dict["bono_frescura"],
                p_prom_planta=detalles_dict["p_prom_planta"],
                costo_transporte=detalles_dict["costo_transporte"]
            )

            response.asai = schemas.PrecioJustoResultadoAsai(
                precio_justo=pj_asai,
                mensaje=mensaje,
                detalles=detalles
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al calcular Precio Justo para Asaí: {str(e)}"
            )

    return response


@router.get("/variables-maestras")
def obtener_variables_maestras(db: Session = Depends(get_db)):
    """
    Endpoint auxiliar para consultar las variables maestras del sistema.
    Útil para debugging y monitoreo.

    Retorna:
    - P_Prom_Planta_C: Precio promedio de castaña en planta
    - P_Prom_Planta_A: Precio promedio de asaí en planta
    - Conteo de reportes usados en los cálculos
    """
    service = PrecioJustoService(db)

    return {
        "p_prom_planta_castana": service.calcular_p_prom_planta_castana(),
        "p_prom_planta_asai": service.calcular_p_prom_planta_asai(),
        "parametros_sistema": {
            "castana": {
                "bono_organico_bs": service.PARAM_BONO_ORGANICO_C_BS,
                "umbral_dias": service.PARAM_UMBRAL_DIAS_C,
                "penalidad_dia_bs": service.PARAM_PENALIDAD_DIA_C_BS
            },
            "asai": {
                "bono_organico_bs": service.PARAM_BONO_ORGANICO_A_BS,
                "bono_fr94_bs": service.PARAM_BONO_ASAI_FR94_BS,
                "bono_fr90_bs": service.PARAM_BONO_ASAI_FR90_BS,
                "bono_fr85_bs": service.PARAM_BONO_ASAI_FR85_BS
            }
        }
    }
