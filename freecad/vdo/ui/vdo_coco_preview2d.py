# =====================================================================
# vdo_coco_preview2d.py
# Vista frontal 2D del COCO: matriz de vanos, paneles y reengroses.
# Sin dependencias de FreeCAD 3D; sólo Qt.
# =====================================================================

from freecad.vdo.core import vdo_frames as VDO_FR
from freecad.vdo.core import vdo_reengrose_geometria as VDO_RE_GEOMETRIA
from freecad.vdo.core.vdo_facade_contract import CALLE_ENTRE_FRENTES_DEFAULT
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets

COLOR_FONDO = QtGui.QColor("#f7f7f5")
COLOR_INTERIOR = QtGui.QColor("#ffffff")
COLOR_PANEL = QtGui.QColor("#4a4a4a")
COLOR_CELDA = QtGui.QColor("#b8b8b8")
COLOR_SELECCION = QtGui.QColor("#e67e22")
COLOR_TEXTO = QtGui.QColor("#303030")
COLOR_ERROR = QtGui.QColor("#c0392b")
COLOR_TIRA = QtGui.QColor(230, 126, 34, 150)

ROLE_KIND = int(QtCore.Qt.UserRole) + 1
ROLE_KEY = int(QtCore.Qt.UserRole) + 2
ROLE_LABEL = int(QtCore.Qt.UserRole) + 3


class CocoPreview2D(QtWidgets.QGraphicsView):
    """Dibuja el frente interior del COCO y permite seleccionar piezas."""

    cellClicked = QtCore.Signal(str)
    panelClicked = QtCore.Signal(str)
    reengroseClicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setRenderHints(
            QtGui.QPainter.Antialiasing
            | QtGui.QPainter.TextAntialiasing)
        self.setMinimumHeight(190)
        self.setBackgroundBrush(COLOR_FONDO)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._cell_items = {}
        self._panel_items = {}
        self._strip_items = {}
        self._selected = None
        self._selected_entity = None
        self._outer_w = 0.0
        self._outer_h = 0.0
        self._resolved = None
        self._reengroses = {}
        self._entities = []
        self._fondo = 0.0

    # -----------------------------------------------------------------
    # API
    # -----------------------------------------------------------------
    def set_layout(self, resolved, outer_w=None, outer_h=None,
                   selected=None, reengroses=None, entities=None,
                   fondo=None, piezas=None, contenido_por_celda=None,
                   label_to_colrow=None):
        self._resolved = resolved
        self._outer_w = float(outer_w or resolved.inner_w)
        self._outer_h = float(outer_h or resolved.inner_h)
        self._selected = selected
        self._reengroses = dict(reengroses or {})
        self._entities = list(entities if entities is not None else piezas or [])
        self._fondo = float(fondo or 0.0)
        self._contenido_por_celda = dict(contenido_por_celda or {})
        self._label_to_colrow = dict(label_to_colrow or {})
        self._construir()

    def set_selected(self, label):
        self._selected = label
        self._selected_entity = None
        for label_item, item in self._cell_items.items():
            self._aplicar_estilo(item, label_item == label)
        for _clave, item in self._panel_items.items():
            self._aplicar_estilo_panel(item, False)
        for _clave, items in self._strip_items.items():
            for item in items:
                self._aplicar_estilo_tira(item, False)
        self.viewport().update()

    def set_selected_entity(self, kind, clave):
        self._selected = None
        self._selected_entity = (kind, clave)
        for item in self._cell_items.values():
            self._aplicar_estilo(item, False)
        for key, item in self._panel_items.items():
            self._aplicar_estilo_panel(
                item, kind == "panel" and key == clave)
        for key, items in self._strip_items.items():
            for item in items:
                self._aplicar_estilo_tira(
                    item, kind == "reengrose" and key == clave)
        self.viewport().update()

    def set_selected_panel(self, clave):
        self.set_selected_entity("panel", clave)

    def set_selected_reengrose(self, clave):
        self.set_selected_entity("reengrose", clave)

    def selected(self):
        return self._selected

    # -----------------------------------------------------------------
    # Geometría
    # -----------------------------------------------------------------
    def _rect(self, x, z, w, h):
        """Convierte coordenadas locales (origen abajo-izquierda) a escena."""
        margen = 14.0
        margen_sup = 34.0
        x0 = (self._outer_w - self._resolved.inner_w) / 2.0
        z0 = (self._outer_h - self._resolved.inner_h) / 2.0
        sx = margen + x0 + float(x)
        sy = margen_sup + self._outer_h - (z0 + float(z) + float(h))
        return QtCore.QRectF(sx, sy, float(w), float(h))

    def _rect_caja(self, caja):
        return self._rect(
            caja.get("x", 0.0), caja.get("z", 0.0),
            caja.get("w", 0.0), caja.get("d", 0.0))

    def _construir(self):
        scene = self.scene()
        scene.clear()
        self._cell_items = {}
        self._panel_items = {}
        self._strip_items = {}
        if self._resolved is None:
            return

        margen = 14.0
        margen_sup = 34.0
        total_w = self._outer_w + margen * 2.0
        total_h = self._outer_h + margen + margen_sup
        scene.setSceneRect(0.0, 0.0, total_w, total_h)

        self._dibujar_rotulos(scene, margen, total_w)
        interior = self._dibujar_carcasa(scene, margen, margen_sup)

        # Paneles físicos (carcasa + divisiones) bajo las celdas.
        self._dibujar_paneles(scene)

        self._dibujar_celdas(scene)

        # Líneas de frentes de cajón (torre apilada)
        self._dibujar_frentes_cajon(scene)

        # Tiras de reengrose, sólo sobre su pieza dueña.
        self._dibujar_tiras(scene)

        # Aviso de overflow.
        if self._resolved.overflow:
            scene.addRect(
                interior.adjusted(1, 1, -1, -1),
                QtGui.QPen(COLOR_ERROR, 2.0))

        self.fitInView(
            scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def _dibujar_rotulos(self, scene, margen, total_w):
        # Etiqueta de frente local y ejes.
        etiqueta = QtWidgets.QGraphicsSimpleTextItem(VDO_FR.ETIQUETA_FRENTE)
        fuente = etiqueta.font()
        fuente.setPointSizeF(7.5)
        fuente.setBold(True)
        etiqueta.setFont(fuente)
        etiqueta.setBrush(COLOR_TEXTO)
        etiqueta.setPos(margen, 7.0)
        scene.addItem(etiqueta)

        ejes = QtWidgets.QGraphicsSimpleTextItem(VDO_FR.EJES_PREVIEW)
        fuente_ejes = ejes.font()
        fuente_ejes.setPointSizeF(7.0)
        ejes.setFont(fuente_ejes)
        ejes.setBrush(COLOR_TEXTO)
        ancho_ejes = ejes.boundingRect().width()
        ejes.setPos(total_w - margen - ancho_ejes, 7.0)
        scene.addItem(ejes)

    def _dibujar_carcasa(self, scene, margen, margen_sup):
        # Carcasa exterior e interior.
        exterior = QtCore.QRectF(
            margen, margen_sup, self._outer_w, self._outer_h)
        scene.addRect(
            exterior, QtGui.QPen(QtGui.QColor("#7a7a7a"), 1.0),
            QtGui.QBrush(COLOR_FONDO))

        t = self._resolved.thickness
        interior = QtCore.QRectF(
            margen + t, margen_sup + t,
            self._resolved.inner_w, self._resolved.inner_h)
        scene.addRect(
            interior, QtGui.QPen(QtGui.QColor("#d0d0d0"), 1.0),
            QtGui.QBrush(COLOR_INTERIOR))

        return interior

    def _dibujar_celdas(self, scene):
        # Celdas (transparentes, encima de los paneles para poder clicar).
        for cell in self._resolved.walk_cells():
            rect = self._rect(cell.x, cell.z, cell.w, cell.h)
            item = QtWidgets.QGraphicsRectItem(rect)
            item.setData(ROLE_KIND, "cell")
            item.setData(ROLE_KEY, cell.label)
            item.setData(ROLE_LABEL, cell.label)
            item.setAcceptHoverEvents(True)
            item.setZValue(10.0 + cell.level * 0.1)
            item.setToolTip(
                f"{cell.label}\nX libre: {cell.w:.1f} mm\n"
                f"Y libre: {cell.h:.1f} mm")
            scene.addItem(item)
            self._cell_items[cell.label] = item
            self._aplicar_estilo(item, cell.label == self._selected)

            if cell.w >= 50.0 and cell.h >= 18.0:
                texto = QtWidgets.QGraphicsSimpleTextItem(cell.label, item)
                fuente = texto.font()
                fuente.setPointSizeF(6.5)
                texto.setFont(fuente)
                texto.setBrush(COLOR_TEXTO)
                br = texto.boundingRect()
                texto.setPos(
                    rect.center().x() - br.width() / 2.0,
                    rect.center().y() - br.height() / 2.0)
