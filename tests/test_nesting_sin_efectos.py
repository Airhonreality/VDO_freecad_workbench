"""Regresion D4: importar core/nesting_presets no escribe preferencias de FreeCAD.

El modulo no debe escribir configuracion del usuario al cargarse. La
inicializacion de presets por defecto es explicita (la llama el workflow de
Nesting al abrirse). Cada caso corre en un proceso hijo limpio, porque otras
pruebas del runner dejan mocks de FreeCAD en sys.modules.

El mock de FreeCAD registra cada llamada a SetString. La prueba exige cero
escrituras al importar el modulo con las preferencias vacias.
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SCRIPT_HIJO = r"""
import json, sys, types
raiz = {raiz!r}

escrituras = []

class _Grupo:
    def __init__(self):
        self.valores = {{}}
    def GetString(self, clave, defecto=""):
        return self.valores.get(clave, defecto)
    def SetString(self, clave, valor):
        escrituras.append((clave, valor))
        self.valores[clave] = valor
    def RemString(self, clave):
        self.valores.pop(clave, None)

grupo = _Grupo()
fc = types.ModuleType("FreeCAD")
fc.ParamGet = lambda ruta: grupo
fc.Console = types.SimpleNamespace(PrintMessage=lambda texto: None)
sys.modules["FreeCAD"] = fc

pkg = types.ModuleType("freecad")
pkg.__path__ = [raiz + "/freecad"]
sys.modules["freecad"] = pkg

from freecad.vdo.core import nesting_presets  # noqa: F401

print("NESTING_SIN_EFECTOS " + json.dumps({{
    "escrituras": len(escrituras),
    "prefs_presets": grupo.GetString("Presets", ""),
}}))
"""


def _python() -> str:
    """Interprete de Python para el hijo. Bajo freecadcmd, sys.executable es freecadcmd."""
    if os.path.basename(sys.executable).startswith("python"):
        return sys.executable
    return shutil.which("python3") or "python3"


def _importar_en_hijo() -> dict:
    codigo = _SCRIPT_HIJO.format(raiz=RAIZ)
    r = subprocess.run([_python(), "-I", "-c", codigo],
                       capture_output=True, text=True, timeout=120)
    for linea in r.stdout.splitlines():
        if linea.startswith("NESTING_SIN_EFECTOS "):
            return json.loads(linea[len("NESTING_SIN_EFECTOS "):])
    raise AssertionError(
        f"el modulo no cargo (rc={r.returncode}): {r.stderr[-600:]}")


class NestingSinEfectosAlImportarTests(unittest.TestCase):

    def test_importar_no_escribe_preferencias(self):
        res = _importar_en_hijo()
        self.assertEqual(res["escrituras"], 0,
                         "importar core/nesting_presets escribio en las preferencias")
        self.assertEqual(res["prefs_presets"], "")


if __name__ == "__main__":
    unittest.main()
