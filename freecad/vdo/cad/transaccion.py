"""cad/transaccion.py — Guardado atómico de las propiedades de un objeto FreeCAD (D-88).

Un accept escribe varias propiedades en secuencia, y a veces añade otras. Si una
escritura o el recálculo falla a mitad, el objeto queda con unas escritas y
otras no. El panel toma una foto antes de escribir y, en su camino de error, la
restaura con ``restaurar_propiedades``: quita las propiedades añadidas y vuelve
a escribir los valores cambiados. El camino de éxito no usa la foto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import FreeCAD as App

_TIPO_FORMA = "Part::PropertyPartShape"
_EQ_OBJETO: Any = object.__eq__


@dataclass(frozen=True)
class FotoPropiedades:
    """Nombres de las propiedades del objeto y valores con igualdad por valor."""

    nombres: frozenset[str]
    valores: dict[str, Any] = field(default_factory=dict)


def foto_propiedades(obj: Any) -> FotoPropiedades:  # objeto FreeCAD sin tipo
    """Foto del objeto antes de escribir.

    Los valores excluyen las propiedades de forma (no se escriben) y las de
    objeto sin ``__eq__`` (material, Proxy): no se pueden comparar, así que no
    se restauran.
    """
    valores: dict[str, Any] = {}
    for nombre in obj.PropertiesList:
        if obj.getTypeIdOfProperty(nombre) == _TIPO_FORMA:
            continue
        valor = getattr(obj, nombre)
        if type(valor).__eq__ is _EQ_OBJETO:
            continue
        valores[nombre] = valor
    return FotoPropiedades(frozenset(obj.PropertiesList), valores)


def restaurar_propiedades(obj: Any, foto: FotoPropiedades) -> None:  # objeto FreeCAD sin tipo
    """Devuelve el objeto al estado de la foto.

    Quita las propiedades añadidas después de la foto y vuelve a escribir los
    valores que hayan cambiado. Un fallo en una propiedad no detiene las demás:
    se registra y se sigue.
    """
    for nombre in list(obj.PropertiesList):
        if nombre in foto.nombres:
            continue
        try:
            obj.removeProperty(nombre)
        except Exception as exc:
            App.Console.PrintWarning(
                f"[VDO] No se pudo quitar {nombre}: {exc}\n")
    for nombre, valor in foto.valores.items():
        try:
            if getattr(obj, nombre) != valor:
                setattr(obj, nombre, valor)
        except Exception as exc:
            App.Console.PrintWarning(
                f"[VDO] No se pudo restaurar {nombre}: {exc}\n")
