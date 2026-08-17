from __future__ import annotations

import random
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import AutorizacionRecolector, Comunidad, Recolector, EntregaRecolector, UsuarioSistema
from app.repositories.recolectores import RecolectorRepository
from app.schemas import RecolectorCreate, RecolectorUpdate, EntregaRecolectorCreate

_ROL_RECOLECTOR = "recolector"
_METODO_AUTH_PIN = "pin"

_ESTADOS_VALIDOS = {"activo", "inactivo"}
_TRANSPORTES_VALIDOS = {"fluvial", "terrestre"}
_RECEPCIONES_VALIDAS = {"aceptado", "rechazado"}


class RecolectorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecolectorRepository(db)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _get_or_404(self, recolector_id: int) -> Recolector:
        rec = self.repo.get_by_id(recolector_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recolector {recolector_id} no encontrado",
            )
        return rec

    @staticmethod
    def _generar_pin() -> str:
        return str(random.randint(100000, 999999))

    @staticmethod
    def _generar_numero_entrega(codigo: str, fecha_entrega: date, hora_recepcion) -> str:
        """Formato: {codigo_recolector}-{YYYYMMDD}-{HHMM}"""
        if hora_recepcion:
            hora_str = hora_recepcion.strftime("%H%M")
        else:
            hora_str = datetime.utcnow().strftime("%H%M")
        return f"{codigo}-{fecha_entrega.strftime('%Y%m%d')}-{hora_str}"

    # ------------------------------------------------------------------
    # Recolectores
    # ------------------------------------------------------------------

    def crear(self, body: RecolectorCreate, creado_por_id) -> tuple[Recolector, str]:
        """
        Crea en una sola transacción:
          1. UsuarioSistema (username = codigo, rol = recolector, metodo_auth = pin)
          2. Recolector vinculado al usuario creado
        Devuelve (recolector, pin_generado). pin_generado es el PIN en texto plano,
        visible UNA SOLA VEZ en la respuesta del POST.
        """
        if self.repo.get_by_codigo(body.codigo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un recolector con el código '{body.codigo}'",
            )

        pin = body.credencial if body.credencial else self._generar_pin()

        comunidad = self.db.query(Comunidad).filter(
            Comunidad.id_comunidad == body.comunidad_id
        ).first()
        if not comunidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comunidad {body.comunidad_id} no encontrada",
            )

        # 1. Crear cuenta de sistema
        usuario = UsuarioSistema(
            nombre_completo=body.nombre_completo,
            username=body.codigo,
            rol=_ROL_RECOLECTOR,
            metodo_auth=_METODO_AUTH_PIN,
            credencial_hash=get_password_hash(pin),
            comunidad=comunidad.nombre,
            creado_por=creado_por_id,
        )
        self.db.add(usuario)
        self.db.flush()  # obtiene usuario.id sin hacer commit

        # 2. Crear perfil de recolector
        rec = Recolector(
            usuario_id=usuario.id,
            comunidad_id=body.comunidad_id,
            codigo=body.codigo,
            nombre_completo=body.nombre_completo,
            ci=body.ci,
            documento_tenencia=body.documento_tenencia,
            codigo_tc=body.codigo_tc,
            especie=body.especie,
            fecha_registro=body.fecha_registro,
            estado="activo",
            creado_por=creado_por_id,
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec, pin

    def listar(
        self,
        *,
        comunidad_id: int | None,
        estado: str | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[Recolector]]:
        if estado and estado not in _ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"estado debe ser uno de: {sorted(_ESTADOS_VALIDOS)}",
            )
        return self.repo.list(
            comunidad_id=comunidad_id,
            estado=estado,
            search=search,
            page=page,
            page_size=page_size,
        )

    def obtener(self, recolector_id: int) -> Recolector:
        return self._get_or_404(recolector_id)

    def obtener_por_usuario(self, usuario_id) -> Recolector:
        rec = self.repo.get_by_usuario_id(usuario_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de recolector no encontrado para este usuario",
            )
        return rec

    def actualizar(self, recolector_id: int, body: RecolectorUpdate) -> Recolector:
        rec = self._get_or_404(recolector_id)
        updates = body.model_dump(exclude_unset=True)

        if "estado" in updates and updates["estado"] not in _ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"estado debe ser uno de: {sorted(_ESTADOS_VALIDOS)}",
            )

        if not updates:
            return rec
        return self.repo.update(rec, **updates)

    # ------------------------------------------------------------------
    # Habilitación vigente
    # ------------------------------------------------------------------

    def get_habilitacion_vigente(self, usuario_id) -> AutorizacionRecolector:
        rec = self.obtener_por_usuario(usuario_id)
        cosecha_actual = datetime.utcnow().year
        habilitacion = self.repo.get_habilitacion_vigente(rec.id, cosecha_actual)
        if not habilitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sin habilitación vigente para la cosecha {cosecha_actual}",
            )
        return habilitacion

    # ------------------------------------------------------------------
    # Entregas
    # ------------------------------------------------------------------

    def listar_entregas(self, recolector_id: int) -> list[EntregaRecolector]:
        self._get_or_404(recolector_id)
        return self.repo.list_entregas(recolector_id)

    def crear_entrega(
        self,
        recolector_id: int,
        body: EntregaRecolectorCreate,
    ) -> EntregaRecolector:
        rec = self._get_or_404(recolector_id)

        if body.medio_transporte and body.medio_transporte not in _TRANSPORTES_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"medio_transporte debe ser uno de: {sorted(_TRANSPORTES_VALIDOS)}",
            )

        fecha_ent = body.fecha_entrega or date.today()
        numero_entrega = self._generar_numero_entrega(rec.codigo, fecha_ent, body.hora_recepcion)

        return self.repo.create_entrega(
            numero_entrega=numero_entrega,
            recolector_id=recolector_id,
            parcela_id=body.parcela_id,
            peso_kg=body.peso_kg,
            fecha_recoleccion=body.fecha_recoleccion,
            fecha_entrega=fecha_ent,
            tipo_envase=body.tipo_envase,
            hora_cosecha=body.hora_cosecha,
            hora_recepcion=body.hora_recepcion,
            medio_transporte=body.medio_transporte,
            firma_recolector=body.firma_recolector,
            observaciones=body.observaciones,
        )
