"""Regresion B4 (P-10): core/nesting_presets.py debe cargar con y sin FreeCAD.

Cada caso se ejecuta en un proceso hijo limpio (sys.executable -I -c ...), porque
otras pruebas del runner dejan mocks de FreeCAD en sys.modules.

- Sin FreeCAD: el modulo carga y los presets por defecto son la tabla del modulo.
- Con FreeCAD (simulado con un ParamGet en memoria): el modulo carga e inicializa
  la preferencia "Presets" con esa tabla.

El paquete ``freecad`` del sistema importa FreeCAD en su __init__, por eso el hijo
registra un paquete ``freecad`` de stub cuyo __path__ apunta al repo.
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
modo = {modo!r}

class _Grupo:
    def __init__(self):
        self.valores = {{}}
    def GetString(self, clave, defecto=""):
        return self.valores.get(clave, defecto)
    def SetString(self, clave, valor):
        self.valores[clave] = valor
    def RemString(self, clave):
        self.valores.pop(clave, None)

grupo = _Grupo()
if modo == "sin_freecad":
    sys.modules["FreeCAD"] = None
else:
    fc = types.ModuleType("FreeCAD")
    fc.ParamGet = lambda ruta: grupo
    fc.Console = types.SimpleNamespace(PrintMessage=lambda texto: None)
    sys.modules["FreeCAD"] = fc

pkg = types.ModuleType("freecad")
pkg.__path__ = [raiz + "/freecad"]
sys.modules["freecad"] = pkg

from freecad.vdo.core import nesting_presets as NP
M = NP.NestingPresetManager
tabla = json.loads(json.dumps(NP.DEFAULT_PRESETS))
M.initialize_defaults()
print("NESTING_RESULT " + json.dumps({{
    "presets": M.get_all_presets(),
    "nombres": M.get_preset_names(),
    "tabla_modulo": tabla,
    "prefs_presets": grupo.GetString("Presets", ""),
}}))
"""


def _python() -> str:
    """Interprete de Python para el hijo. Bajo freecadcmd, sys.executable es freecadcmd."""
    if os.path.basename(sys.executable).startswith("python"):
        return sys.executable
    return shutil.which("python3") or "python3"


def _ejecutar(modo: str) -> dict:
    codigo = _SCRIPT_HIJO.format(raiz=RAIZ, modo=modo)
    r = subprocess.run([_python(), "-I", "-c", codigo],
                       capture_output=True, text=True, timeout=120)
    for linea in r.stdout.splitlines():
        if linea.startswith("NESTING_RESULT "):
            return json.loads(linea[len("NESTING_RESULT "):])
    raise AssertionError(
        f"el modulo no cargo en modo {modo} (rc={r.returncode}): {r.stderr[-600:]}")


class NestingPresetsCargaTests(unittest.TestCase):

    def test_sin_freecad_carga_y_usa_presets_por_defecto(self):
        res = _ejecutar("sin_freecad")
        self.assertEqual(res["presets"], res["tabla_modulo"])
        self.assertEqual(res["nombres"], list(res["tabla_modulo"].keys()))
        self.assertIn("Estándar EN", res["nombres"])

    def test_sin_freecad_no_escribe_preferencias(self):
        res = _ejecutar("sin_freecad")
        self.assertEqual(res["prefs_presets"], "")

    def test_con_freecad_inicializa_preferencia_con_presets_por_defecto(self):
        res = _ejecutar("con_freecad")
        self.assertEqual(res["presets"], res["tabla_modulo"])
        guardado = json.loads(res["prefs_presets"])
        self.assertEqual(guardado["presets"], res["tabla_modulo"])
        self.assertEqual(guardado["list"], list(res["tabla_modulo"].keys()))


if __name__ == "__main__":
    unittest.main()
