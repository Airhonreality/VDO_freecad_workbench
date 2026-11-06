"""Especificación de los formularios de zócalo (M6, MN-08). Solo datos, sin lógica.

Cada grupo es (título, filas). Cada fila es la especificación de un campo que
FormBuilder.construir_grupo convierte en widgets. La fila de índice i ocupa la
fila i de la rejilla del grupo.
"""

from freecad.vdo.core import vdo_frames as VDO_FR
from freecad.vdo.core.aperturas import ETIQUETAS
from freecad.vdo.core.vdo_defaults import ORIENTACIONES_VALIDAS
from freecad.vdo.core.vdo_finish import CANTOS_VALIDOS
from freecad.vdo.core.vdo_module_props import ANCLAJE_LABELS, ANCLAJES
from freecad.vdo.core.vdo_puerta_despiece import SISTEMAS_APERTURA

ITEMS_ANCLAJE = [(ANCLAJE_LABELS.get(a, a), a) for a in ANCLAJES]

# Opciones del panel de puerta (antes en ui/puerta_task_constantes).
FAMILIAS = ["Batiente Vertical", "Basculante Horizontal", "Corrediza"]
SENTIDOS_BATIENTE = ["Izquierda", "Derecha", "Doble"]
SENTIDOS_BASCULANTE = ["Hacia Arriba", "Hacia Abajo"]
SENTIDOS_CORREDIZA = ["2 hojas", "3 hojas"]

AYUDA_CANTO = {
    "Norte": "Borde norte del tablero visto desde la cara A.",
    "Sur": "Borde sur del tablero visto desde la cara A.",
    "Este": "Borde este del tablero visto desde la cara A.",
    "Oeste": "Borde oeste del tablero visto desde la cara A.",
}

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


# --- Panel VDO (M6, MN-08, D-71) -------------------------------------------
# El panel se construye en dos tramos: los grupos antes del bloque de
# reengrose (que es un editor propio) y los grupos despues de el.

PANEL_GRUPOS_ANTES = (
    ("Panel", (
        {"tipo": "texto", "clave": "etiqueta", "etiqueta": "Etiqueta:",
         "tooltip": "Nombre visible de la pieza en el árbol y en la lista de corte."},
        {"tipo": "combo", "clave": "orientacion", "etiqueta": "Orientación:",
         "items": [(o, None) for o in ORIENTACIONES_VALIDAS],
         "tooltip": "Horizontal: el largo corre a lo ancho del mueble. "
                    "Vertical: el largo corre en altura."},
        {"tipo": "texto", "clave": "material", "etiqueta": "Material:",
         "tooltip": "Referencia de material del manifiesto, por ejemplo "
                    "melamina_standar."},
    )),
    ("Dimensiones", (
        {"tipo": "combo", "clave": "modo", "sin_etiqueta": True, "colspan": 2,
         "items": [("Directo", None), ("Expresión (fórmula)", None)],
         "tooltip": "Directo: valor numérico libre. "
                    "Expresión (fórmula): expresión nativa de FreeCAD que enlaza "
                    "cualquier propiedad del proyecto (p. ej. Params.Largo / 2)."},
        {"tipo": "expresion", "clave": "largo", "etiqueta": "Largo (mm):",
         "tooltip": "Largo real de la cara del tablero, no la diagonal ni el desarrollo."},
        {"tipo": "expresion", "clave": "ancho", "etiqueta": "Ancho (mm):",
         "tooltip": "Ancho de la cara del tablero. En un lateral vertical suele ser "
                    "la profundidad del mueble."},
        {"tipo": "expresion", "clave": "espesor", "etiqueta": "Espesor (mm):",
         "tooltip": "Espesor del tablero. El reengrose usa este valor por defecto."},
    )),
    ("Cantos", tuple(
        {"tipo": "combo", "clave": f"canto_{d.lower()}", "etiqueta": f"{d}:",
         "items": [(c, None) for c in CANTOS_VALIDOS],
         "tooltip": AYUDA_CANTO[d] + " RIG = canto rígido, SMRG = semi-rígido, "
                    "FX = sin canto."}
        for d in ("Norte", "Sur", "Este", "Oeste")
    )),
)

PANEL_GRUPOS_DESPUES = (
    ("Colocación", (
        {"tipo": "vdo_double_spin", "clave": "rotacion", "etiqueta": "Rotación Z:",
         "valor_defecto": 0.0, "rango": (-360.0, 360.0), "decimales": 1,
         "sufijo": " °", "wrapping": True,
         "tooltip": "Rotación de colocación alrededor de Z. No cambia las medidas "
                    "del tablero."},
        {"tipo": "combo", "clave": "anclaje", "etiqueta": "Anclaje:",
         "items": ITEMS_ANCLAJE,
         "tooltip": "Esquina del panel que se apoya en el punto de colocación."},
    )),
)


# --- Panel de puerta (M6, MN-08, D-72) ------------------------------------
# Bloques en orden de aparición. (clave, titulo, filas) es un grupo;
# (clave, None, filas) es un campo suelto. Los estilos (colores) los pone la UI.
PUERTA_BLOQUES = (
    ("familia", "Familia de puerta", (
        {"tipo": "combo", "clave": "sistema", "etiqueta": "Tipo de sistema:",
         "items": [(f, None) for f in FAMILIAS],
         "tooltip": "Batiente Vertical, Basculante Horizontal o Corrediza."},
    )),
    ("montaje", "Montaje (batiente)", (
        {"tipo": "combo", "clave": "montaje", "etiqueta": "Tipo de montaje:",
         "items": [(m, None) for m in ("Parche", "Semiparche", "Embebida")]},
        {"tipo": "combo", "clave": "sentido", "etiqueta": "Sentido de apertura:",
         "items": [(s, None) for s in SENTIDOS_BATIENTE]},
    )),
    ("dimensiones", "Dimensiones de la puerta (mm)", (
        {"tipo": "vdo_double_spin", "clave": "ancho", "etiqueta": "Ancho (W):",
         "valor_defecto": 100.0, "rango": (100, 3000), "decimales": 1, "sufijo": " mm"},
        {"tipo": "vdo_double_spin", "clave": "alto", "etiqueta": "Alto (H):",
         "valor_defecto": 100.0, "rango": (100, 2600), "decimales": 1, "sufijo": " mm"},
        {"tipo": "spin", "clave": "espesor", "etiqueta": "Espesor (mm):",
         "valor_defecto": 18, "rango": (10, 50), "sufijo": " mm"},
    )),
    ("apertura", "Sistema de apertura / fachada", (
        {"tipo": "combo", "clave": "apertura", "etiqueta": "Tipo:",
         "items": [(ETIQUETAS[k], None) for k in SISTEMAS_APERTURA]},
    )),
    ("herraje", "Herraje comercial", (
        {"tipo": "combo", "clave": "sku", "etiqueta": "SKU:", "items": []},
        {"tipo": "label", "clave": "info_herraje", "valor_defecto": "",
         "sin_etiqueta": True, "colspan": 2, "ajustar_texto": True, "estilo": "info"},
    )),
    ("piston", "Cálculo de pistón a gas", (
        {"tipo": "label", "clave": "info_piston", "valor_defecto": "",
         "sin_etiqueta": True, "colspan": 2, "ajustar_texto": True, "estilo": "piston"},
    )),
    ("expulsor", None, (
        {"tipo": "checkbox", "clave": "expulsor",
         "etiqueta": "Inyectar expulsor magnético al BOM", "estilo": "texto"},
    )),
    ("posicion", "Posición (mm)", (
        {"tipo": "vdo_double_spin", "clave": "pos_x", "etiqueta": "Pos X:",
         "valor_defecto": 0.0, "rango": (-5000, 5000), "decimales": 1, "sufijo": " mm"},
        {"tipo": "vdo_double_spin", "clave": "pos_y", "etiqueta": "Pos Y:",
         "valor_defecto": 0.0, "rango": (-5000, 5000), "decimales": 1, "sufijo": " mm"},
        {"tipo": "vdo_double_spin", "clave": "pos_z", "etiqueta": "Pos Z:",
         "valor_defecto": 0.0, "rango": (-5000, 5000), "decimales": 1, "sufijo": " mm"},
        {"tipo": "combo", "clave": "anclaje", "etiqueta": "Anclaje:",
         "items": ITEMS_ANCLAJE, "estilo": "texto"},
    )),
)


def cajon_bloques(marcas):
    """Especificación del panel de cajón (M6, D-73). `marcas` viene de listar_marcas()."""
    return (
        ("espacio", "Espacio interior (datos de partida)", (
            {"tipo": "vdo_double_spin", "clave": "li", "etiqueta": "Ancho libre LI (mm):",
             "rango": (1, 3000), "decimales": 1, "sufijo": " mm"},
            {"tipo": "vdo_double_spin", "clave": "prof", "etiqueta": "Profundidad libre (mm):",
             "rango": (1, 1500), "decimales": 1, "sufijo": " mm"},
            {"tipo": "vdo_double_spin", "clave": "ancho_mod", "etiqueta": "Ancho módulo (fachada):",
             "rango": (1, 3000), "decimales": 1, "sufijo": " mm"},
            {"tipo": "vdo_double_spin", "clave": "alto_frente", "etiqueta": "Alto frente (mm):",
             "rango": (1, 800), "decimales": 1, "sufijo": " mm"},
        )),
        ("herraje", "Corredera y herraje", (
            {"tipo": "combo", "clave": "tipo", "etiqueta": "Tipo de corredera:",
             "items": [(t, None) for t in ("Oculta (Blum Tandem / Genérica)",
                                           "Telescópica", "Metálica (Slim Box / Tandembox)")],
             "tooltip": ("Oculta: corredera bajo cajón con notch y pin.\n"
                         "Telescópica: guía lateral con piso delgado en ranura.\n"
                         "Metálica: sin laterales de madera, solo piso y trasera.")},
            {"tipo": "combo", "clave": "sku", "etiqueta": "SKU comercial:", "items": [],
             "editable": True,
             "tooltip": "SKU de la corredera (vía vdo_hardware_hub.py)."},
            {"tipo": "combo", "clave": "marca", "etiqueta": "Marca:",
             "items": [(m, None) for m in marcas],
             "tooltip": "Marca de corredera oculta (delta y cotas)."},
            {"tipo": "vdo_double_spin", "clave": "guia", "etiqueta": "Longitud guía (mm):",
             "rango": (0, 800), "decimales": 0, "sufijo": " mm",
             "texto_especial": "Auto (según profundidad)"},
            {"tipo": "combo", "clave": "montaje", "etiqueta": "Montaje trasera:",
             "items": [(m, None) for m in ("entre_laterales", "testa")]},
        )),
        ("apertura", "Sistema de apertura (fachada)", (
            {"tipo": "combo", "clave": "apertura", "etiqueta": "Sistema:",
             "items": [(a, None) for a in ("Tirador", "Gola aluminio (−35 mm altura)",
                                           "45° (bisel en arista superior)",
                                           "Push open (expulsor magnético)")],
             "tooltip": ("Tirador: manija postiza, altura completa.\n"
                         "Gola: perfil C/L integrado, descuenta 35 mm en altura.\n"
                         "45°: bisel paramétrico en arista superior frontal.\n"
                         "Push open: émbolo magnético, holgura perimetral ajustada.")},
            {"tipo": "combo", "clave": "montaje_fachada", "etiqueta": "Montaje fachada:",
             "items": [(m, None) for m in ("Parche", "Semiparche", "Embebida")],
             "tooltip": ("Parche: solapa sobre los cantos del vano.\n"
                         "Semiparche: comparte montante central.\n"
                         "Embebida: a ras dentro del vano (deja cantos vistos).")},
        )),
        ("caja", "Caja y fachada", (
            {"tipo": "vdo_double_spin", "clave": "alto_caja", "etiqueta": "Alto caja (mm):",
             "rango": (1, 300), "decimales": 1, "sufijo": " mm"},
            {"tipo": "spin", "clave": "g_caja", "etiqueta": "Grosor caja (mm):",
             "rango": (1, 25), "sufijo": " mm"},
            {"tipo": "spin", "clave": "g_fondo", "etiqueta": "Grosor piso (mm):",
             "rango": (1, 12), "sufijo": " mm"},
            {"tipo": "spin", "clave": "g_fachada", "etiqueta": "Grosor fachada (mm):",
             "rango": (1, 30), "sufijo": " mm"},
        )),
        ("colocacion", "Colocación", (
            {"tipo": "vdo_double_spin", "clave": "rotacion", "etiqueta": "Rotación Z:",
             "rango": (-360.0, 360.0), "decimales": 1, "sufijo": " °", "wrapping": True},
            {"tipo": "combo", "clave": "anclaje", "etiqueta": "Anclaje:",
             "items": ITEMS_ANCLAJE},
        )),
    )


# --- Panel COCO, campos simples (M6, MN-08, D-74) ---------------------------
# Solo los campos de valor único (medidas, rotación, anclaje y exposición).
# La matriz de espacios, la tabla de celdas, el árbol de hijos y el chasis
# quedan fuera de la especificación (ver D-74).

COCO_ESTADOS_EXPOSICION = (
    ("Oculto", "oculto"),
    ("Visto", "visto"),
    ("Apoyado", "apoyado"),
)

COCO_MEDIDAS = ("Medidas Generales", (
    {"tipo": "vdo_double_spin", "clave": "alto", "etiqueta": "Alto (mm):",
     "valor_defecto": 1.0, "rango": (1, 3000), "decimales": 1, "sufijo": " mm",
     "tooltip": ("Alto exterior total del mueble, de piso a techo, incluyendo "
                 "tapa y base.")},
    {"tipo": "vdo_double_spin", "clave": "ancho", "etiqueta": "Ancho (mm):",
     "valor_defecto": 1.0, "rango": (1, 3000), "decimales": 1, "sufijo": " mm",
     "tooltip": "Ancho exterior total del mueble, de lateral a lateral."},
    {"tipo": "vdo_double_spin", "clave": "fondo_modulo", "etiqueta": "Fondo módulo (mm):",
     "valor_defecto": 1.0, "rango": (1, 1500), "decimales": 1, "sufijo": " mm",
     "tooltip": "Profundidad exterior del mueble, desde el frente hasta el fondo."},
    {"tipo": "spin", "clave": "espesor", "etiqueta": "Espesor (mm):",
     "valor_defecto": 1, "rango": (1, 50), "sufijo": " mm",
     "tooltip": "Espesor del tablero de laterales, base, techo y divisiones."},
))

COCO_ROTACION = {
    "tipo": "vdo_double_spin", "clave": "rotacion", "etiqueta": "Rotación Z:",
    "valor_defecto": 0.0, "rango": (-360.0, 360.0), "decimales": 1,
    "sufijo": " °", "wrapping": True,
    "tooltip": "Rotación de colocación alrededor de Z. No cambia las medidas del mueble.",
}

COCO_ROTACION_PASOS = (
    {"texto": "-90°", "delta": -90.0,
     "tooltip": "Gira el mueble 90° en sentido horario."},
    {"texto": "+90°", "delta": 90.0,
     "tooltip": "Gira el mueble 90° en sentido antihorario."},
)

COCO_ANCLAJE = {
    "tipo": "combo", "clave": "anclaje", "etiqueta": "Anclaje:",
    "items": ITEMS_ANCLAJE,
    "tooltip": "Esquina del mueble que se apoya en el punto de colocación.",
}

COCO_EXPOSICION = tuple(
    (lado, {"tipo": "combo", "clave": f"exp_{lado}", "etiqueta": f"{etiqueta}:",
            "items": COCO_ESTADOS_EXPOSICION,
            "tooltip": ("Visto: cara exterior visible. Apoyado: contra muro/piso. "
                        "Oculto: sin exposición.")})
    for lado, etiqueta in (
        (VDO_FR.FRENTE, "Frente"), (VDO_FR.FONDO, "Fondo"),
        (VDO_FR.IZQUIERDA, "Izquierda"), (VDO_FR.DERECHA, "Derecha"),
        (VDO_FR.SUPERIOR, "Superior"), (VDO_FR.INFERIOR, "Inferior"),
    )
)
