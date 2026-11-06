"""Constantes del editor de reengrose: etiquetas, opciones de esquina y colores."""


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
    "vertical_domina": "#00b894",
    "horizontal_domina": "#e67e22",
    "inglete_45": "#9b59b6",
    "marco_interior": "#7f8c8d",
}
