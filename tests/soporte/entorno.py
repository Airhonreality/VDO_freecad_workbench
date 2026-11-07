"""Prepara sys.path para ejecutar un test directamente (fuera del runner).

Importar este modulo antes que el paquete freecad.vdo añade la raiz del
repositorio a sys.path. Lo usan los tests que pueden ejecutarse como
``python3 tests/test_x.py``; el runner ya lo hace por su cuenta.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
