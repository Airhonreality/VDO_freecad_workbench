# -*- coding: utf-8 -*-
"""Genera docs/MATRIZ_MAPEO.md leyendo los imports reales de los módulos legacy.

Para cada .py de Macro/ (excepto tests/ y tools/) registra:
- imports de nivel de módulo (se ejecutan al importar el archivo),
- imports diferidos (dentro de funciones/clases),
- si toca FreeCADGui, PySide* o Qt a nivel de módulo (bloquea la prueba headless),
- dependencias internas (otros módulos de Macro/),
- capa propuesta y destino en la estructura objetivo.

Uso: python3 tools/matriz_mapeo.py

Nota: lee Macro/, retirado en la Fase 3. Solo sirve sobre un checkout anterior a la migración.
"""

import ast
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEGACY = os.path.join(RAIZ, "Macro")
SALIDA = os.path.join(RAIZ, "docs", "MATRIZ_MAPEO.md")

GUI_PREFIJOS = ("FreeCADGui", "PySide", "PySide2", "PySide6", "Gui")
IGNORAR = {"Init", "InitGui"}

# Capa propuesta por nombre. Los nombres coinciden con los de Macro/ (Fase 2: sin renombrar).
# UI = contiene widgets/TaskPanels. CORE = motor sin GUI. APP = punto de entrada y comandos.
CAPA_UI_SUFIJOS = ("_task", "_view", "_preview", "_ui", "_widget", "_dock", "_preview2d", "_inspector_dock")


def _nombre_modulo(ruta):
    return os.path.splitext(os.path.basename(ruta))[0]


def _raiz_import(nombre):
    return nombre.split(".")[0] if nombre else ""


def analizar(ruta):
    with open(ruta, encoding="utf-8") as f:
        arbol = ast.parse(f.read(), filename=ruta)

    nivel_modulo, diferidos = set(), set()
    gui_nivel_modulo = False
    gui_refs = set()

    def _registrar(nodo, dentro_de_funcion):
        nombres = []
        if isinstance(nodo, ast.Import):
            nombres = [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres = [nodo.module]
        for n in nombres:
            r = _raiz_import(n)
            if r in ("FreeCADGui",) or r.startswith(GUI_PREFIJOS):
                gui_refs.add(n)
                if not dentro_de_funcion:
                    nonlocal_flag[0] = True
            (diferidos if dentro_de_funcion else nivel_modulo).add(n)

    nonlocal_flag = [False]

    def _recorrer(nodos, dentro_de_funcion):
        for nodo in nodos:
            if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                _registrar(nodo, dentro_de_funcion)
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _recorrer(nodo.body, True)
            elif isinstance(nodo, ast.ClassDef):
                _recorrer(nodo.body, dentro_de_funcion)
            else:
                # if/try/with/for: los imports anidados siguen siendo de nivel de módulo
                _recorrer([h for h in ast.iter_child_nodes(nodo) if isinstance(h, ast.stmt)], dentro_de_funcion)

    _recorrer(arbol.body, False)
    gui_nivel_modulo = nonlocal_flag[0]
    return {
        "nivel_modulo": sorted(nivel_modulo),
        "diferidos": sorted(diferidos),
        "gui_nivel_modulo": gui_nivel_modulo,
        "gui_refs": sorted(gui_refs),
    }


def main():
    modulos = {}
    for nombre_archivo in sorted(os.listdir(LEGACY)):
        if not nombre_archivo.endswith(".py"):
            continue
        base = _nombre_modulo(nombre_archivo)
        if base in IGNORAR:
            continue
        modulos[base] = analizar(os.path.join(LEGACY, nombre_archivo))

    internos = set(modulos)
    filas = []
    for base in sorted(modulos):
        info = modulos[base]
        dep_int = sorted(
            {_raiz_import(n) for n in info["nivel_modulo"] + info["diferidos"]} & internos
        )
        capa = "UI" if base.endswith(CAPA_UI_SUFIJOS) or info["gui_nivel_modulo"] else "CORE"
        filas.append((base, capa, info, dep_int))

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("# Matriz de mapeo: Macro/ → estructura objetivo\n\n")
        f.write("Generada por `tools/matriz_mapeo.py` (no editar a mano). Lee los imports reales con `ast`.\n\n")
        f.write("Capa: **CORE** = sin GUI a nivel de módulo (candidato a `freecad/vdo/core/`). "
                "**UI** = toca GUI/Qt a nivel de módulo o es un TaskPanel/widget (candidato a `freecad/vdo/ui/`).\n\n")
        f.write("| Módulo | Capa | GUI a nivel de módulo | Imports internos (nivel módulo + diferidos) | Imports GUI detectados |\n")
        f.write("|---|---|---|---|---|\n")
        for base, capa, info, dep in filas:
            gui = "**sí**" if info["gui_nivel_modulo"] else "no"
            dep_txt = ", ".join(dep) if dep else "—"
            gui_refs = ", ".join(info["gui_refs"]) if info["gui_refs"] else "—"
            f.write("| {} | {} | {} | {} | {} |\n".format(base, capa, gui, dep_txt, gui_refs))

        cnt = {"CORE": 0, "UI": 0}
        for _, capa, _, _ in filas:
            cnt[capa] += 1
        f.write("\n**Totales:** {} módulos; CORE: {}; UI: {}.\n".format(len(filas), cnt["CORE"], cnt["UI"]))

        violadores = [b for b, c, i, _ in filas if c == "CORE" and i["gui_nivel_modulo"]]
        f.write("\n**Incumplimientos de headless en CORE (debe estar vacío):** {}\n".format(violadores or "ninguno"))

    print("Matriz escrita en {} ({} módulos)".format(SALIDA, len(filas)))


if __name__ == "__main__":
    sys.exit(main())
