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
import os
if os.environ.get("QT_QPA_PLATFORM") is None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
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
from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import anadir_propiedad_texto, asignar_propiedades
from freecad.vdo.ui.inspector_cabecera import (
    _BreadcrumbBar,
    _CLAVE_BREADCRUMB_A_NIVEL,
    _MicroHeaderWidget,
    _RUTA_BREADCRUMB_DEFECTO,
    _RUTA_BREADCRUMB_POR_TARGET,
)
from freecad.vdo.ui.inspector_pagina_pieza import PaginaPieza
from freecad.vdo.ui.inspector_pagina_vano import PaginaVano
from freecad.vdo.ui.inspector_paginas import (
    PAGE_CHASIS,
    PAGE_CIERRE,
    PAGE_PIEZA,
    PAGE_VANO,
    PaginaChasis,
    PaginaCierre,
    _TARGET_TO_PAGE,
    _float_seguro,
)




class VDOUniversalInspectorWidget(QtWidgets.QWidget):
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
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Breadcrumbs
        self.breadcrumbs = _BreadcrumbBar(self)
        self.breadcrumbs.sigNivelClickeado.connect(self._on_breadcrumb_clicked)
        root.addWidget(self.breadcrumbs)

        # 2. Micro-Header editable
        self.micro_header = _MicroHeaderWidget(self)
        self.micro_header.sigDimensionesCambiadas.connect(self._on_dimensiones_header_cambiadas)
        root.addWidget(self.micro_header)

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

        # Proporción inicial del splitter (130px árbol : 230px stack)
        self.splitter.setSizes([130, 230])
        root.addWidget(self.splitter, 1)

        # Iniciar en nivel Chasis
        self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
    def _ir_a_nivel(self, page_index, target_type):
        if self.stack is None:
            return
        self.stack.setCurrentIndex(page_index)
        self._tipo_actual = target_type

        # Actualizar breadcrumbs
        ruta, activo = _RUTA_BREADCRUMB_POR_TARGET.get(
            target_type, _RUTA_BREADCRUMB_DEFECTO)
        self.breadcrumbs.set_ruta(list(ruta), activo=activo)

        self.sigNivelCambiado.emit(page_index, target_type)
    def _on_breadcrumb_clicked(self, clave):
        destino = _CLAVE_BREADCRUMB_A_NIVEL.get(clave)
        if destino is not None:
            self._ir_a_nivel(*destino)
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

        texto_div = getattr(obj, "VDO_Divisiones", "") or ""
        layout = Layout.loads(texto_div) if Layout is not None else None

        texto_reeng = getattr(obj, "VDO_Reengrose_JSON", "{}") or "{}"
        try:
            reengroses = json.loads(texto_reeng) if isinstance(texto_reeng, str) else dict(texto_reeng)
        except Exception:
            reengroses = {}

        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "{}") or "{}"
        try:
            contenido_por_celda = json.loads(texto_contenido) if isinstance(texto_contenido, str) else dict(texto_contenido)
        except Exception:
            contenido_por_celda = {}

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
        self._resolved_layout = resolved

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

        self._piezas_calculadas = piezas

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

        # 5. Regenerar Árbol Maestro
        self._regenerar_arbol_maestro(obj, piezas, resolved, contenido_por_celda)
    def _regenerar_arbol_maestro(self, obj, piezas, resolved, contenido_por_celda):
        self.master_tree.blockSignals(True)
        self.master_tree.clear()

        nombre_raiz = getattr(obj, "Label", getattr(obj, "Name", "COCO")) if obj else "COCO"
        raiz = QtWidgets.QTreeWidgetItem([f"📦 {nombre_raiz}"])
        raiz.setData(0, QtCore.Qt.UserRole, {"tipo": "coco", "obj": obj})
        self.master_tree.addTopLevelItem(raiz)

        # Rama 1: Chasis y Envolvente
        item_chasis = QtWidgets.QTreeWidgetItem(["🪵 Chasis y Envolvente"])
        item_chasis.setData(0, QtCore.Qt.UserRole, {"tipo": "chasis", "obj": obj})
        raiz.addChild(item_chasis)

        caras_chasis = [
            ("━━ Tapa Superior", "superior"),
            ("━━ Base Inferior", "inferior"),
            ("◀ Lateral Izquierdo", "izquierda"),
            ("Lateral Derecho ▶", "derecha"),
            ("▦ Fondo Trasero", "fondo"),
            ("⌸ Zócalo Base", "zocalo"),
        ]
        for nom, face_id in caras_chasis:
            it = QtWidgets.QTreeWidgetItem([nom])
            it.setData(0, QtCore.Qt.UserRole, {"tipo": "chasis_face", "face": face_id})
            item_chasis.addChild(it)

        # Rama 2: Piezas Físicas
        item_piezas = QtWidgets.QTreeWidgetItem(["🪵 Piezas Físicas"])
        item_piezas.setData(0, QtCore.Qt.UserRole, {"tipo": "piezas_header", "obj": obj})
        raiz.addChild(item_piezas)

        for p in piezas:
            it = QtWidgets.QTreeWidgetItem([f"🪵 {p['nombre']} [{p['largo']:.0f}×{p['ancho']:.0f}]"])
            it.setData(0, QtCore.Qt.UserRole, {"tipo": "pieza", "clave": p["key"], "pieza": p})
            item_piezas.addChild(it)

        # Rama 3: Vanos y Cavidades
        item_vanos = QtWidgets.QTreeWidgetItem(["🔲 Vanos y Cavidades"])
        item_vanos.setData(0, QtCore.Qt.UserRole, {"tipo": "vanos_header", "obj": obj})
        raiz.addChild(item_vanos)

        if resolved is not None:
            for cell in resolved.walk_cells():
                lbl = getattr(cell, "label", "(x1, y1)")
                it_cell = QtWidgets.QTreeWidgetItem([f"🔲 {lbl} [{cell.w:.0f}×{cell.h:.0f}]"])
                it_cell.setData(0, QtCore.Qt.UserRole, {"tipo": "vano", "label": lbl, "cell": cell})
                item_vanos.addChild(it_cell)

                # Insertos anidados bajo la celda
                ins_cfg = contenido_por_celda.get(lbl, {})
                tipo_ins = ins_cfg.get("tipo")
                if tipo_ins == "cajon":
                    it_ins = QtWidgets.QTreeWidgetItem([f"🗄️ Cajón ({ins_cfg.get('n_cajones', 1)}x)"])
                    it_ins.setData(0, QtCore.Qt.UserRole, {"tipo": "inserto_cajon", "cfg": ins_cfg, "cell": cell})
                    it_cell.addChild(it_ins)
                elif tipo_ins == "puerta":
                    it_ins = QtWidgets.QTreeWidgetItem([f"🚪 Puerta ({ins_cfg.get('sistema', 'Batiente')})"])
                    it_ins.setData(0, QtCore.Qt.UserRole, {"tipo": "inserto_puerta", "cfg": ins_cfg, "cell": cell})
                    it_cell.addChild(it_ins)

        raiz.setExpanded(True)
        item_chasis.setExpanded(True)
        item_vanos.setExpanded(True)
        self.master_tree.blockSignals(False)
    def _on_tree_item_clicked(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        if not data or not isinstance(data, dict):
            return

        tipo = data.get("tipo")
        if tipo in ("coco", "chasis", "chasis_face"):
            self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_COCO)
            if self.preview is not None:
                self.preview.set_selected(None)

        elif tipo == "pieza":
            p = data.get("pieza", {})
            self.pagina_pieza.cargar_pieza_dict(p)
            self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)
            if self.preview is not None:
                self.preview.set_selected_panel(p.get("key", ""))

        elif tipo == "piezas_header":
            self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)

        elif tipo == "vano":
            cell = data.get("cell")
            self.pagina_vano.cargar_vano_cell(cell, fondo=_float_seguro(getattr(self._obj_actual, "FondoModulo", 550.0)))
            self._ir_a_nivel(PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"))
            if self.preview is not None:
                self.preview.set_selected(data.get("label", ""))

        elif tipo in ("inserto_cajon", "inserto_puerta"):
            cfg = data.get("cfg", {})
            self.pagina_cierre.cargar_cierre_desde_config(tipo, cfg)
            self._ir_a_nivel(PAGE_CIERRE, "CAJON" if "cajon" in tipo else "PUERTA")
    # ------------------------------------------------------------------
    # Clics del Visor 2D (CocoPreview2D) -> Árbol y Páginas
    # ------------------------------------------------------------------
    def _on_preview_cell_clicked(self, label):
        self._seleccionar_item_en_arbol("label", label)
        if self._resolved_layout is not None:
            for cell in self._resolved_layout.walk_cells():
                if getattr(cell, "label", "") == label:
                    self.pagina_vano.cargar_vano_cell(cell, fondo=_float_seguro(getattr(self._obj_actual, "FondoModulo", 550.0)))
                    break
        self._ir_a_nivel(PAGE_VANO, getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"))
    def _on_preview_panel_clicked(self, clave):
        self._seleccionar_item_en_arbol("clave", clave)
        for p in self._piezas_calculadas:
            if p.get("key") == clave:
                self.pagina_pieza.cargar_pieza_dict(p)
                break
        self._ir_a_nivel(PAGE_PIEZA, VDOSelectionBridge.TARGET_PANEL)
    def _on_preview_reengrose_clicked(self, clave):
        self._on_preview_panel_clicked(clave)
    def _seleccionar_item_en_arbol(self, campo, valor):
        """Busca y selecciona el elemento en el QTreeWidget Maestro."""
        it = QtWidgets.QTreeWidgetItemIterator(self.master_tree)
        while it.value():
            item = it.value()
            data = item.data(0, QtCore.Qt.UserRole)
            if isinstance(data, dict) and data.get(campo) == valor:
                self.master_tree.blockSignals(True)
                self.master_tree.setCurrentItem(item)
                self.master_tree.blockSignals(False)
                return
            it += 1
    # ------------------------------------------------------------------
    # Ediciones de Usuario en MicroHeader y Páginas
    # ------------------------------------------------------------------
    def _on_dimensiones_header_cambiadas(self, w, h, d, e):
        obj = self._obj_actual
        if obj is not None:
            try:
                if hasattr(obj, "Ancho"):
                    asignar_propiedades(obj, {"Ancho": w})
                if hasattr(obj, "Alto"):
                    asignar_propiedades(obj, {"Alto": h})
                if hasattr(obj, "FondoModulo"):
                    asignar_propiedades(obj, {"FondoModulo": d})
                if hasattr(obj, "Espesor"):
                    try:
                        asignar_propiedades(obj, {"Espesor": e})
                    except TypeError:
                        asignar_propiedades(obj, {"Espesor": round(e)})
                doc = getattr(obj, "Document", None)
                if doc is not None:
                    recalcular(doc)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudieron actualizar las dimensiones del header")
        self._actualizar_vista_completa()
    def _on_habitante_vano_cambiado(self, tipo_hab, cfg):
        obj = self._obj_actual
        if obj is None or Layout is None:
            return

        def _guardar_prop(prop_name, prop_val):
            try:
                if hasattr(obj, prop_name):
                    asignar_propiedades(obj, {prop_name: prop_val})
                elif hasattr(obj, "addProperty"):
                    anadir_propiedad_texto(obj, prop_name, "VDO", prop_name)
                    asignar_propiedades(obj, {prop_name: prop_val})
            except Exception:
                App.Console.PrintWarning(
                    f"[VDO] No se pudo guardar propiedad {prop_name}")

        celda_lbl = cfg.get("celda", "(x1, y1)")
        texto_div = getattr(obj, "VDO_Divisiones", "") or ""
        layout = Layout.loads(texto_div)

        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "{}") or "{}"
        try:
            contenido = json.loads(texto_contenido) if isinstance(texto_contenido, str) else dict(texto_contenido)
        except Exception:
            contenido = {}

        if tipo_hab == "subdividir":
            cell = layout.find_label(celda_lbl)
            if cell is not None:
                layout.set_split(cell, cfg.get("eje", "Y"), int(cfg.get("n_partes", 2)))
                _guardar_prop("VDO_Divisiones", layout.dumps())
        elif tipo_hab == "cajon" or tipo_hab == "puerta":
            contenido[celda_lbl] = cfg
            _guardar_prop("VDO_Contenido_JSON", json.dumps(contenido))
        elif tipo_hab == "vacio":
            cell = layout.find_label(celda_lbl)
            if cell is not None:
                layout.disable_split(cell)
                _guardar_prop("VDO_Divisiones", layout.dumps())
            if celda_lbl in contenido:
                del contenido[celda_lbl]
                _guardar_prop("VDO_Contenido_JSON", json.dumps(contenido))

        try:
            doc = getattr(obj, "Document", None)
            if doc is not None:
                recalcular(doc)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo recomputar el documento")

        self._actualizar_vista_completa()
    # ------------------------------------------------------------------
    # Puente de selección nativa FreeCAD
    # ------------------------------------------------------------------
    def _inicializar_puente(self):
        self._puente = VDOSelectionBridge(
            on_target_changed=self._on_selection_changed)
        self._puente.attach()
    def _on_selection_changed(self, obj, target_type):
        """Reacción reactiva a un cambio de selección en FreeCAD."""
        try:
            self._obj_actual = obj
            self._tipo_actual = target_type

            if obj is None or target_type == VDOSelectionBridge.TARGET_UNKNOWN:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
                return

            page = _TARGET_TO_PAGE.get(target_type, PAGE_CHASIS)

            if page == PAGE_CHASIS and target_type == VDOSelectionBridge.TARGET_COCO:
                self.cargar_coco(obj)
            elif page == PAGE_PIEZA and target_type == VDOSelectionBridge.TARGET_PANEL:
                self.pagina_pieza.cargar_panel(obj)
            elif page == PAGE_CIERRE:
                self.pagina_cierre.cargar_cierre(obj, target_type)
            elif page == PAGE_VANO:
                self.pagina_vano.cargar_vano(obj)
            else:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
                return

            self._ir_a_nivel(page, target_type)

        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error navegando a nivel de página")
            try:
                self._ir_a_nivel(PAGE_CHASIS, VDOSelectionBridge.TARGET_UNKNOWN)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo navegar a la página de chasis")
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
