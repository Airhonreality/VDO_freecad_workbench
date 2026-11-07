# =====================================================================
# tema.py
# Tokens de tema visual VDO: fuente única de color para la UI.
# D-10: acento unificado en #007acc (antes #0098ff en muchos sitios).
# D-24: definición única de get_svg_icon.
# =====================================================================

from freecad.vdo.qt_compat import QtCore, QtGui, QtSvg

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

_ICON_CACHE = {}


def obtener_svg_icon(name, size=22):
    """Icono Lucide de la paleta VDO, con caché compartida por nombre y tamaño."""
    return get_svg_icon(name, size, icons_map=LUCIDE_ICONS, cache=_ICON_CACHE)

__all__ = [
    "LUCIDE_ICONS",
    "get_svg_icon",
    "obtener_svg_icon",
]
