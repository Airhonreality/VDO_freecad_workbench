# -*- coding: utf-8 -*-
"""Genera dist/VDO-<versión>.zip con solo lo necesario para el workbench.

La versión se lee de package.xml (única fuente de verdad, D11).

Incluye: package.xml, Init.py, InitGui.py, freecad/, Resources/, LICENSE, README.md.
Excluye: tests/, tools/, docs/, dist/, .git/, .claude/, node_modules/ y cachés de Python.

Uso: python3 tools/build_zip.py
"""

import os
import re
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ_ZIP = "VDO"  # carpeta raíz dentro del ZIP: al descomprimir en Mod/ queda Mod/VDO/

INCLUIR_FICHEROS = ["package.xml", "Init.py", "InitGui.py", "LICENSE", "README.md"]
INCLUIR_CARPETAS = ["freecad", "Resources"]
EXCLUIR_NOMBRES = {"__pycache__", ".DS_Store"}
EXCLUIR_EXTENSIONES = (".pyc", ".pyo", ".FCBak")


def leer_version():
    with open(os.path.join(RAIZ, "package.xml"), encoding="utf-8") as f:
        m = re.search(r"<version>\s*([^<\s]+)\s*</version>", f.read())
    if not m:
        raise SystemExit("package.xml sin <version>")
    return m.group(1)


def _ficheros_a_incluir():
    for f in INCLUIR_FICHEROS:
        ruta = os.path.join(RAIZ, f)
        if not os.path.isfile(ruta):
            raise SystemExit(f"Falta un fichero obligatorio para el ZIP: {f}")
        yield ruta, f
    for carpeta in INCLUIR_CARPETAS:
        base = os.path.join(RAIZ, carpeta)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in EXCLUIR_NOMBRES]
            for nombre in filenames:
                if nombre in EXCLUIR_NOMBRES or nombre.endswith(EXCLUIR_EXTENSIONES):
                    continue
                ruta = os.path.join(dirpath, nombre)
                yield ruta, os.path.relpath(ruta, RAIZ)


def main():
    version = leer_version()
    destino_dir = os.path.join(RAIZ, "dist")
    os.makedirs(destino_dir, exist_ok=True)
    zip_path = os.path.join(destino_dir, f"VDO-{version}.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    n = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta, rel in _ficheros_a_incluir():
            z.write(ruta, os.path.join(RAIZ_ZIP, rel))
            n += 1
    print(f"ZIP generado: {zip_path} ({n} ficheros)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
