"""Golden de MODULE_SPECS desde b78de04 (D-17).

tests/golden/module_specs.json es MODULE_SPECS tal como existe en b78de04, con el orden
de claves original. Procedencia en docs/metricas/goldens_origen.md.
La prueba compara el valor vigente (y el orden de claves) con ese golden.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "tests" / "golden" / "module_specs.json"


def _vigente() -> dict:
    from freecad.vdo.core import module_specs as MS

    return MS.MODULE_SPECS


class ModuleSpecsGoldenTests(unittest.TestCase):

    def test_golden_existe_con_siete_modulos(self):
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(len(golden), 7)

    def test_valor_y_orden_de_claves_iguales_al_golden(self):
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        vigente = _vigente()
        self.assertEqual(list(vigente.keys()), list(golden.keys()))
        # El golden está en JSON: las tuplas de origen (p. ej. 'factory') son listas.
        # Se normalizan ambos lados igual, para no comparar tupla con lista.
        self.assertEqual(json.loads(json.dumps(vigente)), golden)


if __name__ == "__main__":
    unittest.main()
