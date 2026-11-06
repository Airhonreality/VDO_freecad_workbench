"""Una sola ruta para el catálogo de herrajes (M2, H-21).

Antes, ui/hardware_manager.py calculaba su propia ruta (ui/vdo_hardware_catalog.json),
que no existe: leía un catálogo vacío y guardaba en un fichero que el hub nunca lee.
La ruta vive ahora en core/hardware_hub.CATALOGO_PATH y la UI la importa.
"""

from __future__ import annotations

import ast
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANAGER = ROOT / "freecad" / "vdo" / "ui" / "hardware_manager.py"


class CatalogoHerrajesRutaTests(unittest.TestCase):

    def test_ruta_unica_apunta_a_un_fichero_existente(self):
        from freecad.vdo.core import hardware_hub as H

        self.assertTrue(
            os.path.isfile(H.CATALOGO_PATH),
            f"CATALOGO_PATH no existe: {H.CATALOGO_PATH}",
        )

    def test_la_ui_no_define_su_propia_ruta(self):
        arbol = ast.parse(MANAGER.read_text(encoding="utf-8"), filename=str(MANAGER))
        definiciones = [
            n.targets[0].id
            for n in arbol.body
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and "CATALOGO" in n.targets[0].id.upper()
        ]
        self.assertEqual(definiciones, [], "la UI define una ruta de catálogo propia")
        # Los textos (docstring, mensajes) pueden citar el nombre; la UI no debe construir la ruta.
        self.assertNotIn("os.path.join", MANAGER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
