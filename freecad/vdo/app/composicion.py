# -*- coding: utf-8 -*-
"""app/composicion.py — Composición única del contexto VDO (M-06, M-08).

Construye el contexto una vez por sesión: manifiesto y catálogo inmutables,
pasados como parámetro a los casos de uso. Sin estado mutable de módulo.
"""

from __future__ import annotations

from typing import Any

from freecad.vdo.core import vdo_manifest as VM
from freecad.vdo.core import vdo_hardware_hub as HH


class Contexto:
    """Contexto de sesión: manifiesto y catálogo inmutables."""

    def __init__(self, manifiesto: dict, catalogo: dict):
        self._manifiesto = manifiesto
        self._catalogo = catalogo

    @property
    def manifiesto(self) -> dict:
        return self._manifiesto

    @property
    def catalogo(self) -> dict:
        return self._catalogo


def contexto() -> Contexto:
    """Construye el contexto de sesión (manifiesto + catálogo inmutables).

    Se carga una vez por sesión. Para recargar, llamar a
    casos_uso.recargar_catalogo().
    """
    manifiesto = VM.get_loader()  # carga fresca del JSON
    catalogo = HH._catalogo_completo()  # carga fresca del catálogo
    return Contexto(manifiesto, catalogo)
