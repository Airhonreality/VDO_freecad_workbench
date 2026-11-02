"""Compuerta de la Fase 3 (PLAN_CONVERSION_WORKBENCH_VDO.md, sección 6).

- Estática (corre en modo puro): ningún exec() en el paquete ni en InitGui.py/Init.py.
- FreeCAD (proceso hijo limpio): los comandos construyen, sus iconos existen y los de
  creación producen objetos en un documento real, sin GUI.
"""

import os
import re
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_RE_EXEC = re.compile(r"(?<![\w.])exec\(")  # exec() builtin; no .exec() de Qt


def _archivos_codigo():
    for base, _dirs, ficheros in os.walk(os.path.join(RAIZ, "freecad")):
        for f in ficheros:
            if f.endswith(".py"):
                yield os.path.join(base, f)
    yield os.path.join(RAIZ, "InitGui.py")
    yield os.path.join(RAIZ, "Init.py")


class SinExecTests(unittest.TestCase):

    def test_ningun_exec_builtin_en_el_codigo(self):
        hallazgos = []
        for ruta in _archivos_codigo():
            with open(ruta, encoding="utf-8") as f:
                for n, linea in enumerate(f, 1):
                    if _RE_EXEC.search(linea) and not linea.lstrip().startswith("#"):
                        hallazgos.append(f"{os.path.relpath(ruta, RAIZ)}:{n}: {linea.strip()}")
        self.assertEqual(hallazgos, [], "Se encontró exec() builtin:\n" + "\n".join(hallazgos))


_HIJO = r"""
import os, sys
raiz = {raiz!r}
import FreeCAD as App
from freecad.vdo import commands as C
import json
out = {{}}
out["ids"] = sorted(C.COMANDOS)
out["iconos"] = {{n: os.path.exists(c().GetResources()["Pixmap"]) for n, c in C.COMANDOS.items()}}
out["barras_ok"] = all(c in C.COMANDOS for cmds in C.BARRAS.values() for c in cmds)
doc = App.newDocument("T_cmd")
C.CmdPanelEstandar().Activated()
out["panel"] = sorted(o.Name for o in doc.Objects)
out["panel_n"] = len(doc.Objects)
C.CmdZocalo().Activated()
out["zocalo"] = len(doc.Objects)
print("CMD_RESULT " + json.dumps(out))
"""


def _freecad_real_en_hijo():
    r = subprocess.run([sys.executable, "-c", "import FreeCAD"], capture_output=True, text=True, timeout=300)
    return r.returncode == 0


class ComandosFreeCADTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not _freecad_real_en_hijo():
            raise unittest.SkipTest("requiere FreeCAD real (freecadcmd)")
        import json
        r = subprocess.run([sys.executable, "-c", _HIJO.format(raiz=RAIZ)],
                           capture_output=True, text=True, timeout=600)
        cls.resultado = None
        for linea in r.stdout.splitlines():
            if linea.startswith("CMD_RESULT "):
                cls.resultado = json.loads(linea[len("CMD_RESULT "):])
        cls.salida_error = r.stderr[-600:]

    def setUp(self):
        self.assertIsNotNone(self.resultado, f"El proceso hijo no devolvió resultado: {self.salida_error}")

    def test_comandos_registrados(self):
        self.assertEqual(len(self.resultado["ids"]), 15)

    def test_todos_los_iconos_existen(self):
        faltan = [n for n, ok in self.resultado["iconos"].items() if not ok]
        self.assertEqual(faltan, [])

    def test_barras_solo_referencian_comandos_registrados(self):
        self.assertTrue(self.resultado["barras_ok"])

    def test_panel_estandar_crea_hoja_y_panel(self):
        nombres = self.resultado["panel"]
        self.assertIn("Params_Melamina", nombres)
        self.assertIn("Params", nombres)
        self.assertIn("Panel_Base", nombres)

    def test_zocalo_anade_objetos(self):
        self.assertGreater(self.resultado["zocalo"], self.resultado["panel_n"])


if __name__ == "__main__":
    unittest.main()
