"""Constantes, tablas e iconos del chasis. Parte de ui/chassis_widget.py (M7, D-45)."""


# ----------------------------------------------------------------------
# Iconografía Vectorial Lucide Embebida (SVG)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Constantes Semióticas de Chasis
# ----------------------------------------------------------------------
CARAS = ("superior", "inferior", "izquierda", "derecha", "fondo")
ENCUENTROS = ("superior_izq", "superior_der", "inferior_izq", "inferior_der")
TIPOS_ENCUENTRO = ("tapa_domina", "lateral_domina", "inglete_45")

ENCUENTRO_TOOLTIPS = {
    "tapa_domina": "Tapa/Base domina: El tablero horizontal vuela continuo de lado a lado (soporta cargas superiores de granito/mesones).",
    "lateral_domina": "Lateral domina: El costado vertical sube completo de punta a punta (ideal para módulos suspendidos o laterales a piso).",
    "inglete_45": "Inglete 45°: Ambas caras cortadas a bisel diagonal continuo (máxima estética de veta continua sin cantos vistos).",
}

ENCUENTRO_LABELS = {
    "tapa_domina": "Tapa/Base pasa",
    "lateral_domina": "Lateral pasa",
    "inglete_45": "Inglete 45°",
}

TIPOS_FONDO = [
    ("ranurado_5mm", "Ranura 5 mm", "ranura", "Fondo delgado de 5.5mm embutido en canal perimetral."),
    ("ranurado_3mm", "Ranura 3 mm", "ranura", "Fondo estándar de 3mm (MDF/Durolac) embutido en canal."),
    ("galce", "Galce / Rebaje", "galce", "Fondo embutido en rebaje fresado perimetral posterior."),
    ("atornillado", "Atornillado 15/18 mm", "atornillado", "Fondo estructural grueso de arriostramiento atornillado a tope."),
    ("abierto", "Abierto / Sin fondo", "abierto", "Mueble pasante sin trasera (estantería o mueble de paso)."),
]

# nombre del arquetipo -> configuracion del chasis que aplica
_ARQUETIPOS = {
    "COCO": {
        "caras": {
            "superior": {"activa": True, "tipo": "estructural"},
            "inferior": {"activa": True, "tipo": "estructural"},
            "izquierda": {"activa": True, "tipo": "estructural"},
            "derecha": {"activa": True, "tipo": "estructural"},
            "fondo": {"activa": True, "tipo": "ranurado_5mm"},
        },
        "encuentros": {
            "superior_izq": "tapa_domina",
            "superior_der": "tapa_domina",
            "inferior_izq": "lateral_domina",
            "inferior_der": "lateral_domina",
        },
        "base": {"estrategia": "zocalo", "altura": 100.0, "separacion_frente": 50.0},
    },
    "Mesa": {
        "caras": {
            "superior": {"activa": True, "tipo": "estructural"},
            "inferior": {"activa": False, "tipo": "estructural"},
            "izquierda": {"activa": True, "tipo": "estructural"},
            "derecha": {"activa": True, "tipo": "estructural"},
            "fondo": {"activa": True, "tipo": "atornillado"},
        },
        "encuentros": {
            "superior_izq": "tapa_domina",
            "superior_der": "tapa_domina",
            "inferior_izq": "lateral_domina",
            "inferior_der": "lateral_domina",
        },
        "base": {"estrategia": "patas", "altura": 20.0, "separacion_frente": 0.0},
    },
    "Estante": {
        "caras": {
            "superior": {"activa": False, "tipo": "estructural"},
            "inferior": {"activa": True, "tipo": "estructural"},
            "izquierda": {"activa": True, "tipo": "estructural"},
            "derecha": {"activa": True, "tipo": "estructural"},
            "fondo": {"activa": False, "tipo": "abierto"},
        },
        "encuentros": {
            "superior_izq": "lateral_domina",
            "superior_der": "lateral_domina",
            "inferior_izq": "lateral_domina",
            "inferior_der": "lateral_domina",
        },
        "base": {"estrategia": "zocalo", "altura": 80.0, "separacion_frente": 0.0},
    },
    "Aéreo": {
        "caras": {
            "superior": {"activa": True, "tipo": "estructural"},
            "inferior": {"activa": True, "tipo": "estructural"},
            "izquierda": {"activa": True, "tipo": "estructural"},
            "derecha": {"activa": True, "tipo": "estructural"},
            "fondo": {"activa": True, "tipo": "ranurado_5mm"},
        },
        "encuentros": {
            "superior_izq": "lateral_domina",
            "superior_der": "lateral_domina",
            "inferior_izq": "lateral_domina",
            "inferior_der": "lateral_domina",
        },
        "base": {"estrategia": "suspendido", "altura": 300.0, "separacion_frente": 0.0},
    },
}
