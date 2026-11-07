"""Fase de consola del workbench VDO.

FreeCAD ejecuta este archivo siempre, también sin interfaz gráfica (FreeCADCmd, CI).
Por eso NO importa FreeCADGui, PySide ni Qt.
"""

import os
import sys

import FreeCAD as App


def _module_dir():
    """Devuelve la carpeta raíz del módulo VDO (ver InitGui.py para el detalle)."""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        for entrada in sys.path:
            manifiesto = os.path.join(entrada, "package.xml")
            if os.path.isfile(manifiesto):
                with open(manifiesto, encoding="utf-8") as archivo:
                    if "<name>VDO</name>" in archivo.read():
                        return os.path.abspath(entrada)
        return None


App.Console.PrintMessage(f"[VDO] Módulo cargado desde: {_module_dir()}\n")
