"""app/casos_uso/crear_coco.py — Caso de uso: crear COCO 4C."""

from __future__ import annotations

from freecad.vdo.app.dto import CocoDTO, CocoResultado
from freecad.vdo.core.vdo_coco_core import make_coco


def crear_coco(doc, dto: CocoDTO) -> CocoResultado:
    """Crea un COCO en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el COCO.")
    cfg = {
        "nombre": dto.nombre,
        "alto": dto.alto,
        "ancho": dto.ancho,
        "fondo_modulo": dto.fondo_modulo,
        "espesor": dto.espesor,
        "tiene_fondo": dto.tiene_fondo,
        "calibre_fondo": dto.calibre_fondo,
        "divisiones": dto.divisiones,
        "reengroses": dto.reengroses or {},
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
        "lados_vistos": dto.lados_vistos or ["frente"],
        "lados_apoyados": dto.lados_apoyados or ["fondo"],
    }
    obj = make_coco(doc, cfg)
    if obj is None:
        return CocoResultado(nombre=dto.nombre, volumen=0.0)
    return CocoResultado(nombre=obj.Name, volumen=float(obj.Shape.Volume))
