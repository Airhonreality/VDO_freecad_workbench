"""Volcado serializable del árbol de widgets Qt (F-UI-2).

Genérico y sin FreeCAD: captura clases, textos, valores, rangos, tooltips,
visibilidad y orden de layout para comparar un formulario antes y después de
migrarlo a FormBuilder.
"""

from __future__ import annotations

from typing import Any

__all__ = ["volcar_arbol"]

_PROPIEDADES = (
    "text",
    "title",
    "value",
    "currentText",
    "currentData",
    "isChecked",
    "suffix",
    "decimals",
    "minimum",
    "maximum",
)


def _serializable(valor: Any) -> Any:
    """Convierte a JSON solo los tipos primitivos; el resto pasa a texto."""
    if valor is None or isinstance(valor, (bool, int, float, str)):
        return valor
    if isinstance(valor, (list, tuple)):
        return [_serializable(v) for v in valor]
    if isinstance(valor, dict):
        return {str(k): _serializable(v) for k, v in valor.items()}
    return str(valor)


def _leer(widget: Any, nombre: str) -> tuple[Any, bool]:
    """Devuelve (valor, existe) de un método sin argumentos del widget."""
    metodo = getattr(widget, nombre, None)
    if not callable(metodo):
        return None, False
    try:
        return metodo(), True
    except (TypeError, RuntimeError):
        return None, False


def _widgets_de_layout(layout: Any) -> list[Any]:
    """Widgets de un layout en orden, aplanando layouts anidados."""
    hijos = []
    for indice in range(layout.count()):
        elemento = layout.itemAt(indice)
        if elemento is None:
            continue
        widget = elemento.widget()
        if widget is not None:
            hijos.append(widget)
            continue
        sublayout = elemento.layout()
        if sublayout is not None:
            hijos.extend(_widgets_de_layout(sublayout))
    return hijos


def _hijos(widget: Any) -> list[Any]:
    """Hijos directos en orden de layout; vacío si el widget no tiene layout."""
    layout = widget.layout()
    return [] if layout is None else _widgets_de_layout(layout)


def _visible(widget: Any, padre: Any) -> bool:
    """Visibilidad relativa al padre: ignora que la ventana no se haya mostrado."""
    try:
        if padre is not None:
            return widget.isVisibleTo(padre)
        return widget.isVisible()
    except (TypeError, RuntimeError):
        return widget.isVisible()


def _nodo(widget: Any, padre: Any) -> dict[str, Any]:
    nodo: dict[str, Any] = {
        "clase": type(widget).__name__,
        "objectName": widget.objectName(),
        "toolTip": widget.toolTip(),
        "visible": _visible(widget, padre),
    }
    for nombre in _PROPIEDADES:
        valor, existe = _leer(widget, nombre)
        if existe:
            nodo[nombre] = _serializable(valor)
    nodo["hijos"] = [_nodo(hijo, widget) for hijo in _hijos(widget)]
    return nodo


def volcar_arbol(widget: Any) -> dict[str, Any]:
    """Devuelve un volcado serializable del widget y sus hijos en orden de layout."""
    return _nodo(widget, widget.parentWidget())
