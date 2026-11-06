"""
box_controller.py

Controlador espacial 2D de tablero al estilo Figma Box Model / CSS DevTools.
Implementa el "Cuadrado Paramétrico Gestáltico" con líneas de distinto calibre (1px y 3px)
para parametrizar visualmente tanto el ANCHO de las tiras como el OFFSET (distancia al canto / retranqueo).

Arquitectura Gestáltica de Doble Anillo (Opción A):
    - Calibre 1 px (Exterior): Canto físico del tablero y selección de márgenes.
    - Calibre 3 px (Interior): Tiras de melamina activas / inactivas.
    - Brecha concéntrica variable: Muestra visualmente si la tira está al ras (0 mm)
      o retranqueada (>0 mm) con línea guía de acotación.
    - Acceso rápido de taller: Chips para 0 (al ras), 18 (1 espesor), 36 (2 espesores), 50 (zócalo).

Totalmente agnóstico de FreeCAD: compatible con PySide, PySide2 y PySide6.
"""

import logging
import sys

from freecad.vdo.core import reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets

from freecad.vdo.ui.box_config import BoxConfigMixin
from freecad.vdo.ui.box_constantes import ESQUINAS
from freecad.vdo.ui.box_construccion import BoxConstruccionMixin
from freecad.vdo.ui.box_esquinas import BoxEsquinasMixin
from freecad.vdo.ui.box_estado import BoxEstadoMixin
from freecad.vdo.ui.box_hoja_estilos import ESTILO_WIDGET
from freecad.vdo.ui.box_margen import BoxMargenMixin
from freecad.vdo.ui import tema

_LOG = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Widget Principal VDOBoxControllerWidget
# ----------------------------------------------------------------------
class VDOBoxControllerWidget(
    BoxConstruccionMixin,
    BoxMargenMixin,
    BoxEsquinasMixin,
    BoxEstadoMixin,
    BoxConfigMixin,
    QtWidgets.QWidget,
):
    """
    Controlador interactivo espacial de borde perimetral estilo Figma Box Model.
    Implementa el Cuadrado Gestáltico con calibres 1px (Canto/Offset) y 3px (Tira).
    """

    sigConfigChanged = QtCore.Signal(dict)
    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VDOBoxRoot")
        tema.aplicar_estilo(self, ESTILO_WIDGET)

        self._cargando = False
        self._margen_seleccionado = "frente"
        self._borde_seleccionado = "frente"
        self._valores_bordes = {
            borde: {"ancho": 70.0, "offset": 0.0}
            for borde in VDO_RE_MODELO.BORDES_2D
        }
        self._esquinas = {
            esquina: "vertical_domina"
            for esquina in ESQUINAS
        }
        self._fabricacion = "pacha"
        self._choque_nucleo = "retroceso"
        self._cara = "cara_a"

        self._construir_ui()
        self._conectar_senales()
        self._actualizar_canvas_concentrico()
        self._actualizar_estado_all()
        self._actualizar_iconos_esquinas()
        self._actualizar_resumen()


# ----------------------------------------------------------------------
# Ejecución Directa Standalone para Validación Visual
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta oscura global
    paleta = QtGui.QPalette()
    paleta.setColor(QtGui.QPalette.Window, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Base, QtGui.QColor("#252525"))
    paleta.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#1e1e1e"))
    paleta.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.Text, QtGui.QColor("#e0e0e0"))
    paleta.setColor(QtGui.QPalette.Button, QtGui.QColor("#2b2b2b"))
    paleta.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#ffffff"))
    paleta.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#007acc"))
    paleta.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(paleta)

    ventana = QtWidgets.QMainWindow()
    ventana.setWindowTitle("VDO Box Controller - Cuadrado Concéntrico Gestáltico (1px / 3px)")
    ventana.setMinimumSize(320, 440)

    widget = VDOBoxControllerWidget()
    widget.setConfig({
        "activo": True,
        "uniforme": True,
        "ancho_uniforme": 70.0,
        "distancia_uniforme": 0.0,
        "esquinas": "inglete_45",
        "bordes": {
            b: {"activo": True, "ancho": 70.0, "offset_borde": 0.0}
            for b in VDO_RE_MODELO.BORDES_2D
        }
    })

    def on_change(cfg):
        activos = [b for b, d in cfg["bordes"].items() if d["activo"]]
        _LOG.debug(f"[VDO Box Event] Activos={activos} Esquinas={cfg['esquinas']} Uniforme={cfg['uniforme']}")

    widget.sigConfigChanged.connect(on_change)

    ventana.setCentralWidget(widget)
    ventana.show()
    exec_func = getattr(app, "exec", getattr(app, "exec_", None))
    sys.exit(exec_func())
