# -*- coding: utf-8 -*-
"""app/vdo_api.py — Capa de re-exportacion para UI (F7).

Permite que ui/ importe de app/ en lugar de core directamente, cumpliendo
la dependencia ui -> app -> cad -> core (M-04).

Este modulo re-exporta los simbolos de core/ que la UI necesita. No contiene
logica propia: solo re-exporta.
"""

from __future__ import annotations

# Modulos enteros de core (re-exportados como atributos)
from freecad.vdo.core import vdo_reengrose as vdo_reengrose  # noqa: F401
from freecad.vdo.core import vdo_frames as vdo_frames  # noqa: F401
from freecad.vdo.core import vdo_finish as vdo_finish  # noqa: F401
from freecad.vdo.core import vdo_defaults as vdo_defaults  # noqa: F401
from freecad.vdo.core import vdo_hardware_hub as vdo_hardware_hub  # noqa: F401
from freecad.vdo.core import vdo_manifest as vdo_manifest  # noqa: F401
from freecad.vdo.core import vdo_module_props as vdo_module_props  # noqa: F401
from freecad.vdo.core import vdo_zocalo_core as vdo_zocalo_core  # noqa: F401
from freecad.vdo.core import vdo_puerta_core as vdo_puerta_core  # noqa: F401
from freecad.vdo.core import vdo_cajon_core as vdo_cajon_core  # noqa: F401
from freecad.vdo.core import vdo_layout as vdo_layout  # noqa: F401
from freecad.vdo.core import vdo_facade_contract as vdo_facade_contract  # noqa: F401
from freecad.vdo.core import vdo_view_base as vdo_view_base  # noqa: F401
from freecad.vdo.core import vdo_paths as vdo_paths  # noqa: F401
from freecad.vdo.core import vdo_optimizer_core as vdo_optimizer_core  # noqa: F401
from freecad.vdo.core import vdo_nesting_presets as vdo_nesting_presets  # noqa: F401
from freecad.vdo.core import vdo_puerta_despiece as vdo_puerta_despiece  # noqa: F401
from freecad.vdo.core import vdo_cajon_despiece as vdo_cajon_despiece  # noqa: F401
from freecad.vdo.core import vdo_panel_core as vdo_panel_core  # noqa: F401
from freecad.vdo.core.vdo_panel_core import (  # noqa: F401
    CANTOS_VALIDOS, add_reengrose_props,
)
from freecad.vdo.core import vdo_spaces as vdo_spaces  # noqa: F401

from freecad.vdo.cad.propiedades import aplicar_rotacion, rotacion_z  # noqa: F401

# Nombres individuales importados directamente por ui/
from freecad.vdo.core.vdo_zocalo_core import (  # noqa: F401
    calcular_geometria_zocalo, ZocaloError,
)
from freecad.vdo.core.vdo_puerta_despiece import (  # noqa: F401
    bisagras_para_puerta, descripcion_piston, calcular_corrediza, ajuste_altura_apertura,
)
from freecad.vdo.core.vdo_cajon_despiece import (  # noqa: F401
    calcular_despiece, listar_marcas,
    CORREDERA_TELESCOPICA, CORREDERA_OCULTA, CAJA_METALICA,
    APERTURA_TIRADOR, APERTURA_GOLA, APERTURA_45_GRADOS, APERTURA_PUSH_OPEN,
    necesita_bisel_45, necesita_descuento_gola,
)
from freecad.vdo.core.vdo_puerta_core import (  # noqa: F401
    make_puerta, PuertaFeature,
)
from freecad.vdo.core.vdo_cajon_core import (  # noqa: F401
    make_cajon, CajonFeature,
)
from freecad.vdo.core.vdo_module_props import (  # noqa: F401
    add_common_props, ANCLAJES, ANCLAJE_LABELS, ANCLAJE_DEFAULT,
    ancla_local, leer_rotacion,
)
from freecad.vdo.core.vdo_layout import (  # noqa: F401
    Layout, resolve_layout, cavidad_interior, LayoutError, AXIS_X, AXIS_Y,
)
from freecad.vdo.core.vdo_view_base import (  # noqa: F401
    _es_coco, _es_cajon, _es_zocalo, _es_panel,
)
from freecad.vdo.core.vdo_facade_contract import (  # noqa: F401
    CALLE_ENTRE_FRENTES_DEFAULT, OPERACION_CANTO_ESTANDAR,
    OPERACION_CANTO_GOLA, OPERACION_CANTO_45,
    MONTAJE_PARCHE, MONTAJE_SEMIPARCHE, MONTAJE_EMBEBIDA,
    SISTEMAS_APERTURA_VALIDOS, cantos_por_sistema_apertura,
    necesita_expulsor_magnetico, necesita_cantos_45,
)
SISTEMAS_APERTURA = SISTEMAS_APERTURA_VALIDOS  # alias para compatibilidad UI
from freecad.vdo.core.vdo_spaces import (  # noqa: F401
    SpaceNode, ESPACIO_FIJO, ESPACIO_RESTANTE, ESPACIO_IGUALES,
    serializar_espacios, deserializar_espacios, calcular_espacio_libre,
)
from freecad.vdo.core.vdo_hardware_hub import (  # noqa: F401
    resolve_drawer_slide, get_family, _FAMILIAS,
)
from freecad.vdo.core.vdo_paths import (  # noqa: F401
    ruta_icono,
)

__all__ = [
    "vdo_reengrose", "vdo_frames", "vdo_finish", "vdo_defaults",
    "vdo_hardware_hub", "vdo_manifest", "vdo_module_props",
    "vdo_zocalo_core", "vdo_puerta_core", "vdo_cajon_core", "vdo_layout",
    "vdo_facade_contract", "vdo_view_base", "vdo_paths",
    "vdo_optimizer_core", "vdo_nesting_presets",
    "vdo_puerta_despiece", "vdo_cajon_despiece",
    "calcular_geometria_zocalo", "ZocaloError",
    "calcular_despiece",
    "CORREDERA_TELESCOPICA", "CORREDERA_OCULTA", "CAJA_METALICA",
    "APERTURA_TIRADOR", "APERTURA_GOLA", "APERTURA_45_GRADOS",
    "APERTURA_PUSH_OPEN", "necesita_bisel_45", "necesita_descuento_gola",
    "make_puerta", "PuertaFeature", "make_cajon", "CajonFeature",
    "add_common_props", "ANCLAJES", "ANCLAJE_LABELS", "ANCLAJE_DEFAULT",
    "leer_rotacion", "ancla_local",
    "Layout", "resolve_layout", "cavidad_interior", "LayoutError",
    "AXIS_X", "AXIS_Y",
    "_es_coco", "_es_cajon", "_es_zocalo", "_es_panel",
    "CALLE_ENTRE_FRENTES_DEFAULT", "OPERACION_CANTO_ESTANDAR",
    "OPERACION_CANTO_GOLA", "OPERACION_CANTO_45",
    "ruta_icono",
    "bisagras_para_puerta", "descripcion_piston", "calcular_corrediza",
    "ajuste_altura_apertura", "listar_marcas",
    "aplicar_rotacion", "rotacion_z",
    "SpaceNode", "ESPACIO_FIJO", "ESPACIO_RESTANTE", "CANTOS_VALIDOS",
    "add_reengrose_props",
    "MONTAJE_PARCHE", "MONTAJE_SEMIPARCHE", "MONTAJE_EMBEBIDA",
    "SISTEMAS_APERTURA_VALIDOS", "SISTEMAS_APERTURA",
    "cantos_por_sistema_apertura",
    "necesita_expulsor_magnetico", "necesita_cantos_45",
    "ESPACIO_IGUALES", "serializar_espacios", "deserializar_espacios",
    "calcular_espacio_libre",
    "resolve_drawer_slide", "get_family", "_FAMILIAS",
]
