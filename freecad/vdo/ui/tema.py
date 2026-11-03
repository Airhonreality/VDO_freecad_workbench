# =====================================================================
# tema.py
# Tokens de tema visual VDO: fuente única de color para la UI.
# D-10: acento unificado en #007acc (antes #0098ff en muchos sitios).
# D-24: definición única de get_svg_icon.
# =====================================================================

from freecad.vdo.qt_compat import QtCore, QtGui, QtSvg

# --- Fondos ---
FONDO = "#1e1e1e"       # fondo principal de paneles y diálogos
FONDO2 = "#262626"      # fondo secundario (grupos, secciones, barras)
FONDO3 = "#333333"      # fondo terciario (entradas activas, resaltado leve)

# --- Texto ---
TEXTO = "#e0e0e0"       # texto primario
TEXTO_SUAVE = "#888888" # texto secundario / atenuado
TEXTO_CLARO = "#ffffff" # texto sobre fondos oscuros / acento
TEXTO_SUAVE2 = "#cccccc"# texto terciario

# --- Bordes y divisores ---
BORDE = "#444444"       # borde principal
BORDE_SUAVE = "#3a3a3a" # borde sutil
BORDE_ACTIVO = "#007acc"# borde con foco / acento
BORDE_CLARO = "#666666" # borde claro

# --- Acento de marca (D-10: único cambio visual autorizado) ---
ACEINTO = "#007acc"     # acento principal (unifica #0098ff)
ACEINTO_HOVER = "#0d4a75"

# --- Estados ---
ERROR = "#b03a2e"       # error / advertencia grave
EXITO = "#00cc00"       # éxito
AVISO = "#ffaa00"       # aviso / atención

# --- Estilos de botón / control (ensamblados a partir de tokens) ---
ESTILO_BOTON_PRIMARIO = (
    f"background-color: {ACEINTO}; color: {TEXTO_CLARO}; "
    f"border: 1px solid {BORDE_ACTIVO};"
)
ESTILO_BOTON_SECUNDARIO = (
    f"background-color: {FONDO3}; color: {TEXTO}; "
    f"border: 1px solid {BORDE};"
)
ESTILO_INPUT = (
    f"background-color: {FONDO3}; color: {TEXTO}; "
    f"border: 1px solid {BORDE};"
)
ESTILO_GROUPBOX = (
    f"QGroupBox {{ background-color: {FONDO2}; color: {TEXTO}; "
    f"border: 1px solid {BORDE}; }}"
)

def estilo_boton(acento=ACEINTO, texto=TEXTO_CLARO, borde=BORDE_ACTIVO):
    """Devuelve una hoja de estilo para botón con los tokens dados."""
    return (f"background-color: {acento}; color: {texto}; "
            f"border: 1px solid {borde};")


# --- Iconos Lucide (tabla única; M2 H-23) ---
LUCIDE_ICONS = {
    "tapa_domina": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2">
        <rect x="2" y="3" width="20" height="5" fill="#007acc" stroke="#007acc" rx="1"/>
        <rect x="2" y="8" width="6" height="13" fill="#333333" stroke="#666666" rx="1"/>
    </svg>""",
    "lateral_domina": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2">
        <rect x="2" y="3" width="6" height="18" fill="#007acc" stroke="#007acc" rx="1"/>
        <rect x="8" y="3" width="14" height="6" fill="#333333" stroke="#666666" rx="1"/>
    </svg>""",
    "inglete_45": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 20 L20 4" stroke-width="2.5"/>
        <path d="M4 4 L4 20 L12 20 L12 12 L20 12 L20 4 Z" fill="#252525" stroke="#555555" stroke-width="1"/>
        <circle cx="4" cy="20" r="1.5" fill="#00d4ff"/>
        <circle cx="20" cy="4" r="1.5" fill="#00d4ff"/>
    </svg>""",
    "zocalo": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="4" width="20" height="10" rx="1" fill="#2b2b2b" stroke="#555555"/>
        <rect x="5" y="14" width="14" height="6" fill="#007acc" stroke="#007acc"/>
        <line x1="2" y1="20" x2="22" y2="20" stroke="#888888" stroke-dasharray="2 2"/>
    </svg>""",
    "suspendido": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="5" y="3" width="16" height="14" rx="1" fill="#2b2b2b" stroke="#555555"/>
        <line x1="2" y1="3" x2="2" y2="21" stroke="#ffaa00" stroke-width="3"/>
        <path d="M2 6 h3 v4 h-3" fill="#ffaa00"/>
        <line x1="2" y1="21" x2="22" y2="21" stroke="#555555" stroke-dasharray="2 2"/>
    </svg>""",
    "patas": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="3" width="20" height="11" rx="1" fill="#2b2b2b" stroke="#555555"/>
        <rect x="5" y="14" width="3" height="6" fill="#007acc"/>
        <ellipse cx="6.5" cy="20" rx="3" ry="1" fill="#007acc"/>
        <rect x="16" y="14" width="3" height="6" fill="#007acc"/>
        <ellipse cx="17.5" cy="20" rx="3" ry="1" fill="#007acc"/>
        <line x1="2" y1="21" x2="22" y2="21" stroke="#888888" stroke-dasharray="2 2"/>
    </svg>""",
    "ranura": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" stroke="#555555" stroke-dasharray="2 2"/>
        <line x1="7" y1="3" x2="7" y2="21" stroke="#00d4ff" stroke-width="3"/>
    </svg>""",
    "galce": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" stroke="#555555"/>
        <path d="M3 6 h4 v15" stroke="#ffaa00" stroke-width="2.5"/>
    </svg>""",
    "atornillado": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="2" fill="#252525" stroke="#777777"/>
        <circle cx="6" cy="6" r="1.5" fill="#28a745"/>
        <circle cx="18" cy="6" r="1.5" fill="#28a745"/>
        <circle cx="6" cy="18" r="1.5" fill="#28a745"/>
        <circle cx="18" cy="18" r="1.5" fill="#28a745"/>
    </svg>""",
    "abierto": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="2" stroke-linecap="round">
        <rect x="3" y="3" width="18" height="18" rx="2" stroke="#555555" stroke-dasharray="3 3"/>
        <line x1="4" y1="4" x2="20" y2="20" stroke="#e74c3c" stroke-width="2"/>
    </svg>""",
    "coco": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="1"/></svg>""",
    "escritorio": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><line x1="2" y1="5" x2="22" y2="5" stroke-width="3"/><line x1="4" y1="5" x2="4" y2="20" stroke-width="2"/><line x1="20" y1="5" x2="20" y2="20" stroke-width="2"/></svg>""",
    "estanteria": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><line x1="4" y1="2" x2="4" y2="22" stroke-width="2"/><line x1="20" y1="2" x2="20" y2="22" stroke-width="2"/><line x1="4" y1="8" x2="20" y2="8"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="4" y1="21" x2="20" y2="21" stroke-width="2.5"/></svg>""",
    "aereo": """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><rect x="4" y="3" width="16" height="14" rx="1"/><line x1="2" y1="2" x2="2" y2="20" stroke="#ffaa00" stroke-width="2"/></svg>""",
    "link": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>""",
    "unlink": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18.84 12.25 1.72-1.71a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="m5.16 11.75-1.72 1.71a5 5 0 0 0 7.07 7.07l1.71-1.71"/><line x1="2" y1="2" x2="22" y2="22"/></svg>""",
    "vertical_domina": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><rect x="4" y="3" width="5" height="18" fill="#555555" stroke="#777777"/><rect x="9" y="8" width="11" height="8" fill="#222222" stroke="#555555"/></svg>""",
    "horizontal_domina": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><rect x="3" y="4" width="18" height="5" fill="#555555" stroke="#777777"/><rect x="8" y="9" width="8" height="11" fill="#222222" stroke="#555555"/></svg>""",
    "marco_interior": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e0e0e0" stroke-width="2"><rect x="6" y="6" width="12" height="12" stroke-dasharray="2 2" stroke="#888888"/><path d="M6 10 h6 v6"/></svg>""",
}


def get_svg_icon(name: str, size: int = 22,
                 icons_map: dict | None = None, cache: dict | None = None) -> QtGui.QIcon:
    """Renderiza un string SVG (Lucide) directamente a un QIcon.

    Se pasa `icons_map` y `cache` desde el módulo llamador para que cada
    UI conserve su propio conjunto de iconos y su caché, con una única
    implementación de renderizado (D-24).
    """
    if cache is None:
        cache = {}
    key = (name, size)
    if key in cache:
        return cache[key]
    svg_str = (icons_map or {}).get(name, "")
    if not svg_str:
        return QtGui.QIcon()
    svg_bytes = QtCore.QByteArray(svg_str.encode("utf-8"))
    renderer = QtSvg.QSvgRenderer(svg_bytes)
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    icon = QtGui.QIcon(pixmap)
    cache[key] = icon
    return icon
__all__ = [
    "ACEINTO",
    "ACEINTO_HOVER",
    "AVISO",
    "BORDE",
    "BORDE_ACTIVO",
    "BORDE_CLARO",
    "BORDE_SUAVE",
    "ERROR",
    "ESTILO_BOTON_PRIMARIO",
    "ESTILO_BOTON_SECUNDARIO",
    "ESTILO_GROUPBOX",
    "ESTILO_INPUT",
    "EXITO",
    "FONDO",
    "FONDO2",
    "FONDO3",
    "LUCIDE_ICONS",
    "TEXTO",
    "TEXTO_CLARO",
    "TEXTO_SUAVE",
    "TEXTO_SUAVE2",
    "estilo_boton",
    "get_svg_icon",
]
