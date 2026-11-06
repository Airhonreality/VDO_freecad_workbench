"""app/casos_uso/crear_zocalo.py — Caso de uso: crear zócalo."""

from __future__ import annotations

from freecad.vdo.core.dto import ZocaloDTO, ZocaloResultado
from freecad.vdo.core.vdo_zocalo_core import make_zocalo


def crear_zocalo(doc, dto: ZocaloDTO) -> ZocaloResultado:
    """Crea un zócalo en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el zócalo.")
    cfg = {
        "nombre": dto.nombre,
        "ancho": dto.ancho,
        "fondo": dto.fondo,
        "alto_zocalo": dto.alto_zocalo,
        "espesor_tablero": dto.espesor_tablero,
        "distancia_frente": dto.distancia_frente,
        "distancia_costados": dto.distancia_costados,
        "distancia_trasera": dto.distancia_trasera,
        "tiene_trasera": dto.tiene_trasera,
        "amarres_intermedios": dto.amarres_intermedios,
        "material_ref": dto.material_ref,
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
    }
    obj = make_zocalo(doc, cfg)
    if obj is None:
        return ZocaloResultado(nombre=dto.nombre, volumen=0.0)
    return ZocaloResultado(nombre=obj.Name, volumen=float(obj.Shape.Volume))
