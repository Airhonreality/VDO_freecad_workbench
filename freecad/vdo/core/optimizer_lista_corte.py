"""Lista de corte: lectura del CSV de vdo_cutting_list y expansión a piezas unitarias."""

import csv
import logging
from typing import Any

from freecad.vdo.core import defaults as _VDO_D

_LOG = logging.getLogger(__name__)

_CANTO_ESPESOR = {
    "FX": 0.0,
    "RIG": float(getattr(_VDO_D, "CANTO_GRUESO_DEFAULT", 2.0)),
    "SMRG": float(getattr(_VDO_D, "CANTO_MEDIO_DEFAULT", 1.0)),
}


# ----------------------------------------------------------------------
# 1. Lectura de la lista de corte (CSV de vdo_cutting_list)
# ----------------------------------------------------------------------
def read_cutting_csv(path):
    """Lee el CSV de lista de corte y devuelve una lista de piezas.

    Formato esperado (OpenCutList / vdo_cutting_list):
        Length,Width,Thickness,Quantity,Material,Name,Unit Cost,Total Cost

    Es tolerante: ignora filas vacías y filas no numéricas (p.ej. el TOTAL).
    """
    parts = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if not row or not row[0].strip():
                continue
            try:
                length = float(row[0])
                width = float(row[1])
                thickness = float(row[2])
                qty = int(float(row[3])) if row[3].strip() else 1
            except (ValueError, IndexError) as exc:
                _LOG.debug("optimizer_lista_corte: fila TOTAL o malformada, se omite: %s", exc)
                continue  # fila TOTAL / malformada

            material = row[4] if len(row) > 4 else ""
            name = (row[5] if len(row) > 5 else "").strip() or "pieza"

            cantos = {}
            for borde, indice in (("norte", 8), ("sur", 9),
                                  ("este", 10), ("oeste", 11)):
                valor = row[indice].strip().upper() if len(row) > indice else ""
                cantos[borde] = valor or "FX"

            parts.append({
                "name": name,
                "length": length,
                "width": width,
                "thickness": thickness,
                "qty": max(1, qty),
                "material": material,
                "cantos": cantos,
            })
    return parts


def expand_pieces(parts):
    """Expande cada pieza según su cantidad a unidades individuales.

    Cada unidad lleva un sufijo (#n) para poder identificarla en el preview.
    """
    pieces = []
    for p in parts:
        for i in range(p["qty"]):
            label = p["name"] if p["qty"] == 1 else f"{p['name']} #{i + 1}"
            pieces.append({
                "name": label,
                "w": p["width"],
                "h": p["length"],
                "thickness": p["thickness"],
                "material": p["material"],
                "cantos": dict(p.get("cantos") or {}),
            })
    return pieces


def _espesor_canto(cantos, borde):
    codigo = str((cantos or {}).get(borde, "FX")).upper()
    return _CANTO_ESPESOR.get(codigo, 0.0)


def _medidas_corte(pieza: dict[str, Any], descontar_cantos: bool) -> tuple[float, float]:
    """Cotas de corte antes del kerf.

    Norte/Sur descuentan sobre el ancho (``w``) y Este/Oeste sobre el
    largo (``h``). Con ``descontar_cantos=False`` se respetan las cotas
    nominales del CSV (caso proveedor externo).
    """
    w = float(pieza["w"])
    h = float(pieza["h"])
    if not descontar_cantos:
        return w, h

    cantos = pieza.get("cantos") or {}
    w -= _espesor_canto(cantos, "norte") + _espesor_canto(cantos, "sur")
    h -= _espesor_canto(cantos, "este") + _espesor_canto(cantos, "oeste")
    return max(0.0, w), max(0.0, h)
