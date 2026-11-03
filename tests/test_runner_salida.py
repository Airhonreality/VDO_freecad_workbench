"""El runner rechaza una salida no escribible con código 2 y sin excepción (segfault al cerrar).

Causa medida: con VDO_TEST_OUT apuntando a un directorio, la escritura del resumen fallaba
al final con una excepción que salía de main() sin liberar los widgets Qt. freecadcmd
terminaba con abort (134) o SIGSEGV (139). Ahora se valida antes de ejecutar la suite.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUNNER = RAIZ / "tools" / "run_tests.py"


def _ejecutar_runner(salida: str) -> subprocess.CompletedProcess:
    entorno = dict(os.environ, VDO_TEST_DIR="tests", VDO_TEST_OUT=salida)
    # Python puro, no freecadcmd: la validación ocurre antes de importar FreeCAD.
    return subprocess.run(
        ["python3", "-I", str(RUNNER)],
        env=entorno, capture_output=True, text=True, timeout=120, cwd=str(RAIZ),
    )


class RunnerSalidaTests(unittest.TestCase):

    def test_directorio_como_salida_sale_con_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _ejecutar_runner(tmp)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("es un directorio", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_padre_inexistente_sale_con_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = os.path.join(tmp, "no_existe", "out.txt")
            r = _ejecutar_runner(salida)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("el directorio padre no existe", r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
