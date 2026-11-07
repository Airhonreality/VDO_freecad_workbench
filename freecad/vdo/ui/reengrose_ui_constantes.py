"""Constantes del editor de reengrose: etiquetas, opciones de esquina y colores."""

from freecad.vdo.ui import tema_colores

LABEL_BORDE = {
    "frente": "Frente",
    "fondo": "Fondo",
    "izquierda": "Izquierda",
    "derecha": "Derecha",
}

LABEL_ESQUINA = {
    "frente_izquierda": "Frente izq.",
    "frente_derecha": "Frente der.",
    "fondo_izquierda": "Fondo izq.",
    "fondo_derecha": "Fondo der.",
}

OPCIONES_ESQUINA = (
    ("A tope lateral (Vertical domina)", "vertical_domina"),
    ("A tope frontal (Horizontal domina)", "horizontal_domina"),
    ("Inglete 45°", "inglete_45"),
    ("Marco interior", "marco_interior"),
)

COLOR_ESQUINA = {
    "vertical_domina": tema_colores.COLOR_CATEGORIA_VERTICAL,
    "horizontal_domina": tema_colores.COLOR_NARANJA,
    "inglete_45": tema_colores.COLOR_CATEGORIA_INGLETE,
    "marco_interior": tema_colores.COLOR_CATEGORIA_MARCO,
}
