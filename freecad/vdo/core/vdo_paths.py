# -*- coding: utf-8 -*-
"""Rutas de recursos del propio módulo VDO.

Solo resuelve rutas dentro del repo (relativas a este archivo). No busca rutas de
instalación de FreeCAD ni de usuario: el código no depende de la instalación (D4).

La versión anterior buscaba la carpeta de macros, user.cfg y la raíz del repo de
sincronización en rutas fijas de cada distribución. Esa lógica se retiró con las
herramientas de sincronización (ver PLAN_CONVERSION_WORKBENCH_VDO.md, D14).
"""

from pathlib import Path


def ruta_icono(nombre):
    """Ruta absoluta de un icono SVG del repo (Resources/icons/<nombre>).

    Relativa a este archivo: freecad/vdo/core/vdo_paths.py -> raíz del módulo.
    """
    return Path(__file__).resolve().parents[3] / "Resources" / "icons" / nombre
