# -*- coding: utf-8 -*-
"""Runner único de la suite VDO. Sirve en modo puro y en modo FreeCAD.

Variables de entorno:
  VDO_TEST_DIR  carpeta donde buscar test_*.py (obligatoria)
  VDO_TEST_OUT  fichero de salida con una línea por test: "<estado> <id>" (obligatoria)

Modo puro:      VDO_TEST_DIR=tests VDO_TEST_OUT=out.txt python3 tools/run_tests.py
Modo FreeCAD:   VDO_TEST_DIR=tests VDO_TEST_OUT=out.txt freecadcmd tools/run_tests.py
  (con flatpak: flatpak run --command=freecadcmd org.freecad.FreeCAD tools/run_tests.py)

Sale con código 0 aunque haya fallos: el resultado va al fichero de salida y al resumen.
"""

import os
import sys
import unittest


def _ids(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from _ids(t)
        else:
            yield t


class _Registro(unittest.TestResult):
    """Registra qué tests llegaron a ejecutarse (startTest). Los que no, no pasaron ni fallaron."""

    def __init__(self):
        super().__init__()
        self.iniciados = set()

    def startTest(self, test):
        self.iniciados.add(test.id())
        super().startTest(test)


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directorio = os.path.join(raiz, os.environ["VDO_TEST_DIR"])
    salida = os.path.join(raiz, os.environ["VDO_TEST_OUT"])
    sys.path.insert(0, raiz)
    sys.path.insert(0, directorio)

    # FreeCADCmd no define FreeCAD.__spec__; importlib.util.find_spec() falla sin él y
    # tumba varios módulos de prueba al importarse. Se define aquí, una vez, para todos.
    try:
        import FreeCAD as _fc
        if getattr(_fc, "__spec__", None) is None:
            import importlib.machinery
            _fc.__spec__ = importlib.machinery.ModuleSpec("FreeCAD", None)
    except ImportError:
        pass

    descubiertos = unittest.defaultTestLoader.discover(directorio, pattern="test_*.py", top_level_dir=directorio)
    # unittest vacía la suite al ejecutarla: los ids se recogen antes
    todos = [t.id() for t in _ids(descubiertos)]
    resultado = _Registro()
    descubiertos.run(resultado)

    # Cada entrada de failures/errors se escribe tal cual (sin colapsar ids repetidos,
    # p. ej. _ErrorHolder de setUpClass). Así el número de líneas coincide con el resumen.
    def _ultima(tb):
        lineas = [l for l in tb.strip().splitlines() if l.strip()]
        return lineas[-1] if lineas else ""
    filas = [("FALLO", t.id(), _ultima(tb)) for t, tb in resultado.failures]
    filas += [("ERROR", t.id(), _ultima(tb)) for t, tb in resultado.errors]
    malos = {t.id() for t, _ in resultado.failures + resultado.errors}
    omitidos = {t.id() for t, _ in resultado.skipped}
    for tid in todos:
        if tid in malos:
            continue
        if tid in omitidos:
            filas.append(("SKIP", tid, ""))
        elif tid in resultado.iniciados:
            filas.append(("OK", tid, ""))
        else:
            # setUpClass/setUpModule falló o saltó: el test no llegó a ejecutarse
            filas.append(("NO_EJECUTADO", tid, ""))

    filas.sort(key=lambda f: f[1])
    with open(salida, "w", encoding="utf-8") as f:
        for estado, tid, detalle in filas:
            f.write("{} {}{}\n".format(estado, tid, (" :: " + detalle[:300]) if detalle else ""))
        f.write("\nRESUMEN ejecutados={} fallos={} errores={} skip={}\n".format(
            resultado.testsRun, len(resultado.failures), len(resultado.errors), len(resultado.skipped)))
    print("RESUMEN ejecutados={} fallos={} errores={} skip={} -> {}".format(
        resultado.testsRun, len(resultado.failures), len(resultado.errors), len(resultado.skipped), salida))


main()
