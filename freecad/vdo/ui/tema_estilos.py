"""Hojas de estilo Qt de la UI VDO y helpers que las aplican (MN-07, D-76)."""

from freecad.vdo.ui.tema_colores import (
    ACEINTO,
    BORDE,
    BORDE_ACTIVO,
    FONDO2,
    FONDO3,
    TEXTO,
    TEXTO_CLARO,
)

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

__all__ = [
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
    "aplicar_estilo",
    "estilo_boton",
    "estilo_breadcrumb",
]
