from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Despacho, ItemDespacho, LoteProductoTerminado
from app.schemas import DespachoCreate, RecepcionDestinoBody


class DespachoRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Despacho]:
        return self.db.query(Despacho).order_by(Despacho.id.desc()).all()

    def get_by_id(self, despacho_id: int) -> Optional[Despacho]:
        return (
            self.db.query(Despacho)
            .filter(Despacho.id == despacho_id)
            .first()
        )

    def create(
        self,
        body: DespachoCreate,
        responsable_id,
        items_data: list,
        total_kg,
        total_bs,
        numero_lote_despacho: str,
    ) -> Despacho:
        ep = body.entregado_por
        cond = body.conductor
        auth = body.autorizado_por
        dest = body.entregado_destino

        despacho = Despacho(
            responsable_id=responsable_id,
            fecha_despacho=body.fecha_despacho,
            numero_lote_despacho=numero_lote_despacho,
            estado_producto=body.estado_producto,
            propietario_pulpa=body.propietario_pulpa,
            origen_carga=body.origen_carga,
            destino_carga=body.destino_carga,
            detalle_transporte=body.detalle_transporte,
            codigo_ncoi=body.codigo_ncoi,
            precio_bs_kg=body.precio_bs_kg,
            total_kg=total_kg,
            total_bs=total_bs,
            estado_pulpa=body.estado_pulpa,
            entregado_por_nombre=ep.nombre if ep else None,
            entregado_por_ci=ep.ci if ep else None,
            entregado_por_cargo=ep.cargo if ep else None,
            conductor_nombre=cond.nombre if cond else None,
            conductor_ci=cond.ci if cond else None,
            conductor_cargo=cond.cargo if cond else None,
            autorizado_por_nombre=auth.nombre if auth else None,
            autorizado_por_ci=auth.ci if auth else None,
            autorizado_por_cargo=auth.cargo if auth else None,
            entregado_destino_nombre=dest.nombre if dest else None,
            entregado_destino_ci=dest.ci if dest else None,
            entregado_destino_cargo=dest.cargo if dest else None,
        )
        self.db.add(despacho)
        self.db.flush()

        for item_body, lpt, subtotal_bs in items_data:
            item = ItemDespacho(
                despacho_id=despacho.id,
                lote_producto_terminado_id=item_body.lote_producto_terminado_id,
                fecha_despacho=body.fecha_despacho,
                numero_lote=lpt.numero_lote,
                peso_kg=item_body.peso_kg,
                numero_cajas=item_body.numero_cajas,
                subtotal_bs=subtotal_bs,
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(despacho)
        return despacho

    def update_recepcion_destino(
        self,
        despacho: Despacho,
        body: RecepcionDestinoBody,
    ) -> Despacho:
        despacho.recibido_por_nombre = body.recibido_por_nombre
        despacho.recibido_por_ci = body.recibido_por_ci
        despacho.recibido_por_cargo = body.recibido_por_cargo
        despacho.fecha_recibido = body.fecha_recibido
        despacho.cantidad_recibida_kg = body.cantidad_recibida_kg
        self.db.commit()
        self.db.refresh(despacho)
        return despacho
