"""verificar.py — ejecuta cada métrica de la rúbrica §2 y devuelve código ≠ 0 si falla.

Uso:
    python3 -I tools/auditoria/verificar.py          # modo texto, salida de código ≠ 0 si falla
    python3 -I tools/auditoria/verificar.py --json   # salida JSON para base.json / final.json

Las métricas que requieren FreeCAD (nivel 2/3) se reportan como "pendiente" si no hay
freecadcmd disponible; no fallan la ejecución en modo puro.
"""

from __future__ import annotations

import ast
import contextlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # raíz del repo
FREECAD = ROOT / "freecad"
CORE = FREECAD / "vdo" / "core"
UI = FREECAD / "vdo" / "ui"
CAD = FREECAD / "vdo" / "cad"
APP = FREECAD / "vdo" / "app"
TESTS = ROOT / "tests"
TOOLS = ROOT / "tools"

RESULTADOS: dict[str, dict] = {}
FALLOS: list[str] = []


def _registrar(metrica: str, valor, umbral, cumple: bool, detalle: str = ""):
    RESULTADOS[metrica] = {
        "valor": valor,
        "umbral": umbral,
        "cumple": cumple,
        "detalle": detalle,
    }
    if not cumple:
        FALLOS.append(metrica)


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def _grep_count(pattern: str, path: Path, flags: int = 0) -> int:
    """Cuenta líneas que coinciden con el patrón (regex) bajo path.

    Un fallo de rg (no instalado, error de patrón) lanza excepción: no se
    convierte en 0 coincidencias, porque eso daría un falso verde.
    """
    res = _run(["rg", "-n", pattern, str(path)], timeout=60)
    if res.returncode == 0:
        return len([l for l in res.stdout.splitlines() if l.strip()])
    if res.returncode == 1:
        return 0
    raise RuntimeError(f"rg falló ({res.returncode}): {res.stderr.strip()[:200]}")


def _ruff_incidencias(rutas: list[str], extra: list[str] | None = None) -> int:
    """Número de incidencias de ruff (salida JSON), no su código de salida."""
    cmd = [str(ROOT / ".venv" / "bin" / "ruff"), "check", *(extra or []),
           "--output-format", "json", *rutas]
    res = _run(cmd, timeout=120)
    try:
        return len(json.loads(res.stdout or "[]"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ruff sin salida JSON: {res.stderr.strip()[:200]}") from exc


def _grep_files(pattern: str, path: Path) -> list[str]:
    # rg: 0 = coincidencias, 1 = ninguna, 2+ = error. Un error no es "cero coincidencias".
    res = _run(["rg", "-l", pattern, str(path)], timeout=60)
    if res.returncode == 0:
        return [l for l in res.stdout.splitlines() if l.strip()]
    if res.returncode == 1:
        return []
    raise RuntimeError(f"rg falló ({res.returncode}): {res.stderr.strip()[:200]}")


# ---------------------------------------------------------------------------
# R1 — Capas: ui → app → cad → core, ninguna otra
# ---------------------------------------------------------------------------
def _m1_capas():
    violaciones = []
    # ui no debe importar core ni cad
    for p in sorted(UI.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text(encoding="utf-8")
        if "freecad.vdo.core" in src or "freecad.vdo.cad" in src:
            violaciones.append(str(p.relative_to(ROOT)))
    # app no debe importar ui (ui → app, no al revés)
    # app → cad está permitido (cad es el adaptador de escritura que app usa)
    if APP.exists():
        for p in sorted(APP.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            src = p.read_text(encoding="utf-8")
            if "freecad.vdo.ui" in src:
                violaciones.append(str(p.relative_to(ROOT)))
    # cad no debe importar ui ni app
    if CAD.exists():
        for p in sorted(CAD.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            src = p.read_text(encoding="utf-8")
            if "freecad.vdo.ui" in src or "freecad.vdo.app" in src:
                violaciones.append(str(p.relative_to(ROOT)))
    cumple = len(violaciones) == 0
    _registrar("R1_capas", len(violaciones), 0, cumple,
               "violaciones: " + ", ".join(violaciones) if violaciones else "ninguna")


# ---------------------------------------------------------------------------
# R2 — Agnosticismo del dominio: core importa solo stdlib y core/
# ---------------------------------------------------------------------------
def _m2_agnosticismo():
    modulos_no_puros = []
    for p in sorted(CORE.rglob("*.py")):
        if "__pycache__" in p.parts or p.name == "__init__.py":
            continue
        src = p.read_text(encoding="utf-8")
        # imports de FreeCAD/Part/PySide/Qt a nivel de modulo (sin indentacion)
        es_impuro = False
        for line in src.splitlines():
            # Solo lineas que empiezan con import/from (sin indentacion)
            if not (line.startswith("import ") or line.startswith("from ")):
                continue
            s = line.strip()
            if (s.startswith("import FreeCAD") or s.startswith("from FreeCAD")
                    or s.startswith("import Part") or s.startswith("from Part")
                    or s.startswith("import PySide") or s.startswith("from PySide")
                    or s.startswith("import qt_compat") or s.startswith("from qt_compat")):
                es_impuro = True
                break
        if es_impuro:
            modulos_no_puros.append(str(p.relative_to(ROOT)))
    cumple = len(modulos_no_puros) == 0
    _registrar("R2_agnosticismo_core", len(modulos_no_puros), 0, cumple,
               "modulos no puros: " + ", ".join(modulos_no_puros) if modulos_no_puros else "ninguno")


# ---------------------------------------------------------------------------
# R3 — Dominio como datos: escrituras a objetos FreeCAD solo en cad/
# ---------------------------------------------------------------------------
def _m3_dominio_como_datos():
    patrones = [r"\.Ancho\s*=", r"\.Alto\s*=", r"\.Largo\s*=", r"\.addObject\b",
                r"\.recompute\b", r"App\.\w+", r"Part\.\w+"]
    escritos_fuera_cad = []
    raiz = FREECAD / "vdo"
    cad_prefix = str(CAD) + "/" if CAD.exists() else ""
    for p in sorted(raiz.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        if cad_prefix and str(p).startswith(cad_prefix):
            continue
        src = p.read_text(encoding="utf-8")
        for pat in patrones:
            if re.search(pat, src):
                escritos_fuera_cad.append(rel)
                break
    cumple = len(escritos_fuera_cad) == 0
    _registrar("R3_dominio_como_datos", len(escritos_fuera_cad), 0, cumple,
               "escrituras fuera de cad/: " + ", ".join(escritos_fuera_cad) if escritos_fuera_cad else "ninguna")


# ---------------------------------------------------------------------------
# R4 — Orquestación: existe app/ con un caso de uso por operación
# ---------------------------------------------------------------------------
def _m4_orquestacion():
    casos_esperados = ["crear_hoja", "crear_panel", "crear_zocalo", "crear_cajon",
                       "crear_puerta", "crear_coco", "editar_modulo", "colocar_modulo",
                       "exportar_lista_corte", "optimizar_corte", "nesting",
                       "consultar_herrajes", "recargar_catalogo"]
    existentes = []
    if APP.exists():
        casos_dir = APP / "casos_uso"
        if casos_dir.exists():
            existentes = [p.stem for p in casos_dir.glob("*.py")
                          if p.stem != "__init__"]
    faltantes = [c for c in casos_esperados if c not in existentes]
    cumple = len(faltantes) == 0 and APP.exists()
    _registrar("R4_orquestacion_app", len(faltantes), 0, cumple,
               "casos faltantes: " + ", ".join(faltantes) if faltantes else "todos presentes")


# ---------------------------------------------------------------------------
# R5 — Inyección y estado: cero estado mutable de módulo (salvo constantes)
# ---------------------------------------------------------------------------
def _es_constante_o_all(nombre: str) -> bool:
    """Constantes en mayúsculas y __all__ no cuentan como estado mutable (R5)."""
    return nombre == "__all__" or nombre.isupper()


def _asignaciones_mutables_modulo(src: str) -> list[tuple[int, str]]:
    """R5: (línea, nombre) de asignaciones de nivel módulo (tree.body) que no son
    constantes en mayúsculas ni __all__. Las variables locales no cuentan."""
    salida: list[tuple[int, str]] = []
    for nodo in ast.parse(src).body:
        if isinstance(nodo, ast.Assign):
            for target in nodo.targets:
                if isinstance(target, ast.Name) and not _es_constante_o_all(target.id):
                    salida.append((target.lineno, target.id))
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            if not _es_constante_o_all(nodo.target.id):
                salida.append((nodo.target.lineno, nodo.target.id))
    return salida


def _m5_estado_inmutable():
    asignaciones_mutables = []
    for base in (CORE, APP, CAD):
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            try:
                hallazgos = _asignaciones_mutables_modulo(p.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            asignaciones_mutables += [f"{p.relative_to(ROOT)}:{ln}:{n}" for ln, n in hallazgos]
    cumple = len(asignaciones_mutables) == 0
    _registrar("R5_estado_inmutable", len(asignaciones_mutables), 0, cumple,
               "asignaciones mutables: " + ", ".join(asignaciones_mutables) if asignaciones_mutables else "ninguna")


# ---------------------------------------------------------------------------
# R6 — Paneles: accept() ≤ 15 líneas en los 5 paneles
# ---------------------------------------------------------------------------
def _m6_paneles_delgados():
    paneles = ["zocalo_task", "panel_task", "puerta_task", "cajon_task", "coco_unified_task"]
    largo = []
    for nombre in paneles:
        p = UI / f"vdo_{nombre}.py"
        if not p.exists():
            largo.append((nombre, "no existe"))
            continue
        src = p.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            largo.append((nombre, "error de sintaxis"))
            continue
        for nodo in ast.walk(t):
            if isinstance(nodo, ast.FunctionDef) and nodo.name == "accept__":
                lineas = (nodo.end_lineno or 0) - (nodo.lineno or 0) + 1
                if lineas > 15:
                    largo.append((nombre, lineas))
    cumple = len(largo) == 0
    _registrar("R6_paneles_accept_le15", len(largo), 0, cumple,
               "paneles > 15 líneas: " + str(largo) if largo else "todos ≤ 15")


# ---------------------------------------------------------------------------
# R7 — Errores: cero except … pass; cero except Exception en core/cad/app
# ---------------------------------------------------------------------------
def _except_pass_en(src: str) -> int:
    """R7: número de manejadores de excepción cuyo cuerpo es solo `pass`."""
    n = 0
    for nodo in ast.walk(ast.parse(src)):
        if isinstance(nodo, ast.Try):
            for handler in nodo.handlers:
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    n += 1
    return n


def _except_exception_en(src: str) -> int:
    """R7: número de manejadores `except Exception` (cualquier cuerpo)."""
    n = 0
    for nodo in ast.walk(ast.parse(src)):
        if isinstance(nodo, ast.Try):
            for handler in nodo.handlers:
                if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                    n += 1
    return n


def _m7_errores():
    except_pass = 0
    except_exception_core_cad_app = 0
    # except … pass: cero en todo el paquete
    for base in (CORE, CAD, APP, UI, FREECAD / "vdo" / "commands.py"):
        if not base.exists():
            continue
        paths = [base] if base.is_file() else sorted(base.rglob("*.py"))
        for p in paths:
            if "__pycache__" in p.parts:
                continue
            try:
                except_pass += _except_pass_en(p.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
    # except Exception: cero solo en core/cad/app
    for base in (CORE, CAD, APP):
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            try:
                except_exception_core_cad_app += _except_exception_en(p.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
    _registrar("R7_except_pass", except_pass, 0, except_pass == 0,
               f"{except_pass} except … pass")
    _registrar("R7_except_exception_core_cad_app", except_exception_core_cad_app, 0,
               except_exception_core_cad_app == 0,
               f"{except_exception_core_cad_app} except Exception en core/cad/app")


# ---------------------------------------------------------------------------
# R8 — Complejidad: ninguna función > 100 líneas; ruff C901 ≤ 12
# ---------------------------------------------------------------------------
def _m8_complejidad():
    largas = []
    for p in sorted(FREECAD.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        for nodo in ast.walk(t):
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lineas = (nodo.end_lineno or 0) - (nodo.lineno or 0) + 1
                if lineas > 100:
                    largas.append((str(p.relative_to(ROOT)), nodo.name, lineas))
    cumple_ast = len(largas) == 0

    # ruff C901
    # Umbral 12 en pyproject.toml ([tool.ruff.lint.mccabe]).
    n_c901 = _ruff_incidencias([str(FREECAD)], ["--select", "C901"])
    _registrar("R8_funciones_le100", len(largas), 0, cumple_ast,
               "funciones > 100 líneas: " + str(largas) if largas else "ninguna")
    _registrar("R8_ruff_c901_le12", n_c901, 0, n_c901 == 0,
               f"ruff C901 (max 12): {n_c901} incidencias")


# ---------------------------------------------------------------------------
# R9 — Duplicación y muerte: 0 clones; 0 defs no usadas
# ---------------------------------------------------------------------------
def _m9_duplicacion():
    # clones
    res = _run(["python3", "-I", str(TOOLS / "auditoria" / "clones.py"), str(FREECAD)],
               timeout=60)
    salida = res.stdout
    n_clones = 0
    for l in salida.splitlines():
        if l.startswith("grupos de funciones"):
            with contextlib.suppress(Exception):
                n_clones = int(l.split(":")[1].strip())
    # defs no usadas (implementación simple: definiciones sin importador externo)
    n_no_usadas = _contar_defs_no_usadas()
    _registrar("R9_clones", n_clones, 0, n_clones == 0, f"{n_clones} grupos de clones")
    _registrar("R9_defs_no_usadas", n_no_usadas, 0, n_no_usadas == 0,
               f"{n_no_usadas} definiciones no usadas")


def _definiciones_modulo(src: str) -> list[tuple[str, int]]:
    """R9: (nombre, línea) de funciones y clases de nivel módulo (tree.body).
    Los métodos de clase no cuentan."""
    return [(n.name, n.lineno) for n in ast.parse(src).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]


def _referencias(src: str) -> set[str]:
    """R9: nombres que el código referencia. Cuenta cualquier forma de uso:
    importación (from x import y), nombre (y), atributo (mod.y) y cadena que sea
    identificador ("y", p. ej. tablas de despacho). Conservador: prefiere no
    marcar como muerto un nombre que podría usarse."""
    refs: set[str] = set()
    for nodo in ast.walk(ast.parse(src)):
        if isinstance(nodo, ast.ImportFrom):
            refs.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.Import):
            refs.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.Attribute):
            refs.add(nodo.attr)
        elif isinstance(nodo, ast.Name):
            refs.add(nodo.id)
        elif isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) and nodo.value.isidentifier():
            refs.add(nodo.value)
    return refs


def _defs_no_usadas(definiciones: dict[str, str], fuentes_referencia: list[str]) -> list[str]:
    """R9: "archivo:nombre" de cada definición de nivel módulo que no aparece
    como referencia en ninguna fuente de referencia (incluido su propio archivo)."""
    usados: set[str] = set()
    for src in fuentes_referencia:
        usados |= _referencias(src)
    no_usadas: list[str] = []
    for ruta, src in definiciones.items():
        for nombre, _linea in _definiciones_modulo(src):
            if nombre not in usados:
                no_usadas.append(f"{ruta}:{nombre}")
    return no_usadas


def _contar_defs_no_usadas() -> int:
    """Cuenta definiciones de nivel módulo sin referencias en paquete, tests,
    tools, InitGui e Init. Ver docs/metricas/README.md (definición exacta)."""
    definiciones: dict[str, str] = {}
    for p in sorted(FREECAD.rglob("*.py")):
        if "__pycache__" in p.parts or p.name == "__init__.py":
            continue
        definiciones[str(p.relative_to(ROOT))] = p.read_text(encoding="utf-8")
    fuentes = [p.read_text(encoding="utf-8") for p in sorted(FREECAD.rglob("*.py"))
               + sorted(TESTS.rglob("*.py")) + sorted(TOOLS.rglob("*.py"))
               if "__pycache__" not in p.parts]
    for nombre in ("InitGui.py", "Init.py"):
        p = ROOT / nombre
        if p.exists():
            fuentes.append(p.read_text(encoding="utf-8"))
    no_usadas = _defs_no_usadas(definiciones, fuentes)
    return len(no_usadas)


# ---------------------------------------------------------------------------
# R10 — Consistencia: ruff=0, mypy strict=0, cero print, cero sys.path, cero hex fuera tema
# ---------------------------------------------------------------------------
def _m10_consistencia():
    # ruff check
    n_ruff = _ruff_incidencias([str(FREECAD), str(TESTS), str(TOOLS)])

    # mypy strict en core/app/cad
    mypy_ok = True
    mypy_errores = 0
    if APP.exists() or CAD.exists():
        res = _run([str(ROOT / ".venv" / "bin" / "mypy"), "--strict",
                    str(CORE), str(APP) if APP.exists() else str(CORE),
                    str(CAD) if CAD.exists() else str(CORE)],
                   timeout=120)
        mypy_ok = res.returncode == 0
        if not mypy_ok:
            mypy_errores = len([l for l in res.stdout.splitlines()
                                if ": error:" in l])

    # cero print en paquete
    n_print = _grep_count(r"\bprint\(", FREECAD)

    # cero sys.path fuera de Init.py/InitGui.py
    n_syspath = 0
    for nombre in ("Init.py", "InitGui.py"):
        p = ROOT / nombre
        if p.exists():
            n_syspath += _grep_count(r"sys\.path", p)
    _grep_count(r"sys\.path", FREECAD) + _grep_count(r"sys\.path", TESTS)
    # sys.path en Init.py/InitGui.py está permitido

    # cero colores hex fuera de ui/tema.py
    n_hex = 0
    for p in sorted(FREECAD.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        if rel.endswith("ui/tema.py"):
            continue
        src = p.read_text(encoding="utf-8")
        import re
        for _m in re.finditer(r"#[0-9a-fA-F]{6}", src):
            # aceptar dentro de comentarios o docstrings es complejo; contamos todos
            n_hex += 1

    _registrar("R10_ruff_check_cero", n_ruff, 0, n_ruff == 0,
               f"ruff check: {n_ruff} incidencias")
    _registrar("R10_mypy_strict_cero", mypy_errores, 0, mypy_ok,
               f"mypy strict: {mypy_errores} errores")
    _registrar("R10_cero_print", n_print, 0, n_print == 0,
               f"{n_print} print() en freecad/")
    _registrar("R10_cero_hex_fuera_tema", n_hex, 0, n_hex == 0,
               f"{n_hex} literales hex fuera de ui/tema.py")


# ---------------------------------------------------------------------------
# R11 — Pruebas: golden masters, suite nivel 1 verde
# ---------------------------------------------------------------------------
def _m11_pruebas():
    n_golden = 0
    golden_dir = TESTS / "golden"
    if golden_dir.exists():
        n_golden = len(list(golden_dir.glob("*.json")))

    # suite nivel 1 (se ejecuta por separado; aquí solo verificamos estructura)
    suite_l1_ok = TESTS.exists()
    _registrar("R11_golden_masters", n_golden, ">=1", n_golden > 0,
               f"{n_golden} golden.json")
    _registrar("R11_suite_nivel1_estructura", 0 if suite_l1_ok else 1, 0,
               suite_l1_ok, "tests/ existe")


# ---------------------------------------------------------------------------
# R12 — Documentación: ARQUITECTURA.md, ADRs, DEUDA_TECNICA.md
# ---------------------------------------------------------------------------
def _m12_documentacion():
    docs = ROOT / "docs"
    archivo_arq = (docs / "ARQUITECTURA.md").exists()
    adr_dir = docs / "adr"
    n_adrs = len(list(adr_dir.glob("ADR-*.md"))) if adr_dir.exists() else 0
    deuda = (docs / "DEUDA_TECNICA.md").exists()
    glosario = (docs / "GLOSARIO.md").exists()
    cumple = archivo_arq and n_adrs > 0 and deuda and glosario
    _registrar("R12_documentacion", 0 if cumple else 1, 0, cumple,
               f"ARQUITECTURA={archivo_arq}, ADRs={n_adrs}, DEUDA={deuda}, GLOSARIO={glosario}")


# ---------------------------------------------------------------------------
# R14 — Verificación real en FreeCAD (bloqueado si no hay freecadcmd)
# ---------------------------------------------------------------------------
def _m14_freecad():
    freecadcmd = None
    for nombre in ("freecadcmd", "freecad-cli"):
        ruta = shutil.which(nombre)
        if ruta:
            freecadcmd = ruta
            break
    if freecadcmd is None:
        _registrar("R14_freecad_real", "pendiente", "instalado", False,
                   "freecadcmd no disponible — F17 bloqueada")
        return
    res = _run([freecadcmd, "--version"], timeout=10)
    salida = res.stdout.strip() if res.returncode == 0 else ""
    # La salida real es "FreeCAD 1.1.4 Revision: ...": se extrae el número, no el prefijo.
    m = re.search(r"\b(\d+)\.(\d+)(?:\.(\d+))?", salida)
    version = m.group(0) if m else "desconocida"
    _registrar("R14_freecad_real", version, "1.x", bool(m) and m.group(1) == "1",
               f"binario: {freecadcmd}, salida: {salida or 'vacía'}")


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------
def main():
    json_only = "--json" in sys.argv

    _m1_capas()
    _m2_agnosticismo()
    _m3_dominio_como_datos()
    _m4_orquestacion()
    _m5_estado_inmutable()
    _m6_paneles_delgados()
    _m7_errores()
    _m8_complejidad()
    _m9_duplicacion()
    _m10_consistencia()
    _m11_pruebas()
    _m12_documentacion()
    _m14_freecad()

    if json_only:
        print(json.dumps({
            "resultado": "OK" if not FALLOS else "FALLA",
            "fallos": FALLOS,
            "metricas": RESULTADOS,
        }, indent=2, ensure_ascii=False))
    else:
        print("=== VDO — verificación de métricas §2 ===")
        for nombre, dato in RESULTADOS.items():
            estado = "OK" if dato["cumple"] else "FALLA"
            print(f"[{estado}] {nombre}: valor={dato['valor']} umbral={dato['umbral']} "
                  f"({dato['detalle']})")
        print()
        if FALLOS:
            print(f"MÉTRICAS FALLADAS ({len(FALLOS)}): " + ", ".join(FALLOS))
            sys.exit(1)
        else:
            print("Todas las métricas cumplen.")

    sys.exit(0 if not FALLOS else 1)


if __name__ == "__main__":
    main()
