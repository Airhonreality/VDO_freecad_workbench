"""Test de humo para tools/vdo_optimizador_cli.py (nivel 1)."""

try:
    from tests.soporte import entorno as _entorno
except ImportError:
    from soporte import entorno as _entorno

import os
import sys
import tempfile
import unittest

from tools.vdo_optimizador_cli import _parse_board

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestOptimizadorCLI(unittest.TestCase):
    """Pruebas de humo del CLI del optimizador."""

    def test_parse_board_valido(self):
        """Formato ANCHOxALTO se parsea correctamente."""
        w, h = _parse_board("2440x1830")
        self.assertEqual(w, 2440.0)
        self.assertEqual(h, 1830.0)

    def test_parse_board_con_decimales(self):
        """Soporta decimales."""
        w, h = _parse_board("1200.5x900.25")
        self.assertEqual(w, 1200.5)
        self.assertEqual(h, 900.25)

    def test_parse_board_invalido(self):
        """Formato invalido lanza ArgumentTypeError."""
        from argparse import ArgumentTypeError
        with self.assertRaises(ArgumentTypeError):
            _parse_board("invalido")

if __name__ == "__main__":
    unittest.main()
