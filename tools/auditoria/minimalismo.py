"""tools/auditoria/minimalismo.py — medición de métricas de minimalismo VDO (§5 del plan).

Subcomandos:
  resumen     líneas por capa, módulos, funciones, tamaño de API pública
  duplicados  tablas constantes idénticas (AST) y funciones con cuerpo idéntico
  literales   valores de dominio repetidos (vigilados en datos/vigilados.json)
  ramas       funciones con cadenas if/elif de 4+ ramas
  fachadas    módulos que solo reexportan o renombran
  tamano      archivos > 400 líneas y funciones > 60 líneas
  excepciones except sin re-lanzamiento ni registro

Salida: JSON y tabla. Código de salida 0 si el alcance cumple su meta.
"""

from __future__ import annotations

import ast
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FREECAD = ROOT / "freecad"
CORE = FREECAD / "vdo" / "core"
UI = FREECAD / "vdo" / "ui"
CAD = FREECAD / "vdo" / "cad"
APP = FREECAD / "vdo" / "app"
TESTS = ROOT / "tests"
TOOLS = ROOT / "tools"
DATOS = FREECAD / "vdo" / "datos"
VIGILADOS = DATOS / "vigilados.json"

CAPAS = [("core", CORE), ("ui", UI), ("cad", CAD), ("app", APP)]


# ---------------------------------------------------------------------------
# Lectura de archivos
# ---------------------------------------------------------------------------
def _archivos_py(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return [p for p in sorted(base.rglob("*.py")) if "__pycache__" not in p.parts]


def _leer(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Subcomando: resumen
# ---------------------------------------------------------------------------
def _resumen() -> dict:
    resultado: dict = {"capas": {}, "total_archivos": 0, "total_funciones": 0,
                        "total_lineas": 0, "api_publica": {}}
    for nombre, base in CAPAS:
        archivos = _archivos_py(base)
        lineas = 0
        funciones = 0
        publicos = []
        for p in archivos:
            src = _leer(p)
            lineas += src.count("\n") + 1
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            for n in ast.walk(t):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funciones += 1
                    if not n.name.startswith("_"):
                        publicos.append(f"{p.relative_to(ROOT)}.{n.name}")
                elif isinstance(n, ast.ClassDef):
                    for m in n.body:
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("_"):
                            publicos.append(f"{p.relative_to(ROOT)}.{n.name}.{m.name}")
        resultado["capas"][nombre] = {
            "archivos": len(archivos),
            "lineas": lineas,
            "funciones": funciones,
            "api_publica": len(publicos),
        }
        resultado["total_archivos"] += len(archivos)
        resultado["total_lineas"] += lineas
        resultado["total_funciones"] += funciones
        resultado["api_publica"][nombre] = publicos
    return resultado


# ---------------------------------------------------------------------------
# Subcomando: duplicados
# ---------------------------------------------------------------------------
def _ast_dump_canonico(nodo) -> str:
    """Dump determinista de un nodo AST (ignora líneas/columnas)."""
    return ast.dump(nodo, annotate_fields=False, include_attributes=False)


def _duplicados() -> dict:
    # 1. Tablas constantes idénticas por AST
    tablas: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    # 2. Funciones con cuerpo idéntico
    cuerpos: dict[str, list[tuple[str, str, int]]] = collections.defaultdict(list)

    for nombre, base in CAPAS:
        for p in _archivos_py(base):
            src = _leer(p)
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            rel = str(p.relative_to(ROOT))
            # Tablas: asignaciones de nivel módulo cuyo valor es un literal contenedor
            for nodo in t.body:
                if isinstance(nodo, ast.Assign):
                    for target in nodo.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            dump = _ast_dump_canonico(nodo.value)
                            tablas[dump].append((target.id, rel))
                elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
                    if nodo.target.id.isupper() and nodo.value is not None:
                        dump = _ast_dump_canonico(nodo.value)
                        tablas[dump].append((nodo.target.id, rel))
            # Funciones con cuerpo idéntico (>= 2 statements, sin docstring al inicio)
            for nodo in ast.walk(t):
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = nodo.body
                    if (isinstance(body[0], ast.Expr)
                            and isinstance(getattr(body[0], "value", None), ast.Constant)
                            and isinstance(body[0].value.value, str)):
                        body = body[1:]
                    if len(body) >= 2:
                        dump = "\n".join(_ast_dump_canonico(s) for s in body)
                        cuerpos[dump].append((nodo.name, rel, nodo.lineno))

    tablas_dup = {k: v for k, v in tablas.items() if len(v) > 1}
    cuerpos_dup = {k: v for k, v in cuerpos.items() if len(v) > 1}

    return {
        "tablas_identicas": len(tablas_dup),
        "detalle_tablas": {k: v for k, v in tablas_dup.items()},
        "cuerpos_identicos": len(cuerpos_dup),
        "detalle_cuerpos": {k: v for k, v in cuerpos_dup.items()},
    }


# ---------------------------------------------------------------------------
# Subcomando: literales
# ---------------------------------------------------------------------------
def _literal_vigilados() -> list[str]:
    if not VIGILADOS.exists():
        return []
    datos = json.loads(VIGILADOS.read_text(encoding="utf-8"))
    return datos.get("valores", [])


def _literales() -> dict:
    vigilados = _literal_vigilados()
    hallazgos: dict[str, list[str]] = {}
    # Cuenta usos como literal de cadena (AST): ignora comentarios, docstrings de
    # texto libre, identificadores como `tirador_x` y subcadenas.
    conjunto = set(vigilados)
    for nombre, base in CAPAS:
        for p in _archivos_py(base):
            try:
                t = ast.parse(_leer(p))
            except SyntaxError:
                continue
            rel = str(p.relative_to(ROOT))
            for nodo in ast.walk(t):
                if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str) and nodo.value in conjunto:
                    hallazgos.setdefault(nodo.value, []).append(f"{rel}:{nodo.lineno}")
    return {"vigilados": vigilados, "hallazgos": hallazgos, "total": sum(len(v) for v in hallazgos.values())}


# ---------------------------------------------------------------------------
# Subcomando: ramas
# ---------------------------------------------------------------------------
def _ramas() -> dict:
    """Funciones con cadenas if/elif de 4 o más ramas sobre el mismo test."""
    resultado: dict = {}
    for nombre, base in CAPAS:
        for p in _archivos_py(base):
            src = _leer(p)
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            rel = str(p.relative_to(ROOT))
            for nodo in ast.walk(t):
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    n_if = _contar_cadena_ifelif(nodo)
                    if n_if >= 4:
                        resultado.setdefault(rel, []).append({
                            "funcion": nodo.name,
                            "ramas": n_if,
                            "linea": nodo.lineno,
                        })
    total = sum(len(v) for v in resultado.values())
    return {"funciones_con_ramas": total, "detalle": resultado}


def _contar_cadena_ifelif(nodo_func) -> int:
    """Longitud de la mayor cadena if/elif de la función.

    Una cadena es un `if` cuyo `else` es un único `if` (y así sucesivamente).
    Los `if` independientes NO se suman: no son ramas de una misma decisión.
    """
    mayor = 0
    for nodo in ast.walk(nodo_func):
        if not isinstance(nodo, ast.If):
            continue
        # Solo se empieza a contar desde el primer `if` de una cadena (no desde un elif).
        if any(isinstance(p, ast.If) and p.orelse == [nodo] for p in ast.walk(nodo_func)):
            continue
        n = 1
        actual = nodo
        while len(actual.orelse) == 1 and isinstance(actual.orelse[0], ast.If):
            n += 1
            actual = actual.orelse[0]
        mayor = max(mayor, n)
    return mayor


# ---------------------------------------------------------------------------
# Subcomando: fachadas
# ---------------------------------------------------------------------------
def _fachadas() -> dict:
    """Módulos cuyo cuerpo son solo imports y reexportaciones."""
    fachadas = []
    for nombre, base in CAPAS:
        for p in _archivos_py(base):
            if p.name == "__init__.py":
                continue
            src = _leer(p)
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            solo_imports = True
            tiene_export = False
            for nodo in t.body:
                if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                    continue
                if isinstance(nodo, ast.Assign):
                    for target in nodo.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            tiene_export = True
                            continue
                    solo_imports = False
                    break
                if isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
                    if nodo.target.id == "__all__":
                        tiene_export = True
                        continue
                    solo_imports = False
                    break
                # Cualquier otra cosa (función, clase, cálculo) rompe la fachada
                solo_imports = False
                break
            if solo_imports and len(t.body) > 0:
                fachadas.append(str(p.relative_to(ROOT)))
    return {"fachadas": len(fachadas), "detalle": fachadas}


# ---------------------------------------------------------------------------
# Subcomando: tamano
# ---------------------------------------------------------------------------
def _tamano() -> dict:
    archivos_grandes = []
    funciones_largas = []
    for nombre, base in CAPAS:
        for p in _archivos_py(base):
            src = _leer(p)
            n_lineas = src.count("\n") + 1
            if n_lineas > 400:
                archivos_grandes.append({"archivo": str(p.relative_to(ROOT)), "lineas": n_lineas})
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            for nodo in ast.walk(t):
                if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ln = (nodo.end_lineno or 0) - (nodo.lineno or 0) + 1
                    if ln > 60:
                        funciones_largas.append({
                            "archivo": str(p.relative_to(ROOT)),
                            "funcion": nodo.name,
                            "lineas": ln,
                            "linea_inicio": nodo.lineno,
                        })
    return {"archivos_grandes": archivos_grandes, "funciones_largas": funciones_largas}


# ---------------------------------------------------------------------------
# Subcomando: excepciones
# ---------------------------------------------------------------------------
def _excepciones() -> dict:
    """except sin re-lanzamiento (raise) ni registro (App.Console / logging)."""
    problemas = []
    for nombre, base in CAPAS:
        for p in _archivos_py(base):
            src = _leer(p)
            try:
                t = ast.parse(src)
            except SyntaxError:
                continue
            rel = str(p.relative_to(ROOT))
            for nodo in ast.walk(t):
                if isinstance(nodo, ast.Try):
                    for handler in nodo.handlers:
                        cuerpo = handler.body
                        tiene_raise = any(
                            isinstance(s, ast.Raise) for s in ast.walk(handler) if isinstance(s, ast.Raise)
                        )
                        tiene_log = False
                        for s in ast.walk(handler):
                            if isinstance(s, ast.Call):
                                func = s.func
                                if isinstance(func, ast.Attribute):
                                    if func.attr in ("PrintError", "PrintWarning", "PrintMessage",
                                                     "error", "warning", "info", "debug", "exception"):
                                        tiene_log = True
                                elif isinstance(func, ast.Name):
                                    if func.id in ("logging", "print"):
                                        tiene_log = True
                        if not tiene_raise and not tiene_log:
                            problemas.append({
                                "archivo": rel,
                                "funcion": getattr(nodo, "name", "<modulo>"),
                                "linea": handler.lineno,
                            })
    return {"excepciones_tragadas": len(problemas), "detalle": problemas}


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------
def _imprimir_tabla(titulo: str, filas: list[list[str]], cabecera: list[str]) -> None:
    print(f"\n=== {titulo} ===")
    if cabecera:
        print(" | ".join(cabecera))
        print("-" * (sum(len(c) for c in cabecera) + 3 * (len(cabecera) - 1)))
    for fila in filas:
        print(" | ".join(fila))


def main() -> int:
    sub = sys.argv[1] if len(sys.argv) > 1 else "resumen"
    salida_json = {"subcomando": sub, "resultado": {}}

    if sub == "resumen":
        data = _resumen()
        salida_json["resultado"] = data
        filas = []
        for capa, d in data["capas"].items():
            filas.append([capa, str(d["archivos"]), str(d["lineas"]), str(d["funciones"]), str(d["api_publica"])])
        filas.append(["TOTAL", str(data["total_archivos"]), str(data["total_lineas"]),
                      str(data["total_funciones"]), "-"])
        _imprimir_tabla("RESUMEN por capa", filas,
                        ["capa", "archivos", "lineas", "funciones", "api_publica"])

    elif sub == "duplicados":
        data = _duplicados()
        salida_json["resultado"] = data
        filas = [[str(data["tablas_identicas"]), "tablas constantes idénticas (AST)"]]
        filas.append([str(data["cuerpos_identicos"]), "funciones con cuerpo idéntico"])
        _imprimir_tabla("DUPLICADOS", filas, ["cantidad", "tipo"])
        for k, v in data["detalle_tablas"].items():
            print(f"  Tabla duplicada: {v}")
        for k, v in data["detalle_cuerpos"].items():
            print(f"  Función duplicada: {v}")

    elif sub == "literales":
        data = _literales()
        salida_json["resultado"] = data
        filas = [[str(data["total"]), "literales vigilados fuera de datos/"]]
        for valor, archivos in sorted(data["hallazgos"].items()):
            filas.append([valor, str(len(archivos)), ", ".join(archivos[:3])])
        _imprimir_tabla("LITERALES vigilados", filas, ["valor", "archivos", "detalle"])

    elif sub == "ramas":
        data = _ramas()
        salida_json["resultado"] = data
        filas = [[str(data["funciones_con_ramas"]), "funciones con 4+ ramas if/elif"]]
        for archivo, funcs in data["detalle"].items():
            for f in funcs:
                filas.append([archivo, f["funcion"], str(f["ramas"]), f"L{f['linea']}"])
        _imprimir_tabla("RAMAS if/elif >= 4", filas, ["archivo", "funcion", "ramas", "linea"])

    elif sub == "fachadas":
        data = _fachadas()
        salida_json["resultado"] = data
        filas = [[str(data["fachadas"]), "módulos fachada (solo imports/reexport)"]]
        for f in data["detalle"]:
            filas.append([f, ""])
        _imprimir_tabla("FACHADAS", filas, ["cantidad", "modulo"])

    elif sub == "tamano":
        data = _tamano()
        salida_json["resultado"] = data
        filas = [[str(len(data["archivos_grandes"])), "archivos > 400 líneas"]]
        for a in data["archivos_grandes"]:
            filas.append([a["archivo"], str(a["lineas"])])
        filas.append([str(len(data["funciones_largas"])), "funciones > 60 líneas"])
        for f in data["funciones_largas"]:
            filas.append([f"{f['archivo']}:{f['funcion']}", str(f["lineas"])])
        _imprimir_tabla("TAMAÑO", filas, ["cantidad/detalle", "valor"])

    elif sub == "excepciones":
        data = _excepciones()
        salida_json["resultado"] = data
        filas = [[str(data["excepciones_tragadas"]), "except que tragan errores"]]
        for e in data["detalle"]:
            filas.append([f"{e['archivo']}:{e['linea']}", e["funcion"]])
        _imprimir_tabla("EXCEPCIONES tragadas", filas, ["ubicacion", "funcion"])

    else:
        print(f"Subcomando desconocido: {sub}")
        print("Opciones: resumen, duplicados, literales, ramas, fachadas, tamano, excepciones")
        return 1

    print(json.dumps(salida_json, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
