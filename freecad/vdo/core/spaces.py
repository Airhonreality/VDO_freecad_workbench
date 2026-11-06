# =====================================================================
# spaces.py
# Motor de resolución de espacios libres para COCO VDO
# Axioma 2: Lógica pura, sin dependencias de UI ni FreeCAD
#
# ⚠ DEPRECATED (VDO): motor legacy de espacios 1D.
# No usar en código nuevo. La fuente única es vdo_layout.Layout /
# VDO_Divisiones (matriz de vanos v2). Este archivo se conserva sólo
# para compatibilidad temporal y será eliminado físicamente del repo
# en la próxima fase de saneamiento.
# =====================================================================

from __future__ import annotations

import json
import logging
from typing import Any

_LOG = logging.getLogger(__name__)

# --- Constantes de tipos de espacio ---
ESPACIO_FIJO = "fijo"
ESPACIO_RESTANTE = "restante"
ESPACIO_IGUALES = "iguales"


class SpaceNode:
    """Nodo de un árbol de espacios libres.

    Cada nodo representa un espacio que puede contener sub-espacios
    en el eje opuesto (recursividad bidimensional).
    """

    def __init__(self, space_type: str = ESPACIO_FIJO, value: float = 0.0,
                 children: list[SpaceNode] | None = None,
                 space_id: str | None = None, parent_id: str | None = None,
                 axis: str | None = None) -> None:
        self.space_type = space_type
        self.value = value
        self.children: list[SpaceNode] = children or []
        self.space_id = space_id or "auto"
        self.parent_id = parent_id or ""
        self.axis = axis

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": self.space_type,
            "id": self.space_id,
            "parent": self.parent_id,
        }
        if self.space_type == ESPACIO_FIJO:
            d["value"] = self.value
        elif self.space_type == ESPACIO_IGUALES:
            d["count"] = int(self.value)
        if self.children:
            d["axis"] = self.axis or "X"
            for child in self.children:
                if not child.parent_id:
                    child.parent_id = self.space_id
            d["children"] = [c.to_dict() for c in self.children]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SpaceNode:
        node = cls(
            space_type=d.get("type", ESPACIO_FIJO),
            value=d.get("value", 0.0),
            space_id=d.get("id", "auto"),
            parent_id=d.get("parent", ""),
            axis=d.get("axis"),
        )
        if d.get("count") is not None:
            node.value = float(d["count"])
        for child_data in d.get("children", []):
            child = cls.from_dict(child_data)
            if not child.parent_id:
                child.parent_id = node.space_id
            node.children.append(child)
        return node

    def __repr__(self) -> str:
        return (f"SpaceNode(type={self.space_type}, value={self.value}, "
                f"id={self.space_id}, children={len(self.children)})")


def deserializar_espacios(json_str: str) -> list[SpaceNode]:
    """Deserializa JSON a lista de SpaceNode."""
    if not json_str or not json_str.strip():
        return []
    try:
        data = json.loads(json_str)
        return [SpaceNode.from_dict(d) for d in data]
    except (json.JSONDecodeError, TypeError) as exc:
        _LOG.warning("spaces: JSON de espacios no valido, usa lista vacia: %s", exc)
        return []


def _division_iguales(nodes: list[SpaceNode], espacio_total: float,
                      espesor: float) -> tuple[float, float]:
    """Espacio disponible y ancho de cada división de los nodos 'iguales'."""
    espacio_disponible = espacio_total

    if espacio_disponible < 0:
        espacio_disponible = 0.0

    fijos = [n for n in nodes if n.space_type == ESPACIO_FIJO]
    restantes = [n for n in nodes if n.space_type == ESPACIO_RESTANTE]
    iguales = [n for n in nodes if n.space_type == ESPACIO_IGUALES]

    espacio_consumido_fijos = sum(n.value for n in fijos)
    espacio_para_iguales = espacio_disponible - espacio_consumido_fijos

    if restantes:
        espacio_para_iguales = max(0, espacio_para_iguales)

    if iguales and espacio_para_iguales > 0:
        n_div_iguales = sum(int(n.value) for n in iguales)
        # Cada grupo de N iguales aporta N-1 separadores internos.
        separadores_iguales = sum(max(0, int(n.value) - 1) for n in iguales)
        espacio_para_dividir = espacio_para_iguales - separadores_iguales * espesor
        espacio_para_dividir = max(0, espacio_para_dividir)
        espacio_cada_div = (espacio_para_dividir / n_div_iguales
                            if n_div_iguales > 0 else 0)
    else:
        espacio_cada_div = 0
    return espacio_disponible, espacio_cada_div


def _nodo_fijo(node: SpaceNode, cursor: float, espacio_disponible: float,
               espesor: float) -> tuple[dict[str, Any], float]:
    """Resuelve un nodo 'fijo'. Devuelve (resuelto, nuevo_cursor)."""
    libre = min(node.value, max(0, espacio_disponible - cursor))
    resuelto: dict[str, Any] = {
        "id": node.space_id,
        "inicio": cursor,
        "fin": cursor + libre,
        "libre": libre,
        "tipo": ESPACIO_FIJO,
        "children": [],
    }
    if node.children:
        resuelto["children"] = _resolver_subespacios(
            node.children, libre, espesor)
    return resuelto, cursor + libre


def _nodo_iguales(node: SpaceNode, cursor: float, espacio_cada_div: float,
                  espesor: float) -> tuple[dict[str, Any], float]:
    """Resuelve un nodo 'iguales' en N subespacios. Devuelve (resuelto, nuevo_cursor)."""
    n_sub = max(1, int(node.value))
    espacio_total_este = espacio_cada_div * n_sub
    sub_cursor = cursor
    sub_spaces: list[dict[str, Any]] = []
    for j in range(n_sub):
        sub_spaces.append({
            "id": f"{node.space_id}_{j+1}",
            "inicio": sub_cursor,
            "fin": sub_cursor + espacio_cada_div,
            "libre": espacio_cada_div,
            "tipo": ESPACIO_FIJO,
            "children": [],
        })
        sub_cursor += espacio_cada_div
        if j < n_sub - 1:
            sub_cursor += espesor

    resuelto: dict[str, Any] = {
        "id": node.space_id,
        "inicio": cursor,
        "fin": sub_cursor,
        "libre": espacio_total_este,
        "tipo": ESPACIO_IGUALES,
        "children": sub_spaces,
    }
    return resuelto, sub_cursor


def _nodo_restante(node: SpaceNode, cursor: float, espacio_disponible: float,
                   espesor: float) -> tuple[dict[str, Any], float]:
    """Resuelve un nodo 'restante'. Devuelve (resuelto, nuevo_cursor)."""
    libre = max(0, espacio_disponible - cursor)
    resuelto: dict[str, Any] = {
        "id": node.space_id,
        "inicio": cursor,
        "fin": cursor + libre,
        "libre": libre,
        "tipo": ESPACIO_RESTANTE,
        "children": [],
    }
    if node.children:
        resuelto["children"] = _resolver_subespacios(
            node.children, libre, espesor)
    return resuelto, cursor + libre


def _resolver_nodo(node: SpaceNode, cursor: float, espacio_disponible: float,
                   espacio_cada_div: float,
                   espesor: float) -> tuple[dict[str, Any] | None, float]:
    """Despacha un nodo a su resolutor. Tipo desconocido: (None, cursor)."""
    if node.space_type == ESPACIO_FIJO:
        return _nodo_fijo(node, cursor, espacio_disponible, espesor)
    if node.space_type == ESPACIO_IGUALES:
        return _nodo_iguales(node, cursor, espacio_cada_div, espesor)
    if node.space_type == ESPACIO_RESTANTE:
        return _nodo_restante(node, cursor, espacio_disponible, espesor)
    return None, cursor


def resolver_espacios_eje(nodes: list[SpaceNode], espacio_total: float,
                          espesor: float) -> list[dict[str, Any]]:
    """Resuelve una lista de nodos en posiciones físicas a lo largo de un eje.

    Args:
        nodes: Lista de SpaceNode (definition-level, no nested).
        espacio_total: Espacio libre total disponible en mm.
        espesor: Espesor de las piezas divisorias en mm.

    Returns:
        Lista de dicts con la información de cada espacio resuelto:
        [
            {
                "id": str,
                "inicio": float,    # posición inicial del espacio libre
                "fin": float,       # posición final del espacio libre
                "libre": float,     # espacio libre en mm
                "tipo": str,        # "fijo", "restante", "iguales"
                "children": list,   # sub-espacios resueltos (si existen)
            },
            ...
        ]
    """
    if not nodes:
        return [{"id": "_full", "inicio": 0.0, "fin": espacio_total,
                 "libre": espacio_total, "tipo": "fijo", "children": []}]

    espacio_disponible, espacio_cada_div = _division_iguales(
        nodes, espacio_total, espesor)

    resultado: list[dict[str, Any]] = []
    cursor = 0.0

    for i, node in enumerate(nodes):
        resuelto, cursor = _resolver_nodo(
            node, cursor, espacio_disponible, espacio_cada_div, espesor)
        if resuelto is not None:
            resultado.append(resuelto)

        if i < len(nodes) - 1:
            cursor += espesor

    return resultado


def _reparto_iguales(children: list[SpaceNode], espacio_libre: float,
                     espesor: float) -> float:
    """Espacio que recibe cada division de los nodos ESPACIO_IGUALES del nivel."""
    espacio_disponible = espacio_libre
    fijos = [c for c in children if c.space_type == ESPACIO_FIJO]
    iguales = [c for c in children if c.space_type == ESPACIO_IGUALES]
    espacio_consumido = sum(c.value for c in fijos)
    espacio_para_iguales = espacio_disponible - espacio_consumido
    if not (iguales and espacio_para_iguales > 0):
        return 0
    n_div = sum(int(c.value) for c in iguales)
    separadores_iguales = sum(max(0, int(c.value) - 1) for c in iguales)
    espacio_para_dividir = max(
        0, espacio_para_iguales - separadores_iguales * espesor)
    return espacio_para_dividir / n_div if n_div > 0 else 0


def _entrada_libre(child: SpaceNode, cursor: float, libre: float,
                   espesor: float) -> dict[str, Any]:
    """Entrada de un nodo fijo o restante cuyo espacio libre ya esta resuelto."""
    return {
        "id": child.space_id,
        "inicio": cursor,
        "fin": cursor + libre,
        "libre": libre,
        "tipo": child.space_type,
        "children": _resolver_subespacios(
            child.children, libre, espesor) if child.children else [],
    }


def _entrada_iguales(child: SpaceNode, cursor: float, espacio_cada: float,
                     espesor: float) -> tuple[dict[str, Any], float]:
    """Entrada de un nodo ESPACIO_IGUALES. Devuelve (entrada, cursor nuevo)."""
    n_sub = max(1, int(child.value))
    sub_cursor = cursor
    sub_spaces: list[dict[str, Any]] = []
    for j in range(n_sub):
        sub_spaces.append({
            "id": f"{child.space_id}_{j+1}",
            "inicio": sub_cursor,
            "fin": sub_cursor + espacio_cada,
            "libre": espacio_cada,
            "tipo": ESPACIO_FIJO,
            "children": [],
        })
        sub_cursor += espacio_cada
        if j < n_sub - 1:
            sub_cursor += espesor
    entrada: dict[str, Any] = {
        "id": child.space_id,
        "inicio": cursor,
        "fin": sub_cursor,
        "libre": espacio_cada * n_sub,
        "tipo": ESPACIO_IGUALES,
        "children": sub_spaces,
    }
    return entrada, sub_cursor


def _resolver_subespacios(children: list[SpaceNode], espacio_libre: float,
                          espesor: float) -> list[dict[str, Any]]:
    """Resuelve sub-espacios recursivamente en el eje opuesto."""
    if not children or espacio_libre <= 0:
        return []

    espacio_disponible = espacio_libre
    espacio_cada = _reparto_iguales(children, espacio_libre, espesor)

    resultado: list[dict[str, Any]] = []
    cursor = 0.0

    for i, child in enumerate(children):
        if child.space_type == ESPACIO_FIJO:
            libre = min(child.value, max(0, espacio_disponible - cursor))
            resultado.append(_entrada_libre(child, cursor, libre, espesor))
            cursor += libre

        elif child.space_type == ESPACIO_IGUALES:
            entrada, cursor = _entrada_iguales(
                child, cursor, espacio_cada, espesor)
            resultado.append(entrada)

        elif child.space_type == ESPACIO_RESTANTE:
            libre = max(0, espacio_disponible - cursor)
            resultado.append(_entrada_libre(child, cursor, libre, espesor))
            cursor += libre

        if i < len(children) - 1:
            cursor += espesor

    return resultado
