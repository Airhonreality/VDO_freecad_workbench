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


# --- Estilos de la UI (MN-07, D-76): literales de ui/ movidos aquí ---
ESTILO_ACENTO_NEGRITA = "font-weight: bold; color: #007acc;"
ESTILO_ARBOL_MAESTRO = """
            QTreeWidget {
                background-color: #1a1a1a;
                border: 1px solid #2d2d2d;
                color: #dcdcdc;
                font-size: 10px;
            }
            QTreeWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
                font-weight: bold;
            }
            QTreeWidget::item:hover:!selected {
                background-color: #262626;
            }
        """
ESTILO_ARQUITECTURA_9PX = "font-size: 9px; color: #888888;"
ESTILO_ATENUADO_10PX = "color: #888888; font-size: 10px;"
ESTILO_ATENUADO_9PX = "color: #888888; font-size: 9px;"
ESTILO_ATENUADO_ITALICA = "color: #8a8a8a; font-style: italic;"
ESTILO_AVISO_10PX = "color: #ffaa00; font-size: 10px;"
ESTILO_BANNER_LUZ = "QFrame { background-color: #22252a; border: 1px solid #007acc; border-radius: 4px; padding: 3px; }"
ESTILO_BOTON_ACENTO_10PX = "background-color: #007acc; color: white; font-weight: bold; padding: 4px; font-size: 10px;"
ESTILO_BOTON_AZUL = "background-color: #0066cc; color: white; font-weight: bold;"
ESTILO_BOTON_AZUL_PAD = "background:#0066cc; color:white; font-weight:bold; padding:6px;"
ESTILO_BOTON_EXITO = "background-color: #00cc00; color: white; font-weight: bold;"
ESTILO_BOTON_VACIO = "background-color: #333333; color: #cccccc; padding: 4px; font-size: 10px;"
ESTILO_BOTON_VANO = """
                QPushButton {
                    background-color: #282828;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    font-size: 9px;
                    color: #cccccc;
                    padding: 2px 4px;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    border-color: #007acc;
                    color: #ffffff;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: #333333;
                    color: #ffffff;
                }
            """
ESTILO_BREADCRUMB_RAIZ = "QLabel#lblBreadcrumbRoot { color: #007acc; font-weight: bold; font-size: 11px; }"
ESTILO_CLAVE_10PX = "color: #aaaaaa; font-size: 10px;"
ESTILO_CLAVE_11PX = "color: #b0b0b0; font-size: 11px;"
ESTILO_ERROR_TEXTO = "QLabel { color: #b03a2e; }"
ESTILO_ETIQUETA_10PX = "font-size: 10px; color: #aaaaaa;"
ESTILO_ETIQUETA_OSCURA = "QLabel { background: #2b2b2b; color: #e0e0e0; padding: 4px; border: 1px solid #4a4a4a; }"
ESTILO_ETIQUETA_OSCURA_5PX = "QLabel { background: #2b2b2b; color: #e0e0e0; padding: 5px; border: 1px solid #4a4a4a; }"
ESTILO_ETIQUETA_OSCURA_COMPACTA = "QLabel { background: #2b2b2b; color: #e0e0e0; padding: 3px; border: 1px solid #4a4a4a; }"
ESTILO_FONDO_CLARO = "background:#fafafa;"
ESTILO_FONDO_DOCK = "background-color: #1a1a1a; border-radius: 4px;"
ESTILO_FONDO_TRANSPARENTE = "background: transparent;"
ESTILO_GRIS_11PX = "color:#777; font-size:11px;"
ESTILO_GRUPO_CABECERA = "QGroupBox { font-weight: bold; color: #e0e0e0; border: 1px solid #555555; border-radius: 6px; margin-top: 10px; padding-top: 8px; }QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }"
ESTILO_GRUPO_HERRAJE = "QGroupBox { color: #28a745; font-weight: bold; border: 1px solid #334d38; border-radius: 4px; margin-top: 6px; padding-top: 10px; }"
ESTILO_GRUPO_PANEL_HEADER = "QGroupBox#grpPanelHeader { color: #e0e0e0; font-weight: bold; border: 1px solid #444444; border-radius: 4px; margin-top: 6px; }QGroupBox#grpPanelHeader::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #007acc; }"
ESTILO_HUB_9PX = "color: #28a745; font-size: 9px;"
ESTILO_INFO_11PX = "color: #666; font-size: 11px;"
ESTILO_LUZ_10PX = "color: #00d4ff; font-size: 10px;"
ESTILO_MICRO_HEADER = """
            QFrame#VDOMicroHeader {
                background-color: #1e1e1e;
                border-top: 1px solid #2d2d2d;
                border-bottom: 1px solid #2d2d2d;
                padding: 1px 4px;
            }
            QLabel {
                color: #888888;
                font-size: 10px;
                font-weight: bold;
            }
            QDoubleSpinBox {
                background-color: #282828;
                color: #00d4ff;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 1px 2px;
                font-size: 10px;
                font-weight: bold;
            }
            QDoubleSpinBox:focus {
                border-color: #007acc;
                background-color: #333333;
            }
        """
ESTILO_NEGRITA = "font-weight: bold;"
ESTILO_NEGRITA_11PX = "font-weight: bold; font-size: 11px;"
ESTILO_NEGRITA_TEXTO = "font-weight: bold; color: #e0e0e0;"
ESTILO_PAGINA_TITULO = "QLabel#lblPaginaTitulo { color: #007acc; font-size: 11px; font-weight: bold; padding-bottom: 2px; }"
ESTILO_RESUMEN_AZUL = "color: #0066cc; font-weight: bold;"
ESTILO_RESUMEN_CAJA = "QLabel { background: #252525; color: #d0d0d0; padding: 4px 6px; border: 1px solid #3a3a3a; border-radius: 4px; font-size: 11px; }"
ESTILO_RESUMEN_CLARO = "QLabel { background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; font-family: monospace; }"
ESTILO_RESUMEN_MONO = "QLabel { background: #2b2b2b; color: #e0e0e0; padding: 6px; border: 1px solid #4a4a4a; font-family: monospace; }"
ESTILO_SCROLL_TRANSPARENTE = "QScrollArea { background-color: transparent; }"
ESTILO_SEPARADOR = "color: #666666; font-size: 10px;"
ESTILO_SPLITTER = """
            QSplitter::handle {
                background-color: #2b2b2b;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
        """
ESTILO_TEXTO_10PX = "font-size: 10px;"
ESTILO_TEXTO_11PX = "font-size: 11px;"
ESTILO_TEXTO_12PX = "font-size:12px;"
ESTILO_TITULO_14PX = "font-size: 14px; font-weight: bold;"
ESTILO_TITULO_14PX_OSCURO = "font-size: 14px; color: #333;"
ESTILO_TITULO_ACENTO_12PX = "font-weight: bold; color: #007acc; font-size: 12px;"
ESTILO_TITULO_DOCK = "color: #888888; font-size: 9px; font-weight: bold; margin-top: 4px;"
ESTILO_TITULO_ESPACIADO = "font-size: 11px; color: #e0e0e0; letter-spacing: 0.5px;"
ESTILO_VALOR_10PX_NEGRITA = "color: #e0e0e0; font-size: 10px; font-weight: bold;"
ESTILO_VALOR_11PX = "color: #e0e0e0; font-size: 11px;"
ESTILO_VALOR_11PX_NEGRITA = "color: #e0e0e0; font-size: 11px; font-weight: bold;"
ESTILO_VALOR_BLANCO_10PX = "color: #ffffff; font-size: 10px; font-weight: bold;"
ESTILO_CAJON = 'QWidget { background-color: #2b2b2b; color: #e0e0e0; }QGroupBox { font-weight: bold; color: #e0e0e0; border: 1px solid #555555; border-radius: 6px; margin-top: 10px; padding-top: 8px; }QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }QLabel { color: #e0e0e0; }QComboBox, QDoubleSpinBox, QSpinBox {  background-color: #3a3a3a; color: #e0e0e0;  border: 1px solid #555555; border-radius: 3px; padding: 3px;}QPushButton {  background-color: #3a3a3a; color: #e0e0e0;  border: 1px solid #555555; border-radius: 4px;  padding: 6px 14px; font-weight: bold;}QPushButton:hover { background-color: #444444; }'
ESTILO_PUERTA_GRUPO_CABECERA = "QGroupBox { background: #1e1e1e; color: #e0e0e0; border: 1px solid #4a4a4a; border-radius: 4px; margin-top: 8px; padding-top: 4px; }QGroupBox::title { subcontrol-origin: margin; left: 8px; }"
ESTILO_PUERTA_GRUPO = "QGroupBox { color: #e0e0e0; border: 1px solid #4a4a4a; border-radius: 4px; margin-top: 8px; }QGroupBox::title { subcontrol-origin: margin; left: 8px; }"
ESTILO_PUERTA_FONDO = "QWidget { background: #1e1e1e; color: #e0e0e0; }"
ESTILO_PUERTA_TEXTO = "color: #e0e0e0;"
ESTILO_PUERTA_PISTON = "QLabel { background: #1e4a1e; color: #8fbc8f; padding: 6px; border: 1px solid #3a7a3a; font-weight: bold; }"


def aplicar_estilo(widget, hoja):
    """Único punto de la UI que aplica una hoja de estilo (widget.setStyleSheet)."""
    widget.setStyleSheet(hoja)


def estilo_breadcrumb(clave, activo_es):
    """Hoja de la miga de pan del inspector: activa en blanco y negrita."""
    return (f"QLabel#lblBreadcrumb_{clave} {{ "
            f"color: {'#ffffff' if activo_es else '#aaaaaa'}; "
            f"font-weight: {'bold' if activo_es else 'normal'}; "
            f"font-size: 10px; }}")


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
    "ACEINTO",
    "ACEINTO_HOVER",
    "AVISO",
    "BORDE",
    "BORDE_ACTIVO",
    "BORDE_CLARO",
    "BORDE_SUAVE",
    "ERROR",
    "ESTILO_ACENTO_NEGRITA",
    "ESTILO_ARBOL_MAESTRO",
    "ESTILO_ARQUITECTURA_9PX",
    "ESTILO_ATENUADO_9PX",
    "ESTILO_ATENUADO_10PX",
    "ESTILO_ATENUADO_ITALICA",
    "ESTILO_AVISO_10PX",
    "ESTILO_BANNER_LUZ",
    "ESTILO_BOTON_ACENTO_10PX",
    "ESTILO_BOTON_AZUL",
    "ESTILO_BOTON_AZUL_PAD",
    "ESTILO_BOTON_EXITO",
    "ESTILO_BOTON_PRIMARIO",
    "ESTILO_BOTON_SECUNDARIO",
    "ESTILO_BOTON_VACIO",
    "ESTILO_BOTON_VANO",
    "ESTILO_BREADCRUMB_RAIZ",
    "ESTILO_CAJON",
    "ESTILO_CLAVE_10PX",
    "ESTILO_CLAVE_11PX",
    "ESTILO_ERROR_TEXTO",
    "ESTILO_ETIQUETA_10PX",
    "ESTILO_ETIQUETA_OSCURA",
    "ESTILO_ETIQUETA_OSCURA_5PX",
    "ESTILO_ETIQUETA_OSCURA_COMPACTA",
    "ESTILO_FONDO_CLARO",
    "ESTILO_FONDO_DOCK",
    "ESTILO_FONDO_TRANSPARENTE",
    "ESTILO_GRIS_11PX",
    "ESTILO_GROUPBOX",
    "ESTILO_GRUPO_CABECERA",
    "ESTILO_GRUPO_HERRAJE",
    "ESTILO_GRUPO_PANEL_HEADER",
    "ESTILO_HUB_9PX",
    "ESTILO_INFO_11PX",
    "ESTILO_INPUT",
    "ESTILO_LUZ_10PX",
    "ESTILO_MICRO_HEADER",
    "ESTILO_NEGRITA",
    "ESTILO_NEGRITA_11PX",
    "ESTILO_NEGRITA_TEXTO",
    "ESTILO_PAGINA_TITULO",
    "ESTILO_PUERTA_FONDO",
    "ESTILO_PUERTA_GRUPO",
    "ESTILO_PUERTA_GRUPO_CABECERA",
    "ESTILO_PUERTA_PISTON",
    "ESTILO_PUERTA_TEXTO",
    "ESTILO_RESUMEN_AZUL",
    "ESTILO_RESUMEN_CAJA",
    "ESTILO_RESUMEN_CLARO",
    "ESTILO_RESUMEN_MONO",
    "ESTILO_SCROLL_TRANSPARENTE",
    "ESTILO_SEPARADOR",
    "ESTILO_SPLITTER",
    "ESTILO_TEXTO_10PX",
    "ESTILO_TEXTO_11PX",
    "ESTILO_TEXTO_12PX",
    "ESTILO_TITULO_14PX",
    "ESTILO_TITULO_14PX_OSCURO",
    "ESTILO_TITULO_ACENTO_12PX",
    "ESTILO_TITULO_DOCK",
    "ESTILO_TITULO_ESPACIADO",
    "ESTILO_VALOR_10PX_NEGRITA",
    "ESTILO_VALOR_11PX",
    "ESTILO_VALOR_11PX_NEGRITA",
    "ESTILO_VALOR_BLANCO_10PX",
    "EXITO",
    "FONDO",
    "FONDO2",
    "FONDO3",
    "LUCIDE_ICONS",
    "TEXTO",
    "TEXTO_CLARO",
    "TEXTO_SUAVE",
    "TEXTO_SUAVE2",
    "aplicar_estilo",
    "estilo_boton",
    "estilo_breadcrumb",
    "get_svg_icon",
    "obtener_svg_icon",
]

# --- Colores fuera de tema (F8, D-94): literales movidas desde ui/* ---
COLOR_ACENTO_PRESIONADO = "#005a9e"
COLOR_ACENTO_CIAN = "#00b4d8"
COLOR_FONDO_PROFUNDO = "#141414"
COLOR_FONDO_CANVAS = "#161616"
COLOR_ACENTO_FONDO = "#192a3a"
COLOR_FONDO_CAJA = "#1b1b1b"
COLOR_FONDO_ENTRADA = "#202020"
COLOR_FONDO_BASE = "#252525"
COLOR_FONDO_BOTON = "#2b2b2b"
COLOR_FONDO_INACTIVO = "#2c2c2c"
COLOR_FONDO_ELEVADO = "#303030"
COLOR_FONDO_SECUNDARIO = "#383838"
COLOR_TEXTO_AZUL_CLARO = "#4da3ff"
COLOR_BORDE_MEDIO = "#555555"
COLOR_TEXTO_ATENUADO = "#aaaaaa"
COLOR_TEXTO_SECUNDARIO = "#d0d0d0"
COLOR_NARANJA = "#e67e22"
COLOR_CIAN_VIVO = "#00d4ff"
COLOR_FONDO_ESTRUCTURA = "#181818"
COLOR_FONDO_CHASIS_OSCURO = "#1a1a1a"
COLOR_FONDO_AUSENTE = "#1c1c1c"
COLOR_FONDO_CAVIDAD = "#1f1f1f"
COLOR_FONDO_CAVIDAD_BRILLO = "#24272b"
COLOR_FONDO_CHASIS = "#25282c"
COLOR_FONDO_MEDIO = "#282828"
COLOR_VERDE_HERRAJE = "#28a745"
COLOR_FONDO_RANURA = "#2a2a2a"
COLOR_BORDE_OSCURO = "#2d2d2d"
COLOR_FONDO_ACTIVO = "#2f353d"
COLOR_BORDE_MEDIO_OSCURO = "#3d3d3d"
COLOR_TEXTO_MUTED = "#777777"
COLOR_CATEGORIA_VERTICAL = "#00b894"
COLOR_TRAZO_NEGRO = "#111111"
COLOR_FONDO_HUB = "#222222"
COLOR_CATEGORIA_MARCO = "#7f8c8d"
COLOR_TRAZO_NEUTRO = "#8a8a8a"
COLOR_CATEGORIA_INGLETE = "#9b59b6"
COLOR_TRAZO_CLARO = "#bdc3c7"
