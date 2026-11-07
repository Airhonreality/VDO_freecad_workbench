"""Regresion E1: los logs del paquete llegan a la consola de FreeCAD.

Los modulos de core/ registran con logging.getLogger(__name__) y no configuran
handler. Sin configuracion, los WARNING salen por stderr y no llegan a
App.Console, donde el usuario mira. La prueba ejecuta Init.py (el arranque del
workbench) en un proceso hijo con un mock de FreeCAD que registra las llamadas
a App.Console, emite un warning de core y exige que llegue a PrintWarning.

Un proceso hijo limpio, porque otras pruebas del runner dejan mocks de FreeCAD
en sys.modules.
"""

import json
import os
import shutil
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SCRIPT_HIJO = r"""
import json, logging, runpy, sys, types
raiz = {raiz!r}

llamadas = []

def _registrador(nivel):
    def _f(texto):
        llamadas.append((nivel, texto))
    return _f

consola = types.SimpleNamespace(
    PrintMessage=_registrador("PrintMessage"),
    PrintWarning=_registrador("PrintWarning"),
    PrintError=_registrador("PrintError"),
    PrintLog=_registrador("PrintLog"),
)
fc = types.ModuleType("FreeCAD")
fc.Console = consola
sys.modules["FreeCAD"] = fc

pkg = types.ModuleType("freecad")
pkg.__path__ = [raiz + "/freecad"]
sys.modules["freecad"] = pkg

# Arranque del workbench (fase de consola).
runpy.run_path(raiz + "/Init.py", run_name="Init")
n_arranque = len(llamadas)

logging.getLogger("freecad.vdo.core.x").warning("prueba")

print("LOG_CONSOLA " + json.dumps({{
    "n_arranque": n_arranque,
    "llamadas": llamadas,
}}))
"""


def _python() -> str:
    """Interprete de Python para el hijo. Bajo freecadcmd, sys.executable es freecadcmd."""
    if os.path.basename(sys.executable).startswith("python"):
        return sys.executable
    return shutil.which("python3") or "python3"


def _ejecutar_arranque() -> dict:
    codigo = _SCRIPT_HIJO.format(raiz=RAIZ)
    r = subprocess.run([_python(), "-I", "-c", codigo],
                       capture_output=True, text=True, timeout=120)
    for linea in r.stdout.splitlines():
        if linea.startswith("LOG_CONSOLA "):
            return json.loads(linea[len("LOG_CONSOLA "):])
    raise AssertionError(
        f"el arranque no termino (rc={r.returncode}): {r.stderr[-600:]}")


class LogsEnConsolaFreeCADTests(unittest.TestCase):

    def test_warning_de_core_llega_a_print_warning(self):
        res = _ejecutar_arranque()
        avisos = [t for nivel, t in res["llamadas"] if nivel == "PrintWarning"]
        self.assertTrue(any("prueba" in t for t in avisos),
                        "un warning de freecad.vdo.core no llego a App.Console.PrintWarning: "
                        f"{res['llamadas']}")


if __name__ == "__main__":
    unittest.main()
