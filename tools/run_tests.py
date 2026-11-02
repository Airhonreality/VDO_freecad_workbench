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


def _leer_omisiones(raiz):
    """Lee tests/soporte/omisiones.txt y devuelve un conjunto de ids a omitir.

    Formato de cada línea: <nombre_archivo>|<motivo>|<nivel>
    Se hace match por sufijo del id del test (ej. test_foo.py::Clase::metodo
    coincide con test_foo.py).
    """
    omisiones = set()
    path = os.path.join(raiz, "tests", "soporte", "omisiones.txt")
    if not os.path.isfile(path):
        return omisiones
    with open(path, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split("|")
            if partes:
                omisiones.add(partes[0].strip())
    return omisiones


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
    omisiones = _leer_omisiones(raiz)
    resultado = _Registro()
    descubiertos.run(resultado)

    # Cada entrada de failures/errors se escribe tal cual (sin colapsar ids repetidos,
    # p. ej. _ErrorHolder de setUpClass). Así el número de líneas coincide con el resumen.
    def _ultima(tb):
        lineas = [l for l in tb.strip().splitlines() if l.strip()]
        return lineas[-1] if lineas else ""
    filas = [("FALLO", t.id(), _ultima(tb)) for t, tb in resultado.failures]
    # Reclasificar como SKIP los errores de tests listados en omisiones.txt
    # (fallan por falta de FreeCAD/Qt, no por defecto de código).
    errores_reclasificados = []
    errores_reales = []
    for t, tb in resultado.errors:
        tid = t.id()
        # _FailedTest tiene id "unittest.loader._FailedTest.<modulo>";
        # los tests normales tienen "modulo.Clase.metodo".
        partes = tid.split(".")
        if len(partes) >= 3 and partes[0] == "unittest" and partes[1] == "loader":
            nombre_modulo = partes[-1]
        else:
            nombre_modulo = partes[0]
        nombre_archivo = os.path.basename(nombre_modulo + ".py")
        if nombre_archivo in omisiones:
            errores_reclasificados.append((tid, _ultima(tb)))
        else:
            errores_reales.append((t, tb))
    filas = [("FALLO", t.id(), _ultima(tb)) for t, tb in resultado.failures]
    filas += [("ERROR", t.id(), _ultima(tb)) for t, tb in errores_reales]
    filas += [("SKIP", tid, "omitado (requiere entorno: " + nombre_archivo + ")")
              for tid, _ in errores_reclasificados]
    malos = {t.id() for t, _ in resultado.failures + errores_reales}
    omitidos = {t.id() for t, _ in resultado.skipped}
    omitidos |= {tid for tid, _ in errores_reclasificados}
    # Los NO_EJECUTADO que estén en omisiones.txt también son skips (su
    # setUpClass/setUpModule saltó por falta de entorno).
    no_ejecutados_reclasificados = []
    for tid in todos:
        if tid in malos:
            continue
        if tid in omitidos:
            filas.append(("SKIP", tid, ""))
        elif tid in resultado.iniciados:
            filas.append(("OK", tid, ""))
        else:
            nombre_archivo = os.path.basename(tid.split(".")[0] + ".py")
            if nombre_archivo in omisiones:
                no_ejecutados_reclasificados.append(tid)
                filas.append(("SKIP", tid, "omitado (requiere entorno: " + nombre_archivo + ")"))
            else:
                # setUpClass/setUpModule falló o saltó: el test no llegó a ejecutarse
                filas.append(("NO_EJECUTADO", tid, ""))
    omitidos |= set(no_ejecutados_reclasificados)

    filas.sort(key=lambda f: f[1])
    n_ok = sum(1 for f in filas if f[0] == "OK")
    n_fail = sum(1 for f in filas if f[0] == "FALLO")
    n_error = sum(1 for f in filas if f[0] == "ERROR")
    n_skip = sum(1 for f in filas if f[0] == "SKIP")
    n_no_exec = sum(1 for f in filas if f[0] == "NO_EJECUTADO")
    with open(salida, "w", encoding="utf-8") as f:
        for estado, tid, detalle in filas:
            f.write("{} {}{}\n".format(estado, tid, (" :: " + detalle[:300]) if detalle else ""))
        f.write("\nRESUMEN ejecutados={} fallos={} errores={} skip={} no_ejecutado={}\n".format(
            n_ok + n_fail + n_error + n_skip, n_fail, n_error, n_skip, n_no_exec))
    print("RESUMEN ejecutados={} fallos={} errores={} skip={} no_ejecutado={} -> {}".format(
        n_ok + n_fail + n_error + n_skip, n_fail, n_error, n_skip, n_no_exec, salida))


main()
