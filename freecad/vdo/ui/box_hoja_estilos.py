"""Hoja de estilos oscura. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.ui import tema_colores

# ----------------------------------------------------------------------
# Hoja de estilos oscura (Figma Dark Theme)
# ----------------------------------------------------------------------
ESTILO_WIDGET = f"""
QWidget#VDOBoxRoot {{
    background-color: {tema_colores.FONDO};
    color: {tema_colores.TEXTO};
}}

QFrame#canvas_container {{
    background-color: {tema_colores.COLOR_FONDO_PROFUNDO};
    border: 1px solid {tema_colores.FONDO3};
    border-radius: 8px;
}}

QPushButton.borde-btn {{
    background-color: {tema_colores.FONDO2};
    border: 1px solid {tema_colores.BORDE};
    border-radius: 4px;
    color: {tema_colores.TEXTO_SUAVE};
    font-size: 10px;
    font-weight: bold;
    padding: 2px 4px;
}}
QPushButton.borde-btn:hover {{
    background-color: {tema_colores.FONDO3};
    border-color: {tema_colores.BORDE_CLARO};
    color: {tema_colores.TEXTO_SUAVE2};
}}
QPushButton.borde-btn:checked {{
    background-color: {tema_colores.ACEINTO_HOVER};
    border: 1px solid {tema_colores.ACEINTO};
    color: {tema_colores.TEXTO_CLARO};
}}
QPushButton.borde-btn[selected="true"] {{
    border: 1.5px solid {tema_colores.COLOR_ACENTO_CIAN};
}}

QPushButton.esquina-btn {{
    background-color: {tema_colores.COLOR_FONDO_ENTRADA};
    border: 1px solid {tema_colores.BORDE};
    border-radius: 4px;
    padding: 2px;
}}
QPushButton.esquina-btn:hover {{
    background-color: {tema_colores.COLOR_FONDO_ELEVADO};
    border-color: {tema_colores.ACEINTO};
}}
QPushButton.esquina-btn:pressed {{
    background-color: {tema_colores.COLOR_FONDO_CANVAS};
}}

QPushButton.centro-btn {{
    background-color: {tema_colores.COLOR_FONDO_CAJA};
    border: 1px solid {tema_colores.BORDE_SUAVE};
    border-radius: 6px;
    color: {tema_colores.TEXTO_SUAVE2};
    font-size: 10px;
    font-weight: bold;
    padding: 3px 6px;
}}
QPushButton.centro-btn:hover {{
    background-color: {tema_colores.COLOR_FONDO_BASE};
    border-color: {tema_colores.COLOR_BORDE_MEDIO};
    color: {tema_colores.TEXTO_CLARO};
}}
QPushButton.centro-btn:checked {{
    background-color: {tema_colores.COLOR_ACENTO_FONDO};
    border: 1px solid {tema_colores.ACEINTO};
    color: {tema_colores.COLOR_TEXTO_AZUL_CLARO};
}}

QPushButton.all-btn {{
    background-color: {tema_colores.COLOR_FONDO_BOTON};
    border: 1px solid {tema_colores.BORDE};
    border-radius: 4px;
    color: {tema_colores.TEXTO_SUAVE2};
    font-weight: bold;
    font-size: 11px;
    padding: 2px 8px;
}}
QPushButton.all-btn:hover {{
    background-color: {tema_colores.COLOR_FONDO_SECUNDARIO};
    border-color: {tema_colores.BORDE_CLARO};
}}
QPushButton.all-btn:checked {{
    background-color: {tema_colores.ACEINTO};
    border-color: {tema_colores.ACEINTO};
    color: {tema_colores.TEXTO_CLARO};
}}

QPushButton.chip-btn {{
    background-color: {tema_colores.COLOR_FONDO_BASE};
    border: 1px solid {tema_colores.BORDE};
    border-radius: 3px;
    color: {tema_colores.COLOR_TEXTO_ATENUADO};
    font-size: 10px;
    padding: 2px 6px;
}}
QPushButton.chip-btn:hover {{
    background-color: {tema_colores.FONDO3};
    border-color: {tema_colores.ACEINTO};
    color: {tema_colores.TEXTO_CLARO};
}}
QPushButton.chip-btn:checked {{
    background-color: {tema_colores.COLOR_ACENTO_PRESIONADO};
    border-color: {tema_colores.ACEINTO};
    color: {tema_colores.TEXTO_CLARO};
    font-weight: bold;
}}

QCheckBox {{
    color: {tema_colores.COLOR_TEXTO_SECUNDARIO};
    font-size: 11px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
}}

QLabel {{
    color: {tema_colores.TEXTO_SUAVE2};
    font-size: 11px;
}}
"""
