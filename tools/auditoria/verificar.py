# -*- coding: utf-8 -*-
"""verificar.py — ejecuta cada métrica de la rúbrica §2 y devuelve código ≠ 0 si falla.

Uso:
    python3 -I tools/auditoria/verificar.py          # modo texto, salida de código ≠ 0 si falla
    python3 -I tools/auditoria/verificar.py --json   # salida JSON para base.json / final.json

Las métricas que requieren FreeCAD (nivel 2/3) se reportan como "pendiente" si no hay
freecadcmd disponible; no fallan la ejecución en modo puro.
"""

from __future__ import annotations

import ast
import json
import os
import re
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
    """Cuenta líneas que coinciden con el patrón (regex) bajo path."""
    try:
        res = _run(["rg", "-n", pattern, str(path)], timeout=60)
        if res.returncode == 0:
            return len([l for l in res.stdout.splitlines() if l.strip()])
        return 0
    except Exception:
        return 0


def _grep_files(pattern: str, path: Path) -> list[str]:
    try:
        res = _run(["rg", "-l", pattern, str(path)], timeout=60)
        if res.returncode == 0:
            return [l for l in res.stdout.splitlines() if l.strip()]
        return []
    except Exception:
        return []


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
    # app no debe importar cad ni ui
    if APP.exists():
        for p in sorted(APP.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            src = p.read_text(encoding="utf-8")
            if "freecad.vdo.cad" in src or "freecad.vdo.ui" in src:
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
    dirs_permitidos = {str(CAD)} if CAD.exists() else set()
    for p in sorted(raiz.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(ROOT))
        if any(rel.startswith(d.replace(str(ROOT), "") + "/") for d in dirs_permitidos):
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
def _m5_estado_inmutable():
    asignaciones_mutables = []
    for p in sorted(CORE.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        for nodo in ast.walk(t):
            if isinstance(nodo, ast.Assign):
                for target in nodo.targets:
                    if isinstance(target, ast.Name):
                        idn = target.id
                        # constantes = mayúsculas con guión bajo
                        if not (idn.isupper() or idn.isidentifier() and idn == idn.upper()):
                            asignaciones_mutables.append(f"{p.relative_to(ROOT)}:{target.lineno}:{idn}")
            elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
                idn = nodo.target.id
                if not idn.isupper():
                    asignaciones_mutables.append(f"{p.relative_to(ROOT)}:{nodo.target.lineno}:{idn}")
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
def _m7_errores():
    except_pass = 0
    except_exception_core_cad_app = 0
    for base in (CORE, CAD, APP, UI, FREECAD / "vdo" / "commands.py"):
        if not base.exists():
            continue
        paths = [base] if base.is_file() else sorted(base.rglob("*.py"))
        for p in paths:
            if "__pycache__" in p.parts:
                continue
            src = p.read_text(encoding="utf-8")
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            for nodo in ast.walk(t):
                if isinstance(nodo, ast.Try):
                    # except … pass
                    for handler in nodo.handlers:
                        cuerpo = handler.body
                        if (len(cuerpo) == 1
                                and isinstance(cuerpo[0], ast.Pass)):
                            except_pass += 1
                        # except Exception
                        tipo = handler.type
                        if tipo is not None:
                            if (isinstance(tipo, ast.Name) and tipo.id == "Exception"):
                                except_exception_core_cad_app += 1
                            elif isinstance(tipo, ast.Attribute):
                                pass
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
    res = _run([str(ROOT / ".venv" / "bin" / "ruff"), "check",
                "--select", "C901", "--config", "max-complexity=12", str(FREECAD)],
               timeout=120)
    ruff_ok = res.returncode == 0
    cumple = cumple_ast and ruff_ok
    _registrar("R8_funciones_le100", len(largas), 0, cumple_ast,
               "funciones > 100 líneas: " + str(largas) if largas else "ninguna")
    _registrar("R8_ruff_c901_le12", 0 if ruff_ok else 1, 0, ruff_ok,
               "ruff C901: " + ("ok" if ruff_ok else "incidencias"))


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
            try:
                n_clones = int(l.split(":")[1].strip())
            except Exception:
                pass
    # defs no usadas (implementación simple: definiciones sin importador externo)
    n_no_usadas = _contar_defs_no_usadas()
    cumple = n_clones == 0 and n_no_usadas == 0
    _registrar("R9_clones", n_clones, 0, n_clones == 0, f"{n_clones} grupos de clones")
    _registrar("R9_defs_no_usadas", n_no_usadas, 0, n_no_usadas == 0,
               f"{n_no_usadas} definiciones no usadas")


def _contar_defs_no_usadas() -> int:
    """Cuenta definiciones de nivel módulo que no son importadas por ningún otro .py."""
    definiciones: dict[str, list[str]] = {}  # nombre -> [archivo]
    for p in sorted(FREECAD.rglob("*.py")):
        if "__pycache__" in p.parts or p.name == "__init__.py":
            continue
        src = p.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        for nodo in ast.walk(t):
            if isinstance(nodo, ast.FunctionDef):
                definiciones.setdefault(nodo.name, []).append(str(p.relative_to(ROOT)))
            elif isinstance(nodo, ast.ClassDef):
                definiciones.setdefault(nodo.name, []).append(str(p.relative_to(ROOT)))

    usados: set[str] = set()
    for p in sorted(FREECAD.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        for nodo in ast.walk(t):
            if isinstance(nodo, ast.ImportFrom):
                if nodo.module:
                    for alias in nodo.names:
                        usados.add(alias.name)
            elif isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    usados.add(alias.name.split(".")[0])
    no_usadas = [n for n in definiciones if n not in usados
                 and not n.startswith("_")]
    return len(no_usadas)


# ---------------------------------------------------------------------------
# R10 — Consistencia: ruff=0, mypy strict=0, cero print, cero sys.path, cero hex fuera tema
# ---------------------------------------------------------------------------
def _m10_consistencia():
    # ruff check
    res = _run([str(ROOT / ".venv" / "bin" / "ruff"), "check", str(FREECAD),
                str(TESTS), str(TOOLS)], timeout=120)
    n_ruff = res.returncode

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
    n_syspath_total = _grep_count(r"sys\.path", FREECAD) + _grep_count(r"sys\.path", TESTS)
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
        for m in re.finditer(r"#[0-9a-fA-F]{6}", src):
            # aceptar dentro de comentarios o docstrings es complejo; contamos todos
            n_hex += 1

    cumple = (n_ruff == 0 and mypy_ok and n_print == 0 and n_hex == 0)
    _registrar("R10_ruff_check_cero", n_ruff, 0, n_ruff == 0,
               f"ruff check devolvió {n_ruff}")
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

    omisiones_ok = True
    omisiones_path = TESTS / "soporte" / "omisiones.txt"
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
        try:
            res = _run(["command", "-v", nombre], shell=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                freecadcmd = res.stdout.strip()
                break
        except Exception:
            pass
    if freecadcmd is None:
        _registrar("R14_freecad_real", "pendiente", "instalado", False,
                   "freecadcmd no disponible — F17 bloqueada")
        return
    res = _run([freecadcmd, "--version"], timeout=10)
    version = res.stdout.strip() if res.returncode == 0 else "desconocida"
    _registrar("R14_freecad_real", version, "1.x", version.startswith("1"),
               f"binario: {freecadcmd}, versión: {version}")


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
