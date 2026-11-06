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


def _problema_salida(salida):
    """Motivo por el que no se puede escribir el resumen en ``salida``, o None.

    Se comprueba antes de ejecutar la suite. Si no se comprueba, la escritura falla
    al final con una excepción que sale del script sin liberar los widgets Qt (causa
    del SIGSEGV/abort al cerrar, medida con VDO_TEST_OUT apuntando a un directorio).
    """
    if os.path.isdir(salida):
        return "es un directorio; hace falta una ruta de fichero"
    if not os.path.isdir(os.path.dirname(salida) or "."):
        return "el directorio padre no existe"
    return None


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directorio = os.path.join(raiz, os.environ["VDO_TEST_DIR"])
    salida = os.path.join(raiz, os.environ["VDO_TEST_OUT"])
    problema = _problema_salida(salida)
    if problema:
        print(f"VDO_TEST_OUT inválido ({salida}): {problema}", file=sys.stderr)
        return 2
    sys.path.insert(0, raiz)
    sys.path.insert(0, directorio)
    # Sin guard __name__: freecadcmd ejecuta el script con otro __name__.
    # Los widgets Qt se liberan en finally: también si la suite lanza una excepción.
    from tests.soporte.qt import liberar_widgets
    try:
        return _ejecutar(directorio, salida)
    finally:
        liberar_widgets()


def _ejecutar(directorio, salida):

    # FreeCADCmd no define FreeCAD.__spec__; importlib.util.find_spec() falla sin él y
    # tumba varios módulos de prueba al importarse. Se define aquí, una vez, para todos.
    try:
        import FreeCAD as _fc
        if getattr(_fc, "__spec__", None) is None:
            import importlib.machinery
            _fc.__spec__ = importlib.machinery.ModuleSpec("FreeCAD", None)
    except ImportError:
        pass

    descubiertos = unittest.defaultTestLoader.discover(
        directorio, pattern="test_*.py", top_level_dir=directorio)
    # unittest vacía la suite al ejecutarla: los ids se recogen antes
    todos = [t.id() for t in _ids(descubiertos)]
    resultado = _Registro()
    descubiertos.run(resultado)

    # Cada entrada de failures/errors se escribe tal cual. Sin reclasificación a SKIP.
    def _ultima(tb):
        lineas = [renglon for renglon in tb.strip().splitlines() if renglon.strip()]
        return lineas[-1] if lineas else ""

    filas = [("FALLO", t.id(), _ultima(tb)) for t, tb in resultado.failures]
    filas += [("ERROR", t.id(), _ultima(tb)) for t, tb in resultado.errors]
    filas += [("SKIP", t.id(), motivo) for t, motivo in resultado.skipped]

    ejecutados_o_omitidos = {t.id() for t, _ in
                             resultado.failures + resultado.errors + resultado.skipped}
    # Si setUpClass omite la clase (entorno ausente), sus tests no llegan a iniciarse.
    # Se reportan como SKIP con el mismo motivo impreso por setUpClass, no como NO_EJECUTADO.
    omitidas_por_clase = {}
    for t, motivo in resultado.skipped:
        tid_sc = t.id()
        if tid_sc.startswith("setUpClass (") and tid_sc.endswith(")"):
            omitidas_por_clase[tid_sc[len("setUpClass ("):-1]] = motivo
    for tid in todos:
        if tid not in ejecutados_o_omitidos:
            if tid in resultado.iniciados:
                filas.append(("OK", tid, ""))
            elif tid.rsplit(".", 1)[0] in omitidas_por_clase:
                filas.append(("SKIP", tid, omitidas_por_clase[tid.rsplit(".", 1)[0]]))
            else:
                filas.append(("NO_EJECUTADO", tid, ""))

    filas.sort(key=lambda f: f[1])
    n_ok = sum(1 for f in filas if f[0] == "OK")
    n_fail = sum(1 for f in filas if f[0] == "FALLO")
    n_error = sum(1 for f in filas if f[0] == "ERROR")
    n_skip = sum(1 for f in filas if f[0] == "SKIP")
    n_no_exec = sum(1 for f in filas if f[0] == "NO_EJECUTADO")
    with open(salida, "w", encoding="utf-8") as f:
        for estado, tid, detalle in filas:
            f.write("{} {}{}\n".format(estado, tid, (" :: " + detalle[:300]) if detalle else ""))
        f.write(f"\nRESUMEN ejecutados={n_ok + n_fail + n_error + n_skip} "
                f"fallos={n_fail} errores={n_error} skip={n_skip} no_ejecutado={n_no_exec}\n")
    print(f"RESUMEN ejecutados={n_ok + n_fail + n_error + n_skip} "
          f"fallos={n_fail} errores={n_error} skip={n_skip} no_ejecutado={n_no_exec} -> {salida}")
    # Código de salida honesto: cualquier FALLO o ERROR devuelve 1 (F19-D1).
    # Antes el runner salía con 0 aunque hubiera fallos.
    return 1 if (n_fail or n_error or n_no_exec) else 0


# Sin guard __name__: freecadcmd ejecuta el script con otro __name__ y no entraría.
# No se usa atexit: bajo freecadcmd no se ejecuta.
_codigo_salida = main()
sys.stdout.flush()
sys.stderr.flush()
sys.exit(_codigo_salida)
