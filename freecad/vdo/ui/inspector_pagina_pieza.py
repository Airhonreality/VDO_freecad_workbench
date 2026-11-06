"""Pagina de pieza del inspector: cabecera de panel y caja."""

import json
import logging

import FreeCAD as App

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets

try:
    from freecad.vdo.ui.box_controller import VDOBoxControllerWidget
except ImportError as exc:  # pragma: no cover
    _LOG.debug("inspector_pagina_pieza: controlador no disponible: %s", exc)
    VDOBoxControllerWidget = None
from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import anadir_propiedad_texto, asignar_propiedades
from freecad.vdo.ui import tema
from freecad.vdo.ui.inspector_paginas import _float_seguro, _PaginaBase, _str_seguro

_LOG = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# PÁGINA 2: PIEZA L1 (PanelHeader + Cuadrado Figma)
# ----------------------------------------------------------------------
class PaginaPieza(_PaginaBase):
    """Nivel Pieza Física (PANEL): Header + Cuadrado Figma (VDOBoxController)."""

    def __init__(self, parent=None):
        super().__init__("Pieza / Tablero (Panel L1)", parent)
        self._obj_actual = None

        self.header = QtWidgets.QGroupBox("PanelHeader")
        self.header.setObjectName("grpPanelHeader")
        tema.aplicar_estilo(self.header, tema.ESTILO_GRUPO_PANEL_HEADER)
        h_layout = QtWidgets.QGridLayout(self.header)
        h_layout.setContentsMargins(8, 14, 8, 8)
        h_layout.setHorizontalSpacing(8)
        h_layout.setVerticalSpacing(3)

        self.lbl_largo = QtWidgets.QLabel("—")
        self.lbl_ancho = QtWidgets.QLabel("—")
        self.lbl_espesor = QtWidgets.QLabel("—")
        self.lbl_canto_norte = QtWidgets.QLabel("—")
        self.lbl_canto_sur = QtWidgets.QLabel("—")
        self.lbl_canto_este = QtWidgets.QLabel("—")
        self.lbl_canto_oeste = QtWidgets.QLabel("—")

        def _fila(r, clave, lbl_widget, label_txt):
            k = QtWidgets.QLabel(label_txt)
            tema.aplicar_estilo(k, tema.ESTILO_CLAVE_10PX)
            v = lbl_widget
            tema.aplicar_estilo(v, tema.ESTILO_VALOR_10PX_NEGRITA)
            h_layout.addWidget(k, r, 0)
            h_layout.addWidget(v, r, 1)

        _fila(0, "Largo", self.lbl_largo, "Largo (mm):")
        _fila(0, "Ancho", self.lbl_ancho, "Ancho (mm):")
        _fila(0, "Espesor", self.lbl_espesor, "Espesor (mm):")
        _fila(1, "CantoNorte", self.lbl_canto_norte, "Canto N:")
        _fila(1, "CantoSur", self.lbl_canto_sur, "Canto S:")
        _fila(2, "CantoEste", self.lbl_canto_este, "Canto E:")
        _fila(2, "CantoOeste", self.lbl_canto_oeste, "Canto O:")

        self.contenedor_datos.addWidget(self.header)

        # Cuadrado Figma (VDOBoxControllerWidget)
        self.box_controller = None
        if VDOBoxControllerWidget is not None:
            self.box_controller = VDOBoxControllerWidget()
            self.box_controller.sigConfigChanged.connect(self._on_box_changed)
            self.contenedor_datos.addWidget(self.box_controller)

    def cargar_panel(self, obj):
        self._obj_actual = obj
        largo = _float_seguro(getattr(obj, "Largo", None))
        ancho = _float_seguro(getattr(obj, "Ancho", None))
        espesor = _float_seguro(getattr(obj, "Espesor", None))

        self.lbl_largo.setText(f"{largo:.1f}" if largo else "—")
        self.lbl_ancho.setText(f"{ancho:.1f}" if ancho else "—")
        self.lbl_espesor.setText(f"{espesor:.1f}" if espesor else "—")

        canto_norte = _str_seguro(getattr(obj, "VDO_Canto_Norte", None), "FX")
        canto_sur = _str_seguro(getattr(obj, "VDO_Canto_Sur", None), "FX")
        canto_este = _str_seguro(getattr(obj, "VDO_Canto_Este", None), "FX")
        canto_oeste = _str_seguro(getattr(obj, "VDO_Canto_Oeste", None), "FX")
        self.lbl_canto_norte.setText(canto_norte)
        self.lbl_canto_sur.setText(canto_sur)
        self.lbl_canto_este.setText(canto_este)
        self.lbl_canto_oeste.setText(canto_oeste)

        if self.box_controller is not None:
            raw_cfg = getattr(obj, "VDO_Reengrose_JSON", None)
            if raw_cfg:
                try:
                    cfg = json.loads(raw_cfg) if isinstance(raw_cfg, str) else raw_cfg
                    self.box_controller.setConfig(cfg)
                    return
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo cargar VDO_Reengrose_JSON")

            self.box_controller.setConfig({
                "activo": True,
                "uniforme": True,
                "ancho_uniforme": 70.0,
                "distancia_uniforme": 0.0,
                "espesor": espesor if espesor else None,
                "bordes": {
                    b: {"activo": True, "ancho": 70.0, "offset_borde": 0.0}
                    for b in ("frente", "fondo", "izquierda", "derecha")
                },
            })

    def cargar_pieza_dict(self, pieza):
        """Carga las cotas de una pieza física a partir de un dict calculado."""
        largo = float(pieza.get("largo", 0.0))
        ancho = float(pieza.get("ancho", 0.0))
        espesor = float(pieza.get("espesor", 18.0))
        self.lbl_largo.setText(f"{largo:.1f}")
        self.lbl_ancho.setText(f"{ancho:.1f}")
        self.lbl_espesor.setText(f"{espesor:.1f}")

        cantos = pieza.get("cantos", {})
        if isinstance(cantos, dict):
            self.lbl_canto_norte.setText(cantos.get("norte", "FX"))
            self.lbl_canto_sur.setText(cantos.get("sur", "FX"))
            self.lbl_canto_este.setText(cantos.get("este", "FX"))
            self.lbl_canto_oeste.setText(cantos.get("oeste", "FX"))

    def _on_box_changed(self, cfg):
        obj = self._obj_actual
        if obj is None:
            return
        try:
            if hasattr(obj, "VDO_Reengrose_JSON"):
                asignar_propiedades(obj, {"VDO_Reengrose_JSON": json.dumps(cfg)})
            elif hasattr(obj, "addProperty"):
                try:
                    anadir_propiedad_texto(obj, "VDO_Reengrose_JSON", "VDO", "Regrueso JSON")
                    asignar_propiedades(obj, {"VDO_Reengrose_JSON": json.dumps(cfg)})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo añadir propiedad VDO_Reengrose_JSON")
            doc = getattr(obj, "Document", None)
            if doc is not None:
                recalcular(doc)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo persistir VDO_Reengrose_JSON")
