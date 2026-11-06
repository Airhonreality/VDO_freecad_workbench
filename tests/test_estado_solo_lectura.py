"""Manifiesto de solo lectura (D-18): VDO_MANIFEST y _MANIFEST no admiten asignación.

Antes eran dicts mutables cargados al importar. Ahora son MappingProxyType de nivel superior.
"""

from __future__ import annotations

import unittest
from types import MappingProxyType


class EstadoSoloLecturaTests(unittest.TestCase):

    def test_manifiesto_del_nucleo_es_solo_lectura(self):
        from freecad.vdo.core import manifest as VM

        self.assertIsInstance(VM.VDO_MANIFEST, MappingProxyType)
        with self.assertRaises(TypeError):
            VM.VDO_MANIFEST["version"] = "x"
        self.assertIn("parametros_globales", VM.VDO_MANIFEST)

    def test_manifiesto_del_cajon_es_solo_lectura(self):
        from freecad.vdo.core import cajon_correderas as CD

        self.assertIsInstance(CD._MANIFEST, MappingProxyType)
        with self.assertRaises(TypeError):
            CD._MANIFEST["correderas_ocultas"] = {}


if __name__ == "__main__":
    unittest.main()
