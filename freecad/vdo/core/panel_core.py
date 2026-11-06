# =====================================================================
# panel_core.py
# Cálculo puro de paneles: validación de la orientación y mapeo de
# expresiones de Params. Sin FreeCAD. La escritura vive en cad/panel.py.
# =====================================================================

from typing import Any

from freecad.vdo.core import defaults as VDO_D


def _validar_orientacion(configuracion: dict[str, Any]) -> str:
    """Valida de forma estricta la clave 'orientacion'."""
    if "orientacion" not in configuracion:
        raise ValueError(
            "Configuración inválida: falta la clave obligatoria 'orientacion'. "
            "Ningún panel puede crearse sin definir su orientación "
            f"({', '.join(VDO_D.ORIENTACIONES_VALIDAS)}).")

    orientacion: str = configuracion["orientacion"]
    if orientacion not in VDO_D.ORIENTACIONES_VALIDAS:
        raise ValueError(
            f"Orientación inválida: '{orientacion}'. "
            f"Debe ser una de: {', '.join(VDO_D.ORIENTACIONES_VALIDAS)}.")
    return orientacion


def expresiones_orientacion(orientacion: str) -> tuple[str, str, str]:
    """Devuelve (largo, ancho, espesor) como nombres de Params según la orientación.

    `Largo`/`Ancho` son siempre las caras del tablero y `Espesor` su grosor
    (semántica de despiece), NO los ejes locales de la caja.
      - horizontal: Largo=ancho, Ancho=fondo, Espesor=espesor
      - vertical:   Largo=alto,  Ancho=fondo, Espesor=espesor
    """
    VDO_D.obtener_mapeo_orientacion(orientacion)  # valida el vocabulario
    if orientacion == "vertical":
        return "alto", "fondo", "espesor"
    return "ancho", "fondo", "espesor"
