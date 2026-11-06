"""cad/transaccion.py — Guardado atómico de las propiedades de un objeto FreeCAD (D-88).

Un accept escribe varias propiedades en secuencia. Si una escritura o el
recálculo falla a mitad, el objeto queda con unas escritas y otras no. El panel
toma una foto de los valores antes de escribir y, en su camino de error, la
restaura con ``restaurar_propiedades``. El camino de éxito no usa la foto.
"""

from __future__ import annotations

from typing import Any

import FreeCAD as App

_TIPO_FORMA = "Part::PropertyPartShape"
_EQ_OBJETO: Any = object.__eq__


def foto_propiedades(obj: Any) -> dict[str, Any]:  # objeto FreeCAD sin tipo
    """Valores de las propiedades con igualdad por valor.

    Se excluyen las de forma (no se escriben) y las de objeto sin ``__eq__``
    (material, Proxy): no se pueden comparar, así que no se restauran.
    """
    foto: dict[str, Any] = {}
    for nombre in obj.PropertiesList:
        if obj.getTypeIdOfProperty(nombre) == _TIPO_FORMA:
            continue
        valor = getattr(obj, nombre)
        if type(valor).__eq__ is _EQ_OBJETO:
            continue
        foto[nombre] = valor
    return foto


def restaurar_propiedades(obj: Any, foto: dict[str, Any]) -> None:  # objeto FreeCAD sin tipo
    """Vuelve a escribir los valores de la foto que hayan cambiado.

    Un fallo al restaurar una propiedad no detiene la restauración de las demás:
    se registra y se sigue.
    """
    for nombre, valor in foto.items():
        try:
            if getattr(obj, nombre) != valor:
                setattr(obj, nombre, valor)
        except Exception as exc:
            App.Console.PrintWarning(
                f"[VDO] No se pudo restaurar {nombre}: {exc}\n")
