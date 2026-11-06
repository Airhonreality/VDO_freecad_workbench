"""Test de arquitectura AST (F19.4).

Verifica las reglas de capa del dominio:
- ui/ no importa core, cad ni app.vdo_api.
- ui/ no contiene asignaciones a atributos de objetos FreeCAD ni llamadas a
  addObject()/recompute().
- core/ no importa app, ui ni cad.
- app/ no importa ui.
- cad/ no importa ui ni app.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

# tests/test_arquitectura.py -> tests/ -> raíz del repo (dos niveles, no tres).
# Con tres niveles ROOT era el directorio padre del repo: los escaneos no
# encontraban archivos y los tests pasaban en vacío (F19.2-ter).
ROOT = Path(__file__).resolve().parent.parent
FREECAD = ROOT / "freecad"
UI = FREECAD / "vdo" / "ui"
CORE = FREECAD / "vdo" / "core"
CAD = FREECAD / "vdo" / "cad"
APP = FREECAD / "vdo" / "app"


def _py_files(base: Path):
    # Un escaneo vacío no es un "cumple": si la carpeta no existe o no tiene
    # archivos, el test debe fallar y no pasar en vacío.
    if not base.is_dir():
        raise AssertionError(f"Carpeta de capa inexistente: {base}")
    archivos = sorted(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)
    if not archivos:
        raise AssertionError(f"Sin archivos .py en la capa: {base}")
    return archivos


def _texto(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _tiene_import_prohibido(src: str, prohibidos: tuple[str, ...]) -> bool:
    try:
        t = ast.parse(src)
    except SyntaxError:
        return False
    for nodo in ast.walk(t):
        if isinstance(nodo, ast.ImportFrom):
            if nodo.module:
                for p in prohibidos:
                    if nodo.module.startswith(p):
                        return True
        elif isinstance(nodo, ast.Import):
            for alias in nodo.names:
                for p in prohibidos:
                    if alias.name.startswith(p):
                        return True
    return False


def _tiene_escritura_freecad(src: str) -> bool:
    """Detecta asignaciones a objetos FreeCAD o llamadas addObject/recompute."""
    patrones = (
        ".addObject(", ".recompute()", ".recompute (",
    )
    for pat in patrones:
        if pat in src:
            return True
    try:
        t = ast.parse(src)
    except SyntaxError:
        return False
    for nodo in ast.walk(t):
        if isinstance(nodo, ast.Attribute) and nodo.attr in (
            "Ancho", "Alto", "Largo",
        ):
            # Solo cuenta si es asignación (target de Assign)
            pass
    import re
    if re.search(r"\.(Ancho|Alto|Largo)\s*=", src):
        return True
    if re.search(r"\bApp\.\w+", src):
        return True
    return bool(re.search(r"\bPart\.\w+", src))


class CapasTests(unittest.TestCase):
    def test_ui_no_importa_core_cad_app_api(self):
        # D-31 (MN-03): ui/ SÍ puede importar core y cad. Prohibido: app
        # (eliminado, MN-01) y app.vdo_api.
        prohibidos = (
            "freecad.vdo.app",
            "freecad.vdo.app.vdo_api",
        )
        violaciones = []
        for p in _py_files(UI):
            src = _texto(p)
            if _tiene_import_prohibido(src, prohibidos):
                violaciones.append(str(p.relative_to(ROOT)))
        self.assertEqual(
            violaciones, [],
            f"ui/ importa app/app.vdo_api (prohibido por MN-03/MN-01): {violaciones}",
        )

    def test_ui_no_escritura_freecad(self):
        violaciones = []
        for p in _py_files(UI):
            src = _texto(p)
            if _tiene_escritura_freecad(src):
                violaciones.append(str(p.relative_to(ROOT)))
        self.assertEqual(
            violaciones, [],
            f"ui/ escribe en FreeCAD: {violaciones}",
        )

    def test_core_no_importa_app_ui_cad(self):
        prohibidos = ("freecad.vdo.app", "freecad.vdo.ui", "freecad.vdo.cad")
        violaciones = []
        for p in _py_files(CORE):
            src = _texto(p)
            if _tiene_import_prohibido(src, prohibidos):
                violaciones.append(str(p.relative_to(ROOT)))
        self.assertEqual(
            violaciones, [],
            f"core/ importa app/ui/cad: {violaciones}",
        )

    def test_app_no_importa_ui(self):
        # D-25: MN-01 elimina app/. Si la capa no existe o no tiene .py, la
        # regla se cumple por ausencia (no se pasa en vacío sobre una carpeta
        # que existe). Si app/ existe con .py, se aplica la regla completa.
        if not APP.is_dir() or not any(
                p for p in APP.rglob("*.py") if "__pycache__" not in p.parts):
            print("\n[D-25] freecad/vdo/app ausente o sin .py: "
                  "test_app_no_importa_ui cumplido por ausencia de capa.")
            return
        prohibidos = ("freecad.vdo.ui",)
        violaciones = []
        for p in _py_files(APP):
            src = _texto(p)
            if _tiene_import_prohibido(src, prohibidos):
                violaciones.append(str(p.relative_to(ROOT)))
        self.assertEqual(
            violaciones, [],
            f"app/ importa ui: {violaciones}",
        )

    def test_cad_no_importa_ui_app(self):
        prohibidos = ("freecad.vdo.ui", "freecad.vdo.app")
        violaciones = []
        for p in _py_files(CAD):
            src = _texto(p)
            if _tiene_import_prohibido(src, prohibidos):
                violaciones.append(str(p.relative_to(ROOT)))
        self.assertEqual(
            violaciones, [],
            f"cad/ importa ui/app: {violaciones}",
        )


if __name__ == "__main__":
    unittest.main()
