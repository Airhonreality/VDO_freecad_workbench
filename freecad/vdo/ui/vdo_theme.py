# -*- coding: utf-8 -*-
# =====================================================================
# vdo_theme.py
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


def get_svg_icon(name: str, size: int = 22,
                 icons_map: dict = None, cache: dict = None) -> QtGui.QIcon:
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
    "FONDO", "FONDO2", "FONDO3",
    "TEXTO", "TEXTO_SUAVE", "TEXTO_CLARO", "TEXTO_SUAVE2",
    "BORDE", "BORDE_SUAVE", "BORDE_ACTIVO", "BORDE_CLARO",
    "ACEINTO", "ACEINTO_HOVER",
    "ERROR", "EXITO", "AVISO",
    "ESTILO_BOTON_PRIMARIO", "ESTILO_BOTON_SECUNDARIO",
    "ESTILO_INPUT", "ESTILO_GROUPBOX", "estilo_boton",
    "get_svg_icon",
]
