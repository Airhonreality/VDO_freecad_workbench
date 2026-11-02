"""app/vdo_api.py — Capa de re-exportacion para UI (F7).

Permite que ui/ importe de app/ en lugar de core directamente, cumpliendo
la dependencia ui -> app -> cad -> core (M-04).

Este modulo re-exporta los simbolos de core/ que la UI necesita. No contiene
logica propia: solo re-exporta.
"""

from __future__ import annotations

from freecad.vdo.cad.propiedades import aplicar_rotacion, rotacion_z
from freecad.vdo.core import vdo_cajon_core as vdo_cajon_core
from freecad.vdo.core import vdo_cajon_despiece as vdo_cajon_despiece
from freecad.vdo.core import vdo_defaults as vdo_defaults
from freecad.vdo.core import vdo_facade_contract as vdo_facade_contract
from freecad.vdo.core import vdo_finish as vdo_finish
from freecad.vdo.core import vdo_frames as vdo_frames
from freecad.vdo.core import vdo_hardware_hub as vdo_hardware_hub
from freecad.vdo.core import vdo_layout as vdo_layout
from freecad.vdo.core import vdo_manifest as vdo_manifest
from freecad.vdo.core import vdo_module_props as vdo_module_props
from freecad.vdo.core import vdo_nesting_presets as vdo_nesting_presets
from freecad.vdo.core import vdo_optimizer_core as vdo_optimizer_core
from freecad.vdo.core import vdo_panel_core as vdo_panel_core
from freecad.vdo.core import vdo_paths as vdo_paths
from freecad.vdo.core import vdo_puerta_core as vdo_puerta_core
from freecad.vdo.core import vdo_puerta_despiece as vdo_puerta_despiece

# Modulos enteros de core (re-exportados como atributos)
from freecad.vdo.core import vdo_reengrose as vdo_reengrose
from freecad.vdo.core import vdo_spaces as vdo_spaces
from freecad.vdo.core import vdo_view_base as vdo_view_base
from freecad.vdo.core import vdo_zocalo_core as vdo_zocalo_core
from freecad.vdo.core.vdo_cajon_core import (
    CajonFeature,
    make_cajon,
)
from freecad.vdo.core.vdo_cajon_despiece import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
    CAJA_METALICA,
    CORREDERA_OCULTA,
    CORREDERA_TELESCOPICA,
    calcular_despiece,
    listar_marcas,
    necesita_bisel_45,
    necesita_descuento_gola,
)
from freecad.vdo.core.vdo_facade_contract import (
    CALLE_ENTRE_FRENTES_DEFAULT,
    MONTAJE_EMBEBIDA,
    MONTAJE_PARCHE,
    MONTAJE_SEMIPARCHE,
    OPERACION_CANTO_45,
    OPERACION_CANTO_ESTANDAR,
    OPERACION_CANTO_GOLA,
    SISTEMAS_APERTURA_VALIDOS,
    cantos_por_sistema_apertura,
    necesita_cantos_45,
    necesita_expulsor_magnetico,
)
from freecad.vdo.core.vdo_layout import (
    AXIS_X,
    AXIS_Y,
    Layout,
    LayoutError,
    cavidad_interior,
    resolve_layout,
)
from freecad.vdo.core.vdo_module_props import (
    ANCLAJE_DEFAULT,
    ANCLAJE_LABELS,
    ANCLAJES,
    add_common_props,
    ancla_local,
    leer_rotacion,
)
from freecad.vdo.core.vdo_panel_core import (
    CANTOS_VALIDOS,
    add_reengrose_props,
)
from freecad.vdo.core.vdo_puerta_core import (
    PuertaFeature,
    make_puerta,
)
from freecad.vdo.core.vdo_puerta_despiece import (
    ajuste_altura_apertura,
    bisagras_para_puerta,
    calcular_corrediza,
    descripcion_piston,
)
from freecad.vdo.core.vdo_view_base import (
    _es_cajon,
    _es_coco,
    _es_panel,
    _es_zocalo,
)

# Nombres individuales importados directamente por ui/
from freecad.vdo.core.vdo_zocalo_core import (
    ZocaloError,
    calcular_geometria_zocalo,
)

SISTEMAS_APERTURA = SISTEMAS_APERTURA_VALIDOS  # alias para compatibilidad UI
from freecad.vdo.core.vdo_hardware_hub import (
    _FAMILIAS,
    get_family,
    resolve_drawer_slide,
)
from freecad.vdo.core.vdo_paths import (
    ruta_icono,
)
from freecad.vdo.core.vdo_spaces import (
    ESPACIO_FIJO,
    ESPACIO_IGUALES,
    ESPACIO_RESTANTE,
    SpaceNode,
    calcular_espacio_libre,
    deserializar_espacios,
    serializar_espacios,
)

__all__ = [
    "ANCLAJES",
    "ANCLAJE_DEFAULT",
    "ANCLAJE_LABELS",
    "APERTURA_45_GRADOS",
    "APERTURA_GOLA",
    "APERTURA_PUSH_OPEN",
    "APERTURA_TIRADOR",
    "AXIS_X",
    "AXIS_Y",
    "CAJA_METALICA",
    "CALLE_ENTRE_FRENTES_DEFAULT",
    "CANTOS_VALIDOS",
    "CORREDERA_OCULTA",
    "CORREDERA_TELESCOPICA",
    "ESPACIO_FIJO",
    "ESPACIO_IGUALES",
    "ESPACIO_RESTANTE",
    "MONTAJE_EMBEBIDA",
    "MONTAJE_PARCHE",
    "MONTAJE_SEMIPARCHE",
    "OPERACION_CANTO_45",
    "OPERACION_CANTO_ESTANDAR",
    "OPERACION_CANTO_GOLA",
    "SISTEMAS_APERTURA",
    "SISTEMAS_APERTURA_VALIDOS",
    "_FAMILIAS",
    "CajonFeature",
    "Layout",
    "LayoutError",
    "PuertaFeature",
    "SpaceNode",
    "ZocaloError",
    "_es_cajon",
    "_es_coco",
    "_es_panel",
    "_es_zocalo",
    "add_common_props",
    "add_reengrose_props",
    "ajuste_altura_apertura",
    "ancla_local",
    "aplicar_rotacion",
    "bisagras_para_puerta",
    "calcular_corrediza",
    "calcular_despiece",
    "calcular_espacio_libre",
    "calcular_geometria_zocalo",
    "cantos_por_sistema_apertura",
    "cavidad_interior",
    "descripcion_piston",
    "deserializar_espacios",
    "get_family",
    "leer_rotacion",
    "listar_marcas",
    "make_cajon",
    "make_puerta",
    "necesita_bisel_45",
    "necesita_cantos_45",
    "necesita_descuento_gola",
    "necesita_expulsor_magnetico",
    "resolve_drawer_slide",
    "resolve_layout",
    "rotacion_z",
    "ruta_icono",
    "serializar_espacios",
    "vdo_cajon_core",
    "vdo_cajon_despiece",
    "vdo_defaults",
    "vdo_facade_contract",
    "vdo_finish",
    "vdo_frames",
    "vdo_hardware_hub",
    "vdo_layout",
    "vdo_manifest",
    "vdo_module_props",
    "vdo_nesting_presets",
    "vdo_optimizer_core",
    "vdo_paths",
    "vdo_puerta_core",
    "vdo_puerta_despiece",
    "vdo_reengrose",
    "vdo_view_base",
    "vdo_zocalo_core",
]
