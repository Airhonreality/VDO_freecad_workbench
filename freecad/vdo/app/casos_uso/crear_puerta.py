"""app/casos_uso/crear_puerta.py — Caso de uso: crear puerta batiente."""

from __future__ import annotations

from freecad.vdo.app.dto import PuertaDTO, PuertaResultado
from freecad.vdo.core.vdo_puerta_core import make_puerta


def crear_puerta(doc, dto: PuertaDTO) -> PuertaResultado:
    """Crea una puerta en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear la puerta.")
    cfg = {
        "nombre": dto.nombre,
        "tipo_sistema": "Batiente Vertical",
        "tipo_montaje": dto.tipo_montaje,
        "sentido_apertura": "Izquierda",
        "sistema_apertura": dto.sistema_apertura,
        "hardware_sku": "",
        "vdo_vano_id": "",
        "ancho": dto.ancho,
        "alto": dto.alto,
        "espesor": dto.espesor,
        "pos_x": 0.0,
        "pos_y": 0.0,
        "pos_z": 0.0,
        "anclaje": dto.anclaje,
    }
    obj = make_puerta(doc, cfg)
    if obj is None:
        return PuertaResultado(nombre=dto.nombre, alto=0.0)
    return PuertaResultado(nombre=obj.Name, alto=float(obj.Alto))
