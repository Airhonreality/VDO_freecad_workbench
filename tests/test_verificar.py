"""Tests del verificador (F19-D12). Prueban las funciones REALES de
tools/auditoria/verificar.py, no copias de las reglas.

Cada regla tiene fixtures con código a propósito correcto o incorrecto:
- R5: una variable local no cuenta; una asignación de nivel módulo sí.
- R7: un ``except … pass`` cuenta; un ``except`` con ``raise`` no.
- R9: un método no cuenta como definición de módulo; un uso por atributo
  (``modulo.funcion()``) SÍ cuenta como uso (regresión: la regla anterior lo
  marcaba como no usado).
"""

from __future__ import annotations

import importlib.util
import pathlib
import unittest

_RUTA_VERIFICAR = (pathlib.Path(__file__).resolve().parent.parent
                   / "tools" / "auditoria" / "verificar.py")
_spec = importlib.util.spec_from_file_location("verificar_vdo", _RUTA_VERIFICAR)
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

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
    def metodo_clase(self):   # método: NO debe contar como def de módulo
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


class TestR5EstadoInmutable(unittest.TestCase):
    def test_variable_local_no_cuenta(self):
        self.assertEqual(V._asignaciones_mutables_modulo(CODIGO_R5_LOCAL), [])

    def test_constante_mayusculas_y_all_no_cuentan(self):
        self.assertEqual(V._asignaciones_mutables_modulo("MI_CONSTANTE = 1\n__all__ = []\n"), [])

    def test_asignacion_de_modulo_si_cuenta(self):
        self.assertEqual(V._asignaciones_mutables_modulo("estado = {}\n"), [(1, "estado")])

    def test_asignacion_anotada_de_modulo_si_cuenta(self):
        self.assertEqual(V._asignaciones_mutables_modulo("cache: dict = {}\n"), [(1, "cache")])


class TestR7Errores(unittest.TestCase):
    def test_except_pass_se_cuenta(self):
        self.assertEqual(V._except_pass_en(CODIGO_R7_EXCEPT_PASS), 1)

    def test_except_con_raise_no_se_cuenta(self):
        self.assertEqual(V._except_pass_en(CODIGO_R7_OK), 0)

    def test_except_exception_se_cuenta_con_cualquier_cuerpo(self):
        self.assertEqual(V._except_exception_en(CODIGO_R7_OK.replace("ValueError", "Exception")), 1)
        self.assertEqual(V._except_exception_en(CODIGO_R7_OK), 0)


class TestR9DefsNoUsadas(unittest.TestCase):
    def test_metodo_no_cuenta_como_def_modulo(self):
        nombres = [n for n, _ in V._definiciones_modulo(CODIGO_R9_METODO)]
        self.assertEqual(nombres, ["_MiClase"])

    def test_funcion_sin_referencias_se_reporta(self):
        defs = {"a.py": "def foo():\n    pass\n"}
        self.assertEqual(V._defs_no_usadas(defs, ["x = 1\n"]), ["a.py:foo"])

    def test_uso_por_atributo_cuenta(self):
        defs = {"a.py": "def foo():\n    pass\n"}
        self.assertEqual(V._defs_no_usadas(defs, ["import a\na.foo()\n"]), [])

    def test_uso_por_import_from_cuenta(self):
        defs = {"a.py": "def foo():\n    pass\n"}
        self.assertEqual(V._defs_no_usadas(defs, ["from a import foo\n"]), [])

    def test_uso_en_el_mismo_archivo_cuenta(self):
        codigo = "def foo():\n    pass\n\nfoo()\n"
        self.assertEqual(V._defs_no_usadas({"a.py": codigo}, [codigo]), [])

    def test_referencia_por_cadena_cuenta(self):
        defs = {"a.py": "def foo():\n    pass\n"}
        self.assertEqual(V._defs_no_usadas(defs, ['TABLA = {"accion": "foo"}\n']), [])

    def test_privada_sin_referencias_se_reporta(self):
        defs = {"a.py": "def _priv():\n    pass\n"}
        self.assertEqual(V._defs_no_usadas(defs, ["x = 1\n"]), ["a.py:_priv"])


if __name__ == "__main__":
    unittest.main()
