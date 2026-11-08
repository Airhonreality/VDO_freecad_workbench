"""Snapshot de las cadenas de estilo de tema_estilos (F-UI-0)."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from freecad.vdo.ui import tema_estilos

RAIZ = Path(__file__).resolve().parent.parent
SNAPSHOT = RAIZ / "tests" / "fixtures" / "tema_estilos_snapshot.json"


class TemaEstilosCadenasTests(unittest.TestCase):

    def test_cadenas_identicas_al_snapshot(self):
        datos = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        for nombre, esperado in datos.items():
            if nombre.startswith("__"):
                continue
            with self.subTest(cadena=nombre):
                self.assertEqual(getattr(tema_estilos, nombre), esperado)
        casos = {
            "__estilo_boton_defaults__": tema_estilos.estilo_boton(),
            "__estilo_boton_custom__": tema_estilos.estilo_boton("#112233", "#445566", "#778899"),
            "__estilo_breadcrumb_true__": tema_estilos.estilo_breadcrumb("x", True),
            "__estilo_breadcrumb_false__": tema_estilos.estilo_breadcrumb("x", False),
        }
        for nombre, real in casos.items():
            with self.subTest(cadena=nombre):
                self.assertEqual(real, datos[nombre])

    def test_fuente_sin_literales_de_color_ni_tamano(self):
        fuente = (RAIZ / "freecad" / "vdo" / "ui" / "tema_estilos.py").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,6}\b", fuente))
        self.assertIsNone(re.search(r"font-size:\s*\d+px", fuente))

    def test_fuente_como_maximo_400_lineas(self):
        fuente = (RAIZ / "freecad" / "vdo" / "ui" / "tema_estilos.py").read_text(encoding="utf-8")
        self.assertLessEqual(len(fuente.splitlines()), 400)


if __name__ == "__main__":
    unittest.main()
