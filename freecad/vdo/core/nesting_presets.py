# =====================================================================
# nesting_presets.py
# Gestor de presets de tableros para nesting.
# Nota: FreeCAD se importa de forma perezosa dentro de las funciones que
# lo necesitan (no a nivel de modulo), para que este modulo pueda
# importarse sin FreeCAD (R2).
# =====================================================================

import json
from collections.abc import Mapping
from typing import Any, Final

from freecad.vdo.core.helpers import _get_app

# Presets estándar del taller (2440x1830 es estándar EN)
DEFAULT_PRESETS: Final[Mapping[str, Mapping[str, int]]] = {
    "Estándar EN": {"width": 2440, "height": 1830, "spacing": 15, "thickness": 3},
    "Medio Horizontal": {"width": 1220, "height": 2440, "spacing": 15, "thickness": 3},
    "Pequeño": {"width": 1200, "height": 900, "spacing": 12, "thickness": 3},
    "Cuadrado": {"width": 1000, "height": 1000, "spacing": 15, "thickness": 3},
    "Larguero": {"width": 3000, "height": 600, "spacing": 15, "thickness": 3},
}

PREFS_PATH: Final = "User parameter:BaseApp/Preferences/NestingWorkbench/VDO"


class NestingPresetManager:
    """Gestiona presets de tableros para nesting."""

    PREFS_PATH = PREFS_PATH

    @staticmethod
    def get_prefs() -> Any:  # ParamGet de FreeCAD: sin tipos
        """Obtiene el objeto de preferencias."""
        return _get_app().ParamGet(NestingPresetManager.PREFS_PATH)

    @staticmethod
    def initialize_defaults() -> None:
        """Inicializa presets por defecto si no existen."""
        prefs = NestingPresetManager.get_prefs()

        if prefs.GetString("Presets", "") == "":
            presets_data = {
                "list": list(DEFAULT_PRESETS.keys()),
                "presets": DEFAULT_PRESETS
            }
            prefs.SetString("Presets", json.dumps(presets_data))
            _get_app().Console.PrintMessage(
                "[VDO Nesting] Presets inicializados con valores por defecto")

    @staticmethod
    def get_all_presets() -> dict[str, Any]:
        """Obtiene todos los presets disponibles."""
        prefs = NestingPresetManager.get_prefs()
        presets_json = prefs.GetString("Presets", "{}")
        data = json.loads(presets_json)
        presets: dict[str, Any] = data.get("presets", DEFAULT_PRESETS)
        return presets

    @staticmethod
    def get_preset(name: str) -> Any:
        """Obtiene un preset específico."""
        presets = NestingPresetManager.get_all_presets()
        return presets.get(name, None)

    @staticmethod
    def save_preset(name: str, width: int, height: int,
                    spacing: int = 15, thickness: int = 3) -> None:
        """Guarda un nuevo preset."""
        prefs = NestingPresetManager.get_prefs()
        presets_json = prefs.GetString("Presets", "{}")
        data = json.loads(presets_json)

        if "list" not in data:
            data["list"] = []
        if "presets" not in data:
            data["presets"] = {}

        data["presets"][name] = {
            "width": width,
            "height": height,
            "spacing": spacing,
            "thickness": thickness
        }

        if name not in data["list"]:
            data["list"].append(name)

        prefs.SetString("Presets", json.dumps(data))
        _get_app().Console.PrintMessage(
            f"[VDO Nesting] Preset '{name}' guardado")

    @staticmethod
    def delete_preset(name: str) -> bool:
        """Elimina un preset."""
        prefs = NestingPresetManager.get_prefs()
        presets_json = prefs.GetString("Presets", "{}")
        data = json.loads(presets_json)

        if name in data.get("presets", {}):
            del data["presets"][name]

        if name in data.get("list", []):
            data["list"].remove(name)

        prefs.SetString("Presets", json.dumps(data))
        _get_app().Console.PrintMessage(
            f"[VDO Nesting] Preset '{name}' eliminado")
        return True

    @staticmethod
    def get_preset_names() -> list[str]:
        """Obtiene lista de nombres de presets."""
        presets = NestingPresetManager.get_all_presets()
        return list(presets.keys())

    @staticmethod
    def export_presets_to_json(filepath: str) -> None:
        """Exporta todos los presets a un archivo JSON."""
        presets = NestingPresetManager.get_all_presets()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(presets, f, indent=2, ensure_ascii=False)
        _get_app().Console.PrintMessage(
            f"[VDO Nesting] Presets exportados a: {filepath}")

    @staticmethod
    def import_presets_from_json(filepath: str) -> bool:
        """Importa presets desde un archivo JSON."""
        with open(filepath, encoding='utf-8') as f:
            new_presets = json.load(f)

        prefs = NestingPresetManager.get_prefs()
        existing_data = json.loads(prefs.GetString("Presets", "{}"))

        if "presets" not in existing_data:
            existing_data["presets"] = {}
        if "list" not in existing_data:
            existing_data["list"] = []

        for name, config in new_presets.items():
            existing_data["presets"][name] = config
            if name not in existing_data["list"]:
                existing_data["list"].append(name)

        prefs.SetString("Presets", json.dumps(existing_data))
        _get_app().Console.PrintMessage(
            f"[VDO Nesting] Presets importados desde: {filepath}")
        return True


# Inicializar presets al cargar el módulo
NestingPresetManager.initialize_defaults()
