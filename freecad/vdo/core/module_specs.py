# =====================================================================
# module_specs.py
# Registro de módulos VDO y sus paneles de configuración.
# Los imports son perezosos para evitar ciclos.
# =====================================================================

import importlib
import json
import os
from collections.abc import Sequence
from typing import Any

# Especificaciones de módulo: datos en freecad/vdo/datos/modulos.json (D-17, MN-04).
# Las tuplas del JSON (p. ej. "factory") son listas; _resolver las desempaqueta igual.
_RUTA_MODULOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos", "modulos.json")
with open(_RUTA_MODULOS, encoding="utf-8") as _fh:
    MODULE_SPECS: dict[str, Any] = json.load(_fh)  # JSON: valores sin tipo fijo



def _resolver(referencia: Sequence[str]) -> Any:  # atributo importado, sin tipo
    modulo, atributo = referencia
    mod = importlib.import_module(modulo)
    return getattr(mod, atributo)


def resolver_panel(spec: dict[str, Any]) -> Any:  # valor JSON 'panel_ref'
    """Devuelve la referencia del panel (string) para que app/ resuelva la vista. D24."""
    return spec.get("panel_ref")


def get_spec(module_key: str) -> dict[str, Any]:
    """Devuelve una copia de la spec con la factory resuelta."""
    base = MODULE_SPECS.get(module_key)
    if base is None:
        raise KeyError(f"Módulo VDO desconocido: {module_key}")
    spec = dict(base)
    spec["config"] = dict(base.get("config", {}))
    spec["factory_fn"] = _resolver(base["factory"])
    spec["panel_ref"] = base["panel"]
    return spec

