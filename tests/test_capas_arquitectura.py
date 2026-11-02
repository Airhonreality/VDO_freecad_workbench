"""Regla de capas (docs/REVISION_ARQUITECTURA_CAPAS.md, sección 1). Corre en modo puro.

El motor (freecad/vdo/core/) no puede importar la interfaz ni FreeCADGui/Qt, ni a nivel de
módulo ni dentro de funciones. La interfaz depende del motor, nunca al revés.
La comprobación es estática (AST): cubre también los imports diferidos, que son los que
ocultaban la dependencia circular.
"""

import ast
import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(RAIZ, "freecad", "vdo", "core")
PROHIBIDOS_EN_CORE = ("freecad.vdo.ui", "FreeCADGui", "freecad.vdo.qt_compat", "PySide", "PySide2", "PySide6")


def _imports(ruta):
    with open(ruta, encoding="utf-8") as f:
        arbol = ast.parse(f.read(), filename=ruta)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for a in nodo.names:
                yield nodo.lineno, a.name
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield nodo.lineno, nodo.module


class CapasTests(unittest.TestCase):

    def test_core_no_importa_interfaz_ni_qt(self):
        hallazgos = []
        for base, _dirs, ficheros in os.walk(CORE):
            for f in ficheros:
                if not f.endswith(".py"):
                    continue
                ruta = os.path.join(base, f)
                for linea, modulo in _imports(ruta):
                    if any(modulo == p or modulo.startswith(p + ".") for p in PROHIBIDOS_EN_CORE):
                        hallazgos.append(f"{os.path.relpath(ruta, RAIZ)}:{linea} importa {modulo}")
        self.assertEqual(hallazgos, [], "El motor depende de la interfaz:\n" + "\n".join(hallazgos))

    def test_registro_de_ui_no_esta_en_core(self):
        # F5 elimino vdo_ui_registry de core; las vistas se adjuntan desde app/.
        self.assertFalse(os.path.isfile(os.path.join(CORE, "vdo_ui_registry.py")))


if __name__ == "__main__":
    unittest.main()
