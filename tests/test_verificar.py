"""Tests propios del verificador (F19-D12).

Fixtures pequeñas con código a propósito incorrecto:
- una variable local no debe contar en R5;
- un método no debe contar en R9;
- un ``except … pass`` debe contar en R7.
"""

from __future__ import annotations

import ast
import unittest

CODIGO_R5_LOCAL = """
MI_CONSTANTE = 1
__all__ = ["foo"]

def mi_funcion():
    x = 10      # variable local: NO debe contar como estado mutable
    y = 20
    return x + y
"""

CODIGO_R9_METODO = """
class _MiClase:
    def metodo_clase(self):   # método: NO debe contar como def de módulo no usada
        return 2
"""

CODIGO_R7_EXCEPT_PASS = """
def algo():
    try:
        pass
    except Exception:
        pass   # debe contar como except … pass
"""

CODIGO_R7_OK = """
def algo():
    try:
        pass
    except ValueError as e:
        raise
"""


def _tiene_asignacion_modulo_no_constante(codigo: str) -> bool:
    """Imita R5 corregida: solo asignaciones de tree.body, excluye mayúsculas y __all__."""
    t = ast.parse(codigo)
    for nodo in t.body:
        if isinstance(nodo, ast.Assign):
            for target in nodo.targets:
                if isinstance(target, ast.Name):
                    idn = target.id
                    if idn == "__all__" or idn.isupper():
                        continue
                    return True
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            idn = nodo.target.id
            if idn == "__all__" or idn.isupper():
                continue
            return True
    return False


def _tiene_def_modulo_no_privada(codigo: str) -> bool:
    """Imita R9 corregida: solo definiciones de tree.body."""
    t = ast.parse(codigo)
    for nodo in t.body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not nodo.name.startswith("_"):
                return True
    return False


def _tiene_except_pass(codigo: str) -> bool:
    """Imita R7: detecta except … pass."""
    t = ast.parse(codigo)
    for nodo in ast.walk(t):
        if isinstance(nodo, ast.Try):
            for handler in nodo.handlers:
                cuerpo = handler.body
                if (len(cuerpo) == 1 and isinstance(cuerpo[0], ast.Pass)):
                    return True
    return False


class TestVerificarR5(unittest.TestCase):
    def test_variable_local_no_cuenta_estado_mutable(self):
        self.assertFalse(_tiene_asignacion_modulo_no_constante(CODIGO_R5_LOCAL))

    def test_constante_mayusculas_no_cuenta(self):
        codigo = "MI_CONSTANTE = 1\n"
        self.assertFalse(_tiene_asignacion_modulo_no_constante(codigo))

    def test_all_no_cuenta(self):
        codigo = '__all__ = ["foo"]\n'
        self.assertFalse(_tiene_asignacion_modulo_no_constante(codigo))


class TestVerificarR9(unittest.TestCase):
    def test_metodo_no_cuenta_def_modulo(self):
        self.assertFalse(_tiene_def_modulo_no_privada(CODIGO_R9_METODO))

    def test_funcion_modulo_si_cuenta(self):
        codigo = "def foo():\n    pass\n"
        self.assertTrue(_tiene_def_modulo_no_privada(codigo))


class TestVerificarR7(unittest.TestCase):
    def test_except_pass_se_cuenta(self):
        self.assertTrue(_tiene_except_pass(CODIGO_R7_EXCEPT_PASS))

    def test_except_con_raise_no_se_cuenta(self):
        self.assertFalse(_tiene_except_pass(CODIGO_R7_OK))


if __name__ == "__main__":
    unittest.main()
