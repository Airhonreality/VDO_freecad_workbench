"""Hojas de estilo Qt de la UI VDO y helpers que las aplican (MN-07, D-76)."""

from freecad.vdo.ui.tema_colores import (
    ACEINTO,
    AVISO,
    BORDE,
    BORDE_ACTIVO,
    BORDE_CLARO,
    BORDE_SUAVE,
    COLOR_AZUL_ACCION,
    COLOR_BANNER_FONDO,
    COLOR_BORDE_GRIS,
    COLOR_BORDE_HERRAJE,
    COLOR_BORDE_MEDIO,
    COLOR_BORDE_MEDIO_OSCURO,
    COLOR_BORDE_OSCURO,
    COLOR_BORDE_PAPEL,
    COLOR_BORDE_PISTON,
    COLOR_CIAN_VIVO,
    COLOR_FONDO_BASE,
    COLOR_FONDO_BOTON,
    COLOR_FONDO_CHASIS_OSCURO,
    COLOR_FONDO_CLARO,
    COLOR_FONDO_MEDIO,
    COLOR_FONDO_PISTON,
    COLOR_FONDO_RESUMEN_PAPEL,
    COLOR_OPT_EJE,
    COLOR_OPT_REGLA,
    COLOR_OPT_TRAZO,
    COLOR_TEXTO_ARBOL,
    COLOR_TEXTO_ATENUADO,
    COLOR_TEXTO_MEDIO,
    COLOR_TEXTO_SECUNDARIO,
    COLOR_TRAZO_NEUTRO,
    COLOR_VERDE_HERRAJE,
    COLOR_VERDE_PISTON_TEXTO,
    ERROR,
    EXITO,
    FONDO,
    FONDO2,
    FONDO3,
    TEXTO,
    TEXTO_CLARO,
    TEXTO_SUAVE,
    TEXTO_SUAVE2,
)
from freecad.vdo.ui.tema_tipografia import (
    ESPACIO_1,
    ESPACIO_2,
    ESPACIO_3,
    ESPACIO_4,
    ESPACIO_5,
    ESPACIO_6,
    ESPACIO_8,
    ESPACIO_10,
    ESPACIO_14,
    ESPACIO_LETRA,
    RADIO_3,
    RADIO_4,
    RADIO_6,
    TAMANO_BASE,
    TAMANO_GRANDE,
    TAMANO_MEDIO,
    TAMANO_PEQUENO,
    TAMANO_TITULO,
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
ESTILO_ACENTO_NEGRITA = f"font-weight: bold; color: {ACEINTO};"
ESTILO_ARBOL_MAESTRO = f"""
            QTreeWidget {{
                background-color: {COLOR_FONDO_CHASIS_OSCURO};
                border: 1px solid {COLOR_BORDE_OSCURO};
                color: {COLOR_TEXTO_ARBOL};
                font-size: {TAMANO_BASE}px;
            }}
            QTreeWidget::item:selected {{
                background-color: {ACEINTO};
                color: {TEXTO_CLARO};
                font-weight: bold;
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {FONDO2};
            }}
        """
ESTILO_ARQUITECTURA_9PX = f"font-size: {TAMANO_PEQUENO}px; color: {TEXTO_SUAVE};"
ESTILO_ATENUADO_10PX = f"color: {TEXTO_SUAVE}; font-size: {TAMANO_BASE}px;"
ESTILO_ATENUADO_9PX = f"color: {TEXTO_SUAVE}; font-size: {TAMANO_PEQUENO}px;"
ESTILO_ATENUADO_ITALICA = f"color: {COLOR_TRAZO_NEUTRO}; font-style: italic;"
ESTILO_AVISO_10PX = f"color: {AVISO}; font-size: {TAMANO_BASE}px;"
ESTILO_BANNER_LUZ = f"QFrame {{ background-color: {COLOR_BANNER_FONDO}; border: 1px solid {ACEINTO}; border-radius: {RADIO_4}px; padding: {ESPACIO_3}px; }}"
ESTILO_BOTON_ACENTO_10PX = f"background-color: {ACEINTO}; color: white; font-weight: bold; padding: {ESPACIO_4}px; font-size: {TAMANO_BASE}px;"
ESTILO_BOTON_AZUL = f"background-color: {COLOR_AZUL_ACCION}; color: white; font-weight: bold;"
ESTILO_BOTON_AZUL_PAD = f"background:{COLOR_AZUL_ACCION}; color:white; font-weight:bold; padding:{ESPACIO_6}px;"
ESTILO_BOTON_EXITO = f"background-color: {EXITO}; color: white; font-weight: bold;"
ESTILO_BOTON_VACIO = f"background-color: {FONDO3}; color: {TEXTO_SUAVE2}; padding: {ESPACIO_4}px; font-size: {TAMANO_BASE}px;"
ESTILO_BOTON_VANO = f"""
                QPushButton {{
                    background-color: {COLOR_FONDO_MEDIO};
                    border: 1px solid {COLOR_BORDE_MEDIO_OSCURO};
                    border-radius: {RADIO_4}px;
                    font-size: {TAMANO_PEQUENO}px;
                    color: {TEXTO_SUAVE2};
                    padding: {ESPACIO_2}px {ESPACIO_4}px;
                }}
                QPushButton:checked {{
                    background-color: {ACEINTO};
                    border-color: {ACEINTO};
                    color: {TEXTO_CLARO};
                    font-weight: bold;
                }}
                QPushButton:hover:!checked {{
                    background-color: {FONDO3};
                    color: {TEXTO_CLARO};
                }}
            """
ESTILO_BREADCRUMB_RAIZ = f"QLabel#lblBreadcrumbRoot {{ color: {ACEINTO}; font-weight: bold; font-size: {TAMANO_MEDIO}px; }}"
ESTILO_CLAVE_10PX = f"color: {COLOR_TEXTO_ATENUADO}; font-size: {TAMANO_BASE}px;"
ESTILO_CLAVE_11PX = f"color: {COLOR_TEXTO_MEDIO}; font-size: {TAMANO_MEDIO}px;"
ESTILO_ERROR_TEXTO = f"QLabel {{ color: {ERROR}; }}"
ESTILO_ETIQUETA_10PX = f"font-size: {TAMANO_BASE}px; color: {COLOR_TEXTO_ATENUADO};"
ESTILO_ETIQUETA_OSCURA = f"QLabel {{ background: {COLOR_FONDO_BOTON}; color: {TEXTO}; padding: {ESPACIO_4}px; border: 1px solid {COLOR_BORDE_GRIS}; }}"
ESTILO_ETIQUETA_OSCURA_5PX = f"QLabel {{ background: {COLOR_FONDO_BOTON}; color: {TEXTO}; padding: {ESPACIO_5}px; border: 1px solid {COLOR_BORDE_GRIS}; }}"
ESTILO_ETIQUETA_OSCURA_COMPACTA = f"QLabel {{ background: {COLOR_FONDO_BOTON}; color: {TEXTO}; padding: {ESPACIO_3}px; border: 1px solid {COLOR_BORDE_GRIS}; }}"
ESTILO_FONDO_CLARO = f"background:{COLOR_FONDO_CLARO};"
ESTILO_FONDO_DOCK = f"background-color: {COLOR_FONDO_CHASIS_OSCURO}; border-radius: {RADIO_4}px;"
ESTILO_FONDO_TRANSPARENTE = "background: transparent;"
ESTILO_GRIS_11PX = f"color:{COLOR_OPT_REGLA}; font-size:{TAMANO_MEDIO}px;"
ESTILO_GRUPO_CABECERA = f"QGroupBox {{ font-weight: bold; color: {TEXTO}; border: 1px solid {COLOR_BORDE_MEDIO}; border-radius: {RADIO_6}px; margin-top: {ESPACIO_10}px; padding-top: {ESPACIO_8}px; }}QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 {ESPACIO_4}px; }}"
ESTILO_GRUPO_HERRAJE = f"QGroupBox {{ color: {COLOR_VERDE_HERRAJE}; font-weight: bold; border: 1px solid {COLOR_BORDE_HERRAJE}; border-radius: {RADIO_4}px; margin-top: {ESPACIO_6}px; padding-top: {ESPACIO_10}px; }}"
ESTILO_GRUPO_PANEL_HEADER = f"QGroupBox#grpPanelHeader {{ color: {TEXTO}; font-weight: bold; border: 1px solid {BORDE}; border-radius: {RADIO_4}px; margin-top: {ESPACIO_6}px; }}QGroupBox#grpPanelHeader::title {{ subcontrol-origin: margin; left: 8px; padding: 0 {ESPACIO_4}px; color: {ACEINTO}; }}"
ESTILO_HUB_9PX = f"color: {COLOR_VERDE_HERRAJE}; font-size: {TAMANO_PEQUENO}px;"
ESTILO_INFO_11PX = f"color: {COLOR_OPT_EJE}; font-size: {TAMANO_MEDIO}px;"
ESTILO_LUZ_10PX = f"color: {COLOR_CIAN_VIVO}; font-size: {TAMANO_BASE}px;"
ESTILO_MICRO_HEADER = f"""
            QFrame#VDOMicroHeader {{
                background-color: {FONDO};
                border-top: 1px solid {COLOR_BORDE_OSCURO};
                border-bottom: 1px solid {COLOR_BORDE_OSCURO};
                padding: {ESPACIO_1}px {ESPACIO_4}px;
            }}
            QLabel {{
                color: {TEXTO_SUAVE};
                font-size: {TAMANO_BASE}px;
                font-weight: bold;
            }}
            QDoubleSpinBox {{
                background-color: {COLOR_FONDO_MEDIO};
                color: {COLOR_CIAN_VIVO};
                border: 1px solid {COLOR_BORDE_MEDIO_OSCURO};
                border-radius: {RADIO_3}px;
                padding: {ESPACIO_1}px {ESPACIO_2}px;
                font-size: {TAMANO_BASE}px;
                font-weight: bold;
            }}
            QDoubleSpinBox:focus {{
                border-color: {ACEINTO};
                background-color: {FONDO3};
            }}
        """
ESTILO_NEGRITA = "font-weight: bold;"
ESTILO_NEGRITA_11PX = f"font-weight: bold; font-size: {TAMANO_MEDIO}px;"
ESTILO_NEGRITA_TEXTO = f"font-weight: bold; color: {TEXTO};"
ESTILO_PAGINA_TITULO = f"QLabel#lblPaginaTitulo {{ color: {ACEINTO}; font-size: {TAMANO_MEDIO}px; font-weight: bold; padding-bottom: {ESPACIO_2}px; }}"
ESTILO_RESUMEN_AZUL = f"color: {COLOR_AZUL_ACCION}; font-weight: bold;"
ESTILO_RESUMEN_CAJA = f"QLabel {{ background: {COLOR_FONDO_BASE}; color: {COLOR_TEXTO_SECUNDARIO}; padding: {ESPACIO_4}px {ESPACIO_6}px; border: 1px solid {BORDE_SUAVE}; border-radius: {RADIO_4}px; font-size: {TAMANO_MEDIO}px; }}"
ESTILO_RESUMEN_CLARO = f"QLabel {{ background-color: {COLOR_FONDO_RESUMEN_PAPEL}; padding: {ESPACIO_8}px; border: 1px solid {COLOR_BORDE_PAPEL}; font-family: monospace; }}"
ESTILO_RESUMEN_MONO = f"QLabel {{ background: {COLOR_FONDO_BOTON}; color: {TEXTO}; padding: {ESPACIO_6}px; border: 1px solid {COLOR_BORDE_GRIS}; font-family: monospace; }}"
ESTILO_SCROLL_TRANSPARENTE = "QScrollArea { background-color: transparent; }"
ESTILO_SEPARADOR = f"color: {BORDE_CLARO}; font-size: {TAMANO_BASE}px;"
ESTILO_SPLITTER = f"""
            QSplitter::handle {{
                background-color: {COLOR_FONDO_BOTON};
                width: 3px;
            }}
            QSplitter::handle:hover {{
                background-color: {ACEINTO};
            }}
        """
ESTILO_TEXTO_10PX = f"font-size: {TAMANO_BASE}px;"
ESTILO_TEXTO_11PX = f"font-size: {TAMANO_MEDIO}px;"
ESTILO_TEXTO_12PX = f"font-size:{TAMANO_GRANDE}px;"
ESTILO_TITULO_14PX = f"font-size: {TAMANO_TITULO}px; font-weight: bold;"
ESTILO_TITULO_14PX_OSCURO = f"font-size: {TAMANO_TITULO}px; color: {COLOR_OPT_TRAZO};"
ESTILO_TITULO_ACENTO_12PX = f"font-weight: bold; color: {ACEINTO}; font-size: {TAMANO_GRANDE}px;"
ESTILO_TITULO_DOCK = f"color: {TEXTO_SUAVE}; font-size: {TAMANO_PEQUENO}px; font-weight: bold; margin-top: {ESPACIO_4}px;"
ESTILO_TITULO_ESPACIADO = f"font-size: {TAMANO_MEDIO}px; color: {TEXTO}; letter-spacing: {ESPACIO_LETRA}px;"
ESTILO_VALOR_10PX_NEGRITA = f"color: {TEXTO}; font-size: {TAMANO_BASE}px; font-weight: bold;"
ESTILO_VALOR_11PX = f"color: {TEXTO}; font-size: {TAMANO_MEDIO}px;"
ESTILO_VALOR_11PX_NEGRITA = f"color: {TEXTO}; font-size: {TAMANO_MEDIO}px; font-weight: bold;"
ESTILO_VALOR_BLANCO_10PX = f"color: {TEXTO_CLARO}; font-size: {TAMANO_BASE}px; font-weight: bold;"
ESTILO_CAJON = f'QWidget {{ background-color: {COLOR_FONDO_BOTON}; color: {TEXTO}; }}QGroupBox {{ font-weight: bold; color: {TEXTO}; border: 1px solid {COLOR_BORDE_MEDIO}; border-radius: {RADIO_6}px; margin-top: {ESPACIO_10}px; padding-top: {ESPACIO_8}px; }}QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 {ESPACIO_4}px; }}QLabel {{ color: {TEXTO}; }}QComboBox, QDoubleSpinBox, QSpinBox {{  background-color: {BORDE_SUAVE}; color: {TEXTO};  border: 1px solid {COLOR_BORDE_MEDIO}; border-radius: {RADIO_3}px; padding: {ESPACIO_3}px;}}QPushButton {{  background-color: {BORDE_SUAVE}; color: {TEXTO};  border: 1px solid {COLOR_BORDE_MEDIO}; border-radius: {RADIO_4}px;  padding: {ESPACIO_6}px {ESPACIO_14}px; font-weight: bold;}}QPushButton:hover {{ background-color: {BORDE}; }}'
ESTILO_PUERTA_GRUPO_CABECERA = f"QGroupBox {{ background: {FONDO}; color: {TEXTO}; border: 1px solid {COLOR_BORDE_GRIS}; border-radius: {RADIO_4}px; margin-top: {ESPACIO_8}px; padding-top: {ESPACIO_4}px; }}QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}"
ESTILO_PUERTA_GRUPO = f"QGroupBox {{ color: {TEXTO}; border: 1px solid {COLOR_BORDE_GRIS}; border-radius: {RADIO_4}px; margin-top: {ESPACIO_8}px; }}QGroupBox::title {{ subcontrol-origin: margin; left: 8px; }}"
ESTILO_PUERTA_FONDO = f"QWidget {{ background: {FONDO}; color: {TEXTO}; }}"
ESTILO_PUERTA_TEXTO = f"color: {TEXTO};"
ESTILO_PUERTA_PISTON = f"QLabel {{ background: {COLOR_FONDO_PISTON}; color: {COLOR_VERDE_PISTON_TEXTO}; padding: {ESPACIO_6}px; border: 1px solid {COLOR_BORDE_PISTON}; font-weight: bold; }}"


def aplicar_estilo(widget, hoja):
    """Único punto de la UI que aplica una hoja de estilo (widget.setStyleSheet)."""
    widget.setStyleSheet(hoja)


def estilo_breadcrumb(clave, activo_es):
    """Hoja de la miga de pan del inspector: activa en blanco y negrita."""
    return (f"QLabel#lblBreadcrumb_{clave} {{ "
            f"color: {TEXTO_CLARO if activo_es else COLOR_TEXTO_ATENUADO}; "
            f"font-weight: {'bold' if activo_es else 'normal'}; "
            f"font-size: {TAMANO_BASE}px; }}")

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
