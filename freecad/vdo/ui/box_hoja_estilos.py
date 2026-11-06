"""Hoja de estilos oscura. Parte de ui/box_controller.py (M7, D-44)."""

from freecad.vdo.ui import tema

# ----------------------------------------------------------------------
# Hoja de estilos oscura (Figma Dark Theme)
# ----------------------------------------------------------------------
ESTILO_WIDGET = f"""
QWidget#VDOBoxRoot {{
    background-color: {tema.FONDO};
    color: {tema.TEXTO};
}}

QFrame#canvas_container {{
    background-color: {tema.COLOR_FONDO_PROFUNDO};
    border: 1px solid {tema.FONDO3};
    border-radius: 8px;
}}

QPushButton.borde-btn {{
    background-color: {tema.FONDO2};
    border: 1px solid {tema.BORDE};
    border-radius: 4px;
    color: {tema.TEXTO_SUAVE};
    font-size: 10px;
    font-weight: bold;
    padding: 2px 4px;
}}
QPushButton.borde-btn:hover {{
    background-color: {tema.FONDO3};
    border-color: {tema.BORDE_CLARO};
    color: {tema.TEXTO_SUAVE2};
}}
QPushButton.borde-btn:checked {{
    background-color: {tema.ACEINTO_HOVER};
    border: 1px solid {tema.ACEINTO};
    color: {tema.TEXTO_CLARO};
}}
QPushButton.borde-btn[selected="true"] {{
    border: 1.5px solid {tema.COLOR_ACENTO_CIAN};
}}

QPushButton.esquina-btn {{
    background-color: {tema.COLOR_FONDO_ENTRADA};
    border: 1px solid {tema.BORDE};
    border-radius: 4px;
    padding: 2px;
}}
QPushButton.esquina-btn:hover {{
    background-color: {tema.COLOR_FONDO_ELEVADO};
    border-color: {tema.ACEINTO};
}}
QPushButton.esquina-btn:pressed {{
    background-color: {tema.COLOR_FONDO_CANVAS};
}}

QPushButton.centro-btn {{
    background-color: {tema.COLOR_FONDO_CAJA};
    border: 1px solid {tema.BORDE_SUAVE};
    border-radius: 6px;
    color: {tema.TEXTO_SUAVE2};
    font-size: 10px;
    font-weight: bold;
    padding: 3px 6px;
}}
QPushButton.centro-btn:hover {{
    background-color: {tema.COLOR_FONDO_BASE};
    border-color: {tema.COLOR_BORDE_MEDIO};
    color: {tema.TEXTO_CLARO};
}}
QPushButton.centro-btn:checked {{
    background-color: {tema.COLOR_ACENTO_FONDO};
    border: 1px solid {tema.ACEINTO};
    color: {tema.COLOR_TEXTO_AZUL_CLARO};
}}

QPushButton.all-btn {{
    background-color: {tema.COLOR_FONDO_BOTON};
    border: 1px solid {tema.BORDE};
    border-radius: 4px;
    color: {tema.TEXTO_SUAVE2};
    font-weight: bold;
    font-size: 11px;
    padding: 2px 8px;
}}
QPushButton.all-btn:hover {{
    background-color: {tema.COLOR_FONDO_SECUNDARIO};
    border-color: {tema.BORDE_CLARO};
}}
QPushButton.all-btn:checked {{
    background-color: {tema.ACEINTO};
    border-color: {tema.ACEINTO};
    color: {tema.TEXTO_CLARO};
}}

QPushButton.chip-btn {{
    background-color: {tema.COLOR_FONDO_BASE};
    border: 1px solid {tema.BORDE};
    border-radius: 3px;
    color: {tema.COLOR_TEXTO_ATENUADO};
    font-size: 10px;
    padding: 2px 6px;
}}
QPushButton.chip-btn:hover {{
    background-color: {tema.FONDO3};
    border-color: {tema.ACEINTO};
    color: {tema.TEXTO_CLARO};
}}
QPushButton.chip-btn:checked {{
    background-color: {tema.COLOR_ACENTO_PRESIONADO};
    border-color: {tema.ACEINTO};
    color: {tema.TEXTO_CLARO};
    font-weight: bold;
}}

QCheckBox {{
    color: {tema.COLOR_TEXTO_SECUNDARIO};
    font-size: 11px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
}}

QLabel {{
    color: {tema.TEXTO_SUAVE2};
    font-size: 11px;
}}
"""
