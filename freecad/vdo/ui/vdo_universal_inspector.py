# =====================================================================
# vdo_universal_inspector.py
# Inspector Universal Reactivo Consolidado — Sistema VDO (FreeCAD).
#
# Panel unificado permanente lateral con:
# 1. Micro-Header editable de alta densidad:
#    📐 [ W ] × [ H ] × [ D ] mm │ Espesor: [ E ] mm
# 2. Visor 2D frontal en elevación completa (CocoPreview2D)
# 3. QSplitter horizontal inferior que aloja:
#    - Izquierda: QTreeWidget Maestro unificado (Chasis, Piezas, Vanos e Insertos)
#    - Derecha: QStackedWidget reactivo (Páginas Chasis, Vano, Pieza y Cierre)
#
# Sincronización bidireccional total entre 3D, 2D, Árbol y Páginas.
# =====================================================================

import json
import FreeCAD as App
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
try:
    import FreeCADGui as Gui
except ImportError:  # pragma: no cover
    Gui = None
from freecad.vdo.ui.vdo_selection_bridge import VDOSelectionBridge
try:
    from freecad.vdo.ui.vdo_coco_preview2d import CocoPreview2D
except ImportError:  # pragma: no cover
    CocoPreview2D = None
try:
    from freecad.vdo.core.vdo_layout_matriz import Layout
    from freecad.vdo.core.vdo_layout_modelo import cavidad_interior
    from freecad.vdo.core.vdo_layout_resolucion import resolve_layout
except ImportError:  # pragma: no cover
    Layout = None
    resolve_layout = None
    cavidad_interior = None
from freecad.vdo.ui.inspector_acciones import AccionesInspectorMixin
from freecad.vdo.ui.inspector_arbol import ArbolInspectorMixin
from freecad.vdo.ui.inspector_cabecera import _BreadcrumbBar, _MicroHeaderWidget
from freecad.vdo.ui.inspector_pagina_pieza import PaginaPieza
from freecad.vdo.ui.inspector_pagina_vano import PaginaVano
from freecad.vdo.ui.inspector_paginas import PAGE_CHASIS, PaginaChasis, PaginaCierre, _float_seguro


class VDOUniversalInspectorWidget(ArbolInspectorMixin, AccionesInspectorMixin, QtWidgets.QWidget):
    """
    Inspector universal lateral reactivo para el Sistema VDO.
    Unifica en un solo panel permanente:
    - Micro-Header editable
    - Visor 2D frontal (CocoPreview2D)
    - Árbol Maestro Izquierdo (QTreeWidget)
    - Stack Contextual Derecho (Chasis, Vano, Pieza, Cierre)
    """
    sigNivelCambiado = QtCore.Signal(int, str)  # (page_index, target_type)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VDOUniversalInspector")
        self.setMinimumWidth(320)

        self._puente = None
        self._obj_actual = None
        self._tipo_actual = VDOSelectionBridge.TARGET_UNKNOWN

        self._resolved_layout = None
        self._piezas_calculadas = []

        self._construir_ui()
        self._inicializar_puente()
    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _construir_ui(self):
        root = self._crear_raiz()
        self._crear_cabecera(root)
        self._crear_preview(root)
        self._crear_splitter()
        self._crear_arbol_maestro()
        self._crear_stack()
        # Proporción inicial del splitter (130px árbol : 230px stack)
        self.splitter.setSizes([130, 230])
        root.addWidget(self.splitter, 1)

        # Iniciar en nivel Chasis
        self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)

    def _crear_raiz(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        return root

    def _crear_cabecera(self, root):
        # 1. Breadcrumbs
        self.breadcrumbs = _BreadcrumbBar(self)
        self.breadcrumbs.sigNivelClickeado.connect(self._on_breadcrumb_clicked)
        root.addWidget(self.breadcrumbs)

        # 2. Micro-Header editable
        self.micro_header = _MicroHeaderWidget(self)
        self.micro_header.sigDimensionesCambiadas.connect(self._on_dimensiones_header_cambiadas)
        root.addWidget(self.micro_header)

    def _crear_preview(self, root):
        # 3. Visor 2D (CocoPreview2D)
        self.preview = None
        if CocoPreview2D is not None:
            self.preview = CocoPreview2D(self)
            self.preview.setMinimumHeight(150)
            self.preview.setMaximumHeight(210)
            self.preview.cellClicked.connect(self._on_preview_cell_clicked)
            self.preview.panelClicked.connect(self._on_preview_panel_clicked)
            self.preview.reengroseClicked.connect(self._on_preview_reengrose_clicked)
            root.addWidget(self.preview)

    def _crear_splitter(self):
        # 4. QSplitter Horizontal Inferior
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2b2b2b;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
        """)

    def _crear_arbol_maestro(self):
        # Panel Izquierdo: QTreeWidget Maestro
        self.master_tree = QtWidgets.QTreeWidget(self.splitter)
        self.master_tree.setHeaderHidden(True)
        self.master_tree.setIndentation(12)
        self.master_tree.setUniformRowHeights(True)
        self.master_tree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.master_tree.setStyleSheet("""
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
        """)
        self.master_tree.itemClicked.connect(self._on_tree_item_clicked)
        self.splitter.addWidget(self.master_tree)

    def _crear_stack(self):
        # Panel Derecho: QStackedWidget con las 4 páginas
        self.stack = QtWidgets.QStackedWidget(self.splitter)

        self.pagina_chasis = PaginaChasis()
        self.pagina_vano = PaginaVano()
        self.pagina_pieza = PaginaPieza()
        self.pagina_cierre = PaginaCierre()

        # Conectar cambios de vano para actualizar preview
        self.pagina_vano.sigHabitanteCambiado.connect(self._on_habitante_vano_cambiado)

        self.stack.addWidget(self.pagina_chasis)   # 0
        self.stack.addWidget(self.pagina_vano)     # 1
        self.stack.addWidget(self.pagina_pieza)    # 2
        self.stack.addWidget(self.pagina_cierre)   # 3

        self.splitter.addWidget(self.stack)

    # ------------------------------------------------------------------
    # Sincronización del Árbol Maestro y Preview 2D
    # ------------------------------------------------------------------
    def cargar_coco(self, obj):
        """Carga y sincroniza el COCO completo en Preview 2D, Árbol y Chasis."""
        self._obj_actual = obj
        alto = _float_seguro(getattr(obj, "Alto", None), 720.0)
        ancho = _float_seguro(getattr(obj, "Ancho", None), 600.0)
        fondo = _float_seguro(getattr(obj, "FondoModulo", None), 580.0)
        espesor = _float_seguro(getattr(obj, "Espesor", None), 18.0)

        # 1. Actualizar Micro-Header
        self.micro_header.cargar_dimensiones(ancho, alto, fondo, espesor)

        # 2. Cargar página Chasis
        self.pagina_chasis.cargar_coco(obj)

        # 3. Resolver Layout y calcular piezas
        self._actualizar_vista_completa()
    def _actualizar_vista_completa(self):
        """Recalcula layout, actualiza CocoPreview2D y regenera el QTreeWidget Maestro."""
        obj = self._obj_actual
        alto = _float_seguro(getattr(obj, "Alto", None), 720.0)
        ancho = _float_seguro(getattr(obj, "Ancho", None), 600.0)
        fondo = _float_seguro(getattr(obj, "FondoModulo", None), 580.0)
        espesor = _float_seguro(getattr(obj, "Espesor", None), 18.0)
        layout = self._leer_layout(obj)
        reengroses = self._leer_reengroses(obj)
        contenido_por_celda = self._leer_contenido(obj)
        resolved = self._resolver_layout(layout, alto, ancho, espesor, reengroses)
        self._resolved_layout = resolved
        piezas = self._piezas_estructura(alto, ancho, fondo, espesor)
        piezas = self._agregar_divisiones(piezas, resolved, fondo, espesor)
        self._piezas_calculadas = piezas
        self._actualizar_preview(resolved, ancho, alto, piezas, fondo, reengroses)
        # 5. Regenerar Árbol Maestro
        self._regenerar_arbol_maestro(obj, piezas, resolved, contenido_por_celda)

    def _leer_layout(self, obj):
        texto_div = getattr(obj, "VDO_Divisiones", "") or ""
        layout = Layout.loads(texto_div) if Layout is not None else None
        return layout

    def _leer_reengroses(self, obj):
        texto_reeng = getattr(obj, "VDO_Reengrose_JSON", "{}") or "{}"
        try:
            reengroses = json.loads(texto_reeng) if isinstance(texto_reeng, str) else dict(texto_reeng)
        except Exception:
            reengroses = {}
        return reengroses

    def _leer_contenido(self, obj):
        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "{}") or "{}"
        try:
            contenido_por_celda = json.loads(texto_contenido) if isinstance(texto_contenido, str) else dict(texto_contenido)
        except Exception:
            contenido_por_celda = {}
        return contenido_por_celda

    def _resolver_layout(self, layout, alto, ancho, espesor, reengroses):
        resolved = None
        if layout is not None and resolve_layout is not None and cavidad_interior is not None:
            cavidad = cavidad_interior(alto, ancho, espesor)
            resolved = resolve_layout(
                layout,
                max(0.0, cavidad["ancho"]),
                max(0.0, cavidad["alto"]),
                espesor,
                reengroses=reengroses
            )
        return resolved

    def _piezas_estructura(self, alto, ancho, fondo, espesor):
        # Calcular lista de piezas físicas
        cav_w = (ancho - 2.0 * espesor) if ancho > 2.0 * espesor else ancho
        (alto - 2.0 * espesor) if alto > 2.0 * espesor else alto

        piezas = [
            {
                "key": "base",
                "nombre": "Base",
                "largo": ancho,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": 0.0, "y": 0.0, "z": 0.0, "w": cav_w, "h": fondo, "d": espesor},
                "cantos": {"norte": "RIG", "sur": "FX", "este": "FX", "oeste": "FX"},
            },
            {
                "key": "techo",
                "nombre": "Tapa / Techo",
                "largo": ancho,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": 0.0, "y": 0.0, "z": max(0.0, alto - espesor), "w": cav_w, "h": fondo, "d": espesor},
                "cantos": {"norte": "RIG", "sur": "FX", "este": "FX", "oeste": "FX"},
            },
            {
                "key": "lat_izq",
                "nombre": "Lateral Izquierdo",
                "largo": alto,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": 0.0, "y": 0.0, "z": 0.0, "w": espesor, "h": fondo, "d": alto},
                "cantos": {"norte": "RIG", "sur": "RIG", "este": "FX", "oeste": "FX"},
            },
            {
                "key": "lat_der",
                "nombre": "Lateral Derecho",
                "largo": alto,
                "ancho": fondo,
                "espesor": espesor,
                "caja": {"x": max(0.0, ancho - espesor), "y": 0.0, "z": 0.0, "w": espesor, "h": fondo, "d": alto},
                "cantos": {"norte": "RIG", "sur": "RIG", "este": "FX", "oeste": "FX"},
            },
        ]
        return piezas

    def _agregar_divisiones(self, piezas, resolved, fondo, espesor):
        # Agregar divisiones de layout si existen
        if resolved is not None:
            for idx, p in enumerate(resolved.pieces):
                piezas.append({
                    "key": f"div_{p.axis.lower()}_{idx}",
                    "nombre": f"{'Repisa' if p.axis == 'Y' else 'Montante'} {idx + 1}",
                    "largo": p.w if p.axis == 'Y' else p.h,
                    "ancho": fondo,
                    "espesor": espesor,
                    "caja": {"x": p.x, "y": 0.0, "z": p.z, "w": p.w, "h": fondo, "d": p.h},
                    "cantos": {"norte": "FX", "sur": "FX", "este": "FX", "oeste": "FX"},
                })
        return piezas

    def _actualizar_preview(self, resolved, ancho, alto, piezas, fondo, reengroses):
        # 4. Actualizar Visor 2D (CocoPreview2D)
        if self.preview is not None and resolved is not None:
            try:
                self.preview.set_layout(
                    resolved,
                    outer_w=ancho,
                    outer_h=alto,
                    entities=piezas,
                    fondo=fondo,
                    reengroses=reengroses,
                )
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo actualizar el visor 2D")

    # ------------------------------------------------------------------
    # API pública y Ciclo de Vida
    # ------------------------------------------------------------------
    def pagina_actual(self):
        return self.stack.currentIndex() if self.stack is not None else -1
    def tipo_actual(self):
        return self._tipo_actual
    def objeto_actual(self):
        return self._obj_actual
    def puente(self):
        return self._puente
    def cerrar_inspector(self):
        """Limpieza: desregistra el observer de FreeCAD sin fugas."""
        try:
            if self._puente is not None:
                self._puente.detach()
                self._puente = None
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo desregistrar el observer de selección")
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar_inspector()
    def closeEvent(self, event):
        self.cerrar_inspector()
        super().closeEvent(event)
    @classmethod
    def mostrar_en_freecad(cls, parent=None):
        """Abre el inspector en FreeCAD GUI dentro de un QDockWidget lateral."""
        from freecad.vdo.ui.vdo_inspector_dock import obtener_o_crear_dock_inspector
        dock = obtener_o_crear_dock_inspector()
        if dock is not None:
            dock.show()
            dock.raise_()
            return dock.widget()
        instancia = cls(parent=parent)
        if Gui is not None and hasattr(Gui, "Control"):
            try:
                Gui.Control.showDialog(instancia)
            except Exception:
                instancia.show()
        else:
            instancia.show()
        return instancia


__all__ = [
    "VDOUniversalInspectorWidget",
]
