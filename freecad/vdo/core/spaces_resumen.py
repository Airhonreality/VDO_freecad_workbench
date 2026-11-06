"""Resumen de texto y espacio libre total de la resolucion de espacios 1D.
Extraido de spaces.py (M7, D-86)."""

from typing import Any

from freecad.vdo.core.spaces import (
    ESPACIO_IGUALES,
    ESPACIO_RESTANTE,
    deserializar_espacios,
    resolver_espacios_eje,
)


def generar_texto_resumen(espacios_resueltos: list[dict[str, Any]], eje_label: str = "X") -> str:
    """Genera un texto legible del resultado de la resolución de espacios."""
    lineas: list[str] = []
    for esp in espacios_resueltos:
        libre = esp["libre"]
        tipo = esp["tipo"]
        if tipo == ESPACIO_RESTANTE:
            tipo_label = "Restante"
        elif tipo == ESPACIO_IGUALES:
            tipo_label = f"Iguales ({len(esp.get('children', []))} partes)"
        else:
            tipo_label = "Fijo"
        lineas.append(
            f"  {esp['id']}: {libre:.1f}mm libres [{tipo_label}]")
        for sub in esp.get("children", []):
            lineas.append(
                f"    {sub['id']}: {sub['libre']:.1f}mm libres")
    return f"Eje {eje_label}:\n" + "\n".join(lineas) if lineas else ""


def calcular_espacio_libre(espacios_json: str, espacio_total: float,
                           espesor: float) -> dict[str, Any]:
    """Calcula el espacio libre total y el último vano remanente.

    Returns:
        dict: {
            "total_libre": float,
            "ultimo_vano": float,
            "n_espacios": int,
            "texto": str
        }
    """
    nodes = deserializar_espacios(espacios_json)
    if not nodes:
        return {
            "total_libre": espacio_total,
            "ultimo_vano": espacio_total,
            "n_espacios": 0,
            "texto": f"Sin divisiones. Espacio libre: {espacio_total:.1f}mm",
        }

    resueltos = resolver_espacios_eje(nodes, espacio_total, espesor)
    total = sum(e["libre"] for e in resueltos)
    ultimo = resueltos[-1]["libre"] if resueltos else espacio_total

    return {
        "total_libre": total,
        "ultimo_vano": ultimo,
        "n_espacios": len(resueltos),
        "texto": generar_texto_resumen(resueltos),
    }
