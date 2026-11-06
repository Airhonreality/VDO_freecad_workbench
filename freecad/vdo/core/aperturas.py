"""Sistemas de apertura: una sola tabla (MN-06, M3).

Cada sistema se define aquí una vez: clave del contrato, etiqueta de UI, operación de canto,
si aplica descuento de gola, bisel a 45°, expulsor magnético, descuento de altura y los
nombres legados que se aceptan. Los consumidores (facade_contract, vdo_cajon_despiece,
puerta_despiece, ui/puerta_task) leen de esta tabla. Los motores de cálculo de
cajón y puerta siguen separados: solo se unifica la tabla de reglas.
"""

from freecad.vdo.datos.valores import TIRADOR

# 1. DATOS -------------------------------------------------------------

OPERACION_CANTO_ESTANDAR = "CANTO_ESTANDAR"
OPERACION_CANTO_GOLA = "CORTE_RECTO_GOLA"
OPERACION_CANTO_45 = "BISEL_45"
GOLA_DESCUENTO_ALTURA_DEFAULT = 35.0  # mm que se restan a la altura de la fachada (perfil C/L)

APERTURA_TIRADOR = TIRADOR
APERTURA_GOLA = "gola_aluminio"
APERTURA_45_GRADOS = "inglete_45"
APERTURA_PUSH_OPEN = "push_open"

# Orden: el mismo que muestra el selector de puerta.
SISTEMAS = {
    APERTURA_TIRADOR: {
        "etiqueta": "Tirador Tradicional", "operacion": OPERACION_CANTO_ESTANDAR,
        "descuento_alto": 0.0, "descuento_gola": False, "bisel_45": False, "expulsor": False,
        "legado": ("tirador tradicional", TIRADOR),
    },
    APERTURA_45_GRADOS: {
        "etiqueta": "Inglete 45 Grados", "operacion": OPERACION_CANTO_45,
        "descuento_alto": 0.0, "descuento_gola": False, "bisel_45": True, "expulsor": False,
        "legado": ("inglete 45 grados", "fachada_a_45_grados", "inglete_45"),
    },
    APERTURA_GOLA: {
        "etiqueta": "Perfil Gola", "operacion": OPERACION_CANTO_GOLA,
        "descuento_alto": GOLA_DESCUENTO_ALTURA_DEFAULT, "descuento_gola": True,
        "bisel_45": False, "expulsor": False,
        "legado": ("perfil gola", "perfil_gola_aluminio", "gola_aluminio"),
    },
    APERTURA_PUSH_OPEN: {
        "etiqueta": "Push to Open", "operacion": OPERACION_CANTO_ESTANDAR,
        "descuento_alto": 0.0, "descuento_gola": False, "bisel_45": False, "expulsor": True,
        "legado": ("push to open", "push_open_mecanico", "push_open"),
    },
}

# 2. DERIVADOS (una sola fuente: la tabla) ---------------------------------

SISTEMAS_APERTURA = tuple(SISTEMAS)
SISTEMAS_APERTURA_VALIDOS = SISTEMAS_APERTURA
ETIQUETAS = {k: v["etiqueta"] for k, v in SISTEMAS.items()}
SISTEMA_POR_ETIQUETA = {v: k for k, v in ETIQUETAS.items()}
LEGADO_A_CONTRATO = {n: k for k, v in SISTEMAS.items() for n in v["legado"]}
DESCUENTO_ALTO = {k: v["descuento_alto"] for k, v in SISTEMAS.items()}

# 3. CÁLCULO (predicados puros) ----------------------------------------


def _clave(sistema_apertura):
    return str(sistema_apertura).strip().lower()


def normalizar_apertura(tipo_apertura):
    """Normaliza un nombre de apertura (legado o canónico) a la clave del contrato."""
    tipo = _clave(tipo_apertura)
    return LEGADO_A_CONTRATO.get(tipo, tipo)


def necesita_descuento_gola(sistema_apertura):
    """True si el sistema requiere descuento de altura (gola)."""
    return _clave(sistema_apertura) == APERTURA_GOLA


def necesita_bisel_45(sistema_apertura):
    """True si el sistema requiere bisel a 45° en la arista de agarre."""
    return _clave(sistema_apertura) == APERTURA_45_GRADOS


def necesita_cantos_45(sistema_apertura):
    """Alias de `necesita_bisel_45` para el vocabulario de puertas."""
    return necesita_bisel_45(sistema_apertura)


def necesita_expulsor_magnetico(sistema_apertura):
    """True si el sistema inyecta expulsor magnético al BOM (push_open)."""
    return _clave(sistema_apertura) == APERTURA_PUSH_OPEN
