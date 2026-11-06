"""Especificación de los formularios de zócalo (M6, MN-08). Solo datos, sin lógica.

Cada grupo es (título, filas). Cada fila es la especificación de un campo que
FormBuilder.construir_grupo convierte en widgets. La fila de índice i ocupa la
fila i de la rejilla del grupo.
"""

from freecad.vdo.core.vdo_module_props import ANCLAJE_LABELS, ANCLAJES

ITEMS_ANCLAJE = [(ANCLAJE_LABELS.get(a, a), a) for a in ANCLAJES]

# clave del campo -> propiedad del objeto FreeCAD que la guarda
PROPIEDAD_ZOCALO = {
    "ancho": "Ancho",
    "fondo": "Fondo",
    "alto": "AltoZocalo",
    "espesor": "EspesorTablero",
    "frente": "DistanciaFrente",
    "costados": "DistanciaCostados",
    "trasera": "DistanciaTrasera",
    "trasera_habilitada": "TieneTrasera",
    "amarres": "AmarresIntermedios",
}

ZOCALO_GRUPOS = (
    ("Dimensiones del mueble", (
        {"tipo": "double_spin", "clave": "ancho", "etiqueta": "Ancho (mm):",
         "valor_defecto": 600.0, "rango": (1, 4000), "decimales": 1,
         "sufijo": " mm",
         "tooltip": "Ancho total del mueble; define el largo de la tira frontal."},
        {"tipo": "double_spin", "clave": "fondo", "etiqueta": "Fondo (mm):",
         "valor_defecto": 580.0, "rango": (1, 2000), "decimales": 1,
         "sufijo": " mm",
         "tooltip": "Fondo total del mueble; limita el largo de los laterales."},
        {"tipo": "double_spin", "clave": "alto", "etiqueta": "Alto zócalo (mm):",
         "valor_defecto": 120.0, "rango": (1, 400), "decimales": 1,
         "sufijo": " mm",
         "tooltip": "Altura física del zócalo (por ejemplo 100 o 120 mm)."},
        {"tipo": "spin", "clave": "espesor", "etiqueta": "Espesor tablero (mm):",
         "valor_defecto": 18, "rango": (1, 40), "sufijo": " mm",
         "tooltip": "Espesor de las tiras de melamina del zócalo."},
    )),
    ("Separación y encuentros", (
        {"tipo": "double_spin", "clave": "frente", "etiqueta": "Separación frontal:",
         "valor_defecto": 0.0, "rango": (0, 500), "decimales": 1, "sufijo": " mm",
         "tooltip": "Distancia desde el frente del mueble hacia adentro. "
                    "Deja espacio libre para no golpear los pies."},
        {"tipo": "double_spin", "clave": "costados", "etiqueta": "Distancia costados:",
         "valor_defecto": 0.0, "rango": (0, 500), "decimales": 1, "sufijo": " mm",
         "tooltip": "Separación desde cada costado del mueble (0 = al ras)."},
        {"tipo": "double_spin", "clave": "trasera", "etiqueta": "Distancia trasera:",
         "valor_defecto": 0.0, "rango": (0, 500), "decimales": 1, "sufijo": " mm",
         "tooltip": "Separación desde el fondo del mueble para librar el "
                    "rodapié de la pared."},
        {"tipo": "checkbox", "clave": "trasera_habilitada", "etiqueta": "Tiene trasera",
         "valor_defecto": True, "colspan": 2,
         "tooltip": "Cierra el cajón del zócalo por detrás."},
    )),
    ("Estructura", (
        {"tipo": "spin", "clave": "amarres", "etiqueta": "Divisiones interiores:",
         "valor_defecto": 0, "rango": (0, 20),
         "tooltip": "Partes iguales del hueco interior entre frente y trasera. "
                    "Se resuelven con el motor de división de vanos (vdo_layout)."},
    )),
    ("Colocación", (
        {"tipo": "double_spin", "clave": "rotacion", "etiqueta": "Rotación Z:",
         "valor_defecto": 0.0, "rango": (-360.0, 360.0), "decimales": 1,
         "sufijo": " °", "wrapping": True,
         "tooltip": "Rotación de colocación alrededor de Z. No cambia la geometría."},
        {"tipo": "combo", "clave": "anclaje", "etiqueta": "Anclaje:",
         "items": ITEMS_ANCLAJE,
         "tooltip": "Esquina del zócalo que se apoya en el punto de colocación."},
    )),
)
