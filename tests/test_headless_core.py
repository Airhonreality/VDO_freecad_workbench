# -*- coding: utf-8 -*-
"""Compuerta headless de la Fase 2 (PLAN_CONVERSION_WORKBENCH_VDO.md, sección 6).

Importar todos los módulos de freecad/vdo/core/ no debe cargar FreeCADGui ni PySide.

La comprobación se hace en un PROCESO FreeCAD HIJO limpio (sys.executable -c ...).
Motivo: test_cajon_core sustituye sys.modules["FreeCAD"] por un mock al importarse, y
ese mock contaminaría cualquier comprobación hecha en el mismo proceso.

Requiere FreeCAD (freecadcmd). Sin FreeCAD la prueba se omite.
"""

import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

def _freecad_real_en_hijo():
    """¿Hay un FreeCAD real? Se pregunta a un proceso hijo: en el padre, test_cajon_core puede
    haber dejado un mock en sys.modules y "import FreeCAD" daría falso positivo."""
    r = subprocess.run([sys.executable, "-c", "import FreeCAD"], capture_output=True, text=True, timeout=300)
    return r.returncode == 0

# Script que corre en el hijo: importa el motor y lista lo GUI que apareció durante la importación.
_SCRIPT_HIJO = r"""
import importlib, json, os, sys
raiz = {raiz!r}
sys.path.insert(0, raiz)
import FreeCAD  # noqa
antes = set(sys.modules)
carpeta = os.path.join(raiz, "freecad", "vdo", "core")
for f in sorted(os.listdir(carpeta)):
    if f.startswith("vdo_") and f.endswith(".py"):
        importlib.import_module("freecad.vdo.core." + f[:-3])
nuevos = set(sys.modules) - antes
prohibidos = sorted(m for m in nuevos if m.split(".")[0].startswith(("FreeCADGui", "PySide")))
print("HEADLESS_RESULT " + json.dumps(prohibidos))
"""


def _ejecutar_hijo():
    codigo = _SCRIPT_HIJO.format(raiz=RAIZ)
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, timeout=300)
    for linea in r.stdout.splitlines():
        if linea.startswith("HEADLESS_RESULT "):
            return json.loads(linea[len("HEADLESS_RESULT "):]), r
    return None, r


class HeadlessCoreTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not _freecad_real_en_hijo():
            raise unittest.SkipTest("requiere FreeCAD real (freecadcmd)")

    def test_core_no_carga_gui_ni_pyside(self):
        prohibidos, r = _ejecutar_hijo()
        self.assertIsNotNone(prohibidos, f"El proceso hijo no terminó bien (rc={r.returncode}): {r.stderr[-400:]}")
        self.assertEqual(prohibidos, [], f"El motor cargó GUI/Qt: {prohibidos}")

    def test_namespace_freecad_incluye_paquete_del_repo(self):
        import freecad
        # Mod/VDO puede ser un enlace simbólico: se compara por ruta real.
        rutas = [os.path.realpath(p) for p in freecad.__path__]
        self.assertIn(os.path.realpath(os.path.join(RAIZ, "freecad")), rutas)

    def test_freecad_no_tiene_init_en_el_repo(self):
        # Si existiera freecad/__init__.py, el paquete del repo sombrearía al de FreeCAD y a los addons.
        self.assertFalse(os.path.exists(os.path.join(RAIZ, "freecad", "__init__.py")))


if __name__ == "__main__":
    unittest.main()
