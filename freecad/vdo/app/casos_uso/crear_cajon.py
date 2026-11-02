"""app/casos_uso/crear_cajon.py — Caso de uso: crear cajón con corredera."""

from __future__ import annotations

from freecad.vdo.app.dto import CajonDTO, CajonResultado
from freecad.vdo.core.vdo_cajon_core import make_cajon


def crear_cajon(doc, dto: CajonDTO) -> CajonResultado:
    """Crea un cajón en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el cajón.")
    cfg = {
        "nombre": dto.nombre,
        "ancho_libre": dto.ancho_libre,
        "prof_libre": dto.prof_libre,
        "ancho_modulo": dto.ancho_modulo,
        "alto_frente": dto.alto_frente,
        "alto_caja": dto.alto_caja,
        "grosor_caja": dto.grosor_caja,
        "grosor_fondo": dto.grosor_fondo,
        "grosor_fachada": dto.grosor_fachada,
        "marca": dto.marca,
        "longitud_guia": dto.longitud_guia,
        "montaje_trasera": dto.montaje_trasera,
        "tipo_corredera": dto.tipo_corredera,
        "sistema_apertura": dto.sistema_apertura,
        "tipo_montaje": dto.tipo_montaje,
        "material_ref": dto.material_ref,
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
    }
    obj = make_cajon(doc, cfg)
    if obj is None:
        return CajonResultado(nombre=dto.nombre, tipo_corredera="")
    return CajonResultado(nombre=obj.Name, tipo_corredera=str(obj.TipoCorredera))
