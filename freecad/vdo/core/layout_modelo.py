# =====================================================================
# vdo_layout.py
# Motor puro de la matriz de vanos del COCO.
#
# No importa FreeCAD ni Qt: sólo datos, medidas y geometría 2D.
#
# MARCO LOCAL 3D (ley única definida en frames.py):
#   X+ = derecha
#   Y+ = fondo / profundidad
#   Z+ = altura
#   Frente funcional = Y-
#
# CONVENCIÓN DE LA MATRIZ 2D (sólo pantalla / filas):
#   X = ancho interior, crece de izquierda a derecha.
#   Y = filas de la matriz, crece de abajo hacia arriba.
#
# IMPORTANTE: la "Y" de la matriz es SOLO una convención cartesiana 2D
# para nombrar filas. En el espacio 3D se proyecta sobre Z (altura).
# La profundidad física es Y, nunca la altura. Internamente las celdas
# resueltas usan (x, z, w, h), donde z es la elevación física.
#
# Coordenadas de usuario:
#   (x1,y1), (x2,y1), (x2.1,y1), (x2.1,y1.2), ...
# =====================================================================


VERSION = 2
AXIS_X = "X"
AXIS_Y = "Y"
EPS = 1e-7


class LayoutError(ValueError):
    """Error de validación de la matriz de vanos."""


def _to_float(valor):
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _sufijo_id(track_id, prefijo):
    texto = str(track_id or "")
    if texto.startswith(prefijo):
        texto = texto[len(prefijo):]
    return texto or "1"


def _id_unico(prefijo, existentes):
    usados = {str(x) for x in existentes}
    n = 1
    while f"{prefijo}{n}" in usados:
        n += 1
    return f"{prefijo}{n}"


def cavidad_interior(alto, ancho, espesor):
    """Devuelve la cavidad libre interior del COCO.

    Laterales, base y tapa consumen un espesor por cada cara, independiente
    de si la tapa/base son internas o externas.
    """
    t = max(0.0, float(espesor))
    ancho = max(0.0, float(ancho))
    alto = max(0.0, float(alto))
    return {
        "x0": t,
        "z0": t,
        "ancho": max(0.0, ancho - 2.0 * t),
        "alto": max(0.0, alto - 2.0 * t),
    }


class Track:
    """Columna o fila de la matriz raíz."""

    def __init__(self, track_id, fixed=None):
        self.id = str(track_id)
        self.fixed = _to_float(fixed)

    def to_dict(self):
        return {"id": self.id, "fixed": self.fixed}

    @classmethod
    def from_dict(cls, data, prefijo, indice):
        if isinstance(data, str):
            return cls(data)
        return cls(
            data.get("id") or f"{prefijo}{indice + 1}",
            data.get("fixed"),
        )

    def copy(self):
        return Track(self.id, self.fixed)


class Cell:
    """Vano de la matriz y, recursivamente, sus subdivisiones."""

    def __init__(self, px="1", py="1", fixed=None, axis=None,
                 children=None):
        self.px = str(px)
        self.py = str(py)
        self.fixed = _to_float(fixed)
        self.axis = axis if axis in (AXIS_X, AXIS_Y) else None
        self.children = list(children or [])

    @property
    def label(self):
        return f"(x{self.px}, y{self.py})"

    def to_dict(self):
        data = {
            "px": self.px,
            "py": self.py,
            "fixed": self.fixed,
        }
        if self.axis and self.children:
            data["axis"] = self.axis
            data["children"] = [c.to_dict() for c in self.children]
        return data

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls()
        children = [
            cls.from_dict(c) for c in data.get("children", [])
            if isinstance(c, dict)
        ]
        axis = data.get("axis")
        if axis not in (AXIS_X, AXIS_Y):
            axis = None
        if not children:
            axis = None
        return cls(
            px=data.get("px", "1"),
            py=data.get("py", "1"),
            fixed=data.get("fixed"),
            axis=axis,
            children=children,
        )

    def copy(self):
        return Cell.from_dict(self.to_dict())
