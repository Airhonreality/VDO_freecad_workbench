"""Construccion de la interfaz del panel COCO."""

import json
import FreeCAD as App

from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import (
    anadir_propiedad_texto,
    asignar_propiedades,
)
from freecad.vdo.core import vdo_frames as VDO_FR
from freecad.vdo.core.vdo_module_props import ANCLAJE_LABELS, ANCLAJES
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.vdo_chassis_widget import VDOChassisControllerWidget
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox
from freecad.vdo.ui.coco_construccion_widgets import DivisionesEditor


LADOS_EXPOSICION = (
    (VDO_FR.FRENTE, "Frente"),
    (VDO_FR.FONDO, "Fondo"),
    (VDO_FR.IZQUIERDA, "Izquierda"),
    (VDO_FR.DERECHA, "Derecha"),
    (VDO_FR.SUPERIOR, "Superior"),
    (VDO_FR.INFERIOR, "Inferior"),
)
ESTADOS_EXPOSICION = (
    ("oculto", "Oculto"),
    ("visto", "Visto"),
    ("apoyado", "Apoyado"),
)


class CocoUnifiedConstruccionMixin:
    """Mixin del panel COCO: Construccion de la interfaz del panel COCO."""

    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(widget)

        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Tab 1: Medidas Generales ---
        tab_medidas = QtWidgets.QWidget()
        layout_medidas = QtWidgets.QVBoxLayout(tab_medidas)

        self._crear_grupo_medidas(layout_medidas)
        self._crear_grupo_coloc(layout_medidas)
        self._crear_grupo_exposicion(layout_medidas)

        # --- Tab 2: Estructura / Chasis (Corte Transversal 2D Gestalt) ---
        tab_estructura = QtWidgets.QWidget()
        self._crear_contenido_estructura(tab_estructura)

        # --- Tab 3: Divisiones (matriz de vanos + preview 2D) ---
        tab_divisiones = QtWidgets.QWidget()
        self._crear_contenido_divisiones(tab_divisiones)

        self.tabs.addTab(tab_medidas, "Medidas")
        self.tabs.addTab(tab_estructura, "Estructura")
        self.tabs.addTab(tab_divisiones, "Divisiones")

        self._crear_grupo_resumen(main_layout)

        main_layout.addStretch()

        botones = QtWidgets.QDialogButtonBox()
        texto_ok = ("Crear y colocar" if not self.auto_transaction
                    else "Aplicar")
        btn_ok = botones.addButton(
            texto_ok, QtWidgets.QDialogButtonBox.AcceptRole)
        btn_cancelar = botones.addButton(
            "Cancelar", QtWidgets.QDialogButtonBox.RejectRole)
        botones.accepted.connect(self._on_ok)
        botones.rejected.connect(self._on_cancel)
        btn_ok.setToolTip(
            "Aplica medidas, estructura, divisiones y colocación del COCO.")
        btn_cancelar.setToolTip("Cierra sin aplicar los cambios.")
        main_layout.addWidget(botones)

        # El resumen sigue los valores de la UI, no las propiedades viejas.
        for spin in [self.spin_alto, self.spin_ancho,
                     self.spin_fondo, self.spin_espesor]:
            spin.valueChanged.connect(self._on_medida_changed)

        return widget
    def _crear_grupo_medidas(self, layout_medidas):
        grupo_medidas = QtWidgets.QGroupBox("Medidas Generales")
        grid_medidas = QtWidgets.QGridLayout(grupo_medidas)

        grid_medidas.addWidget(QtWidgets.QLabel("Alto (mm):"), 0, 0)
        self.spin_alto = VDO_DoubleSpinBox()
        self.spin_alto.setRange(1, 3000)
        self.spin_alto.setSuffix(" mm")
        self.spin_alto.setDecimals(1)
        self.spin_alto.setToolTip(
            "Alto exterior total del mueble, de piso a techo, incluyendo "
            "tapa y base.")
        grid_medidas.addWidget(self.spin_alto, 0, 1)

        grid_medidas.addWidget(QtWidgets.QLabel("Ancho (mm):"), 1, 0)
        self.spin_ancho = VDO_DoubleSpinBox()
        self.spin_ancho.setRange(1, 3000)
        self.spin_ancho.setSuffix(" mm")
        self.spin_ancho.setDecimals(1)
        self.spin_ancho.setToolTip(
            "Ancho exterior total del mueble, de lateral a lateral.")
        grid_medidas.addWidget(self.spin_ancho, 1, 1)

        grid_medidas.addWidget(QtWidgets.QLabel("Fondo módulo (mm):"), 2, 0)
        self.spin_fondo = VDO_DoubleSpinBox()
        self.spin_fondo.setRange(1, 1500)
        self.spin_fondo.setSuffix(" mm")
        self.spin_fondo.setDecimals(1)
        self.spin_fondo.setToolTip(
            "Profundidad exterior del mueble, desde el frente hasta el fondo.")
        grid_medidas.addWidget(self.spin_fondo, 2, 1)

        grid_medidas.addWidget(QtWidgets.QLabel("Espesor (mm):"), 3, 0)
        self.spin_espesor = QtWidgets.QSpinBox()
        self.spin_espesor.setRange(1, 50)
        self.spin_espesor.setSuffix(" mm")
        self.spin_espesor.setToolTip(
            "Espesor del tablero de laterales, base, techo y divisiones.")
        grid_medidas.addWidget(self.spin_espesor, 3, 1)

        layout_medidas.addWidget(grupo_medidas)

    def _crear_grupo_coloc(self, layout_medidas):
        # --- Colocación (pose, no geometría) ---
        grupo_coloc = QtWidgets.QGroupBox("Colocación")
        grid_coloc = QtWidgets.QGridLayout(grupo_coloc)

        grid_coloc.addWidget(QtWidgets.QLabel("Rotación Z:"), 0, 0)
        layout_rot = QtWidgets.QHBoxLayout()
        self.spin_rotacion = VDO_DoubleSpinBox()
        self.spin_rotacion.setRange(-360.0, 360.0)
        self.spin_rotacion.setDecimals(1)
        self.spin_rotacion.setSuffix(" °")
        self.spin_rotacion.setWrapping(True)
        self.spin_rotacion.setToolTip(
            "Rotación de colocación alrededor de Z. No cambia las medidas "
            "del mueble.")
        layout_rot.addWidget(self.spin_rotacion)
        btn_rot_menos = QtWidgets.QPushButton("-90°")
        btn_rot_menos.setMaximumWidth(50)
        btn_rot_menos.setToolTip(
            "Gira el mueble 90° en sentido horario.")
        btn_rot_menos.clicked.connect(
            lambda: self.spin_rotacion.setValue(
                self.spin_rotacion.value() - 90.0))
        layout_rot.addWidget(btn_rot_menos)
        btn_rot_mas = QtWidgets.QPushButton("+90°")
        btn_rot_mas.setMaximumWidth(50)
        btn_rot_mas.setToolTip(
            "Gira el mueble 90° en sentido antihorario.")
        btn_rot_mas.clicked.connect(
            lambda: self.spin_rotacion.setValue(
                self.spin_rotacion.value() + 90.0))
        layout_rot.addWidget(btn_rot_mas)
        grid_coloc.addLayout(layout_rot, 0, 1)

        grid_coloc.addWidget(QtWidgets.QLabel("Anclaje:"), 1, 0)
        self.combo_anclaje = QtWidgets.QComboBox()
        for anclaje in ANCLAJES:
            self.combo_anclaje.addItem(
                ANCLAJE_LABELS.get(anclaje, anclaje), anclaje)
        self.combo_anclaje.setToolTip(
            "Esquina del mueble que se apoya en el punto de colocación.")
        grid_coloc.addWidget(self.combo_anclaje, 1, 1)

        layout_medidas.addWidget(grupo_coloc)

    def _crear_grupo_exposicion(self, layout_medidas):
        grupo_exp = QtWidgets.QGroupBox("Exposición")
        grid_exp = QtWidgets.QGridLayout(grupo_exp)
        self.combos_exposicion = {}
        for i, (lado, label) in enumerate(LADOS_EXPOSICION):
            fila = i // 2
            col = (i % 2) * 2
            grid_exp.addWidget(QtWidgets.QLabel(f"{label}:"), fila, col)
            combo = QtWidgets.QComboBox()
            for codigo, texto in ESTADOS_EXPOSICION:
                combo.addItem(texto, codigo)
            combo.setToolTip(
                "Visto: cara exterior visible. Apoyado: contra muro/piso. "
                "Oculto: sin exposición.")
            self.combos_exposicion[lado] = combo
            grid_exp.addWidget(combo, fila, col + 1)
        layout_medidas.addWidget(grupo_exp)

    def _crear_contenido_estructura(self, tab_estructura):
        layout_estructura = QtWidgets.QVBoxLayout(tab_estructura)
        layout_estructura.setContentsMargins(0, 0, 0, 0)

        scroll_est = QtWidgets.QScrollArea()
        scroll_est.setWidgetResizable(True)
        scroll_est.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.box_chassis = VDOChassisControllerWidget()
        self.box_chassis.sigChassisChanged.connect(self._on_chassis_changed)
        scroll_est.setWidget(self.box_chassis)

        layout_estructura.addWidget(scroll_est)

    def _crear_contenido_divisiones(self, tab_divisiones):
        layout_divisiones = QtWidgets.QVBoxLayout(tab_divisiones)
        self.editor_divisiones = DivisionesEditor()
        self.editor_divisiones.changed.connect(self._on_divisiones_changed)
        layout_divisiones.addWidget(self.editor_divisiones)

    def _crear_grupo_resumen(self, main_layout):
        # Resumen global
        grupo_resumen = QtWidgets.QGroupBox("Resumen Completo")
        layout_resumen = QtWidgets.QVBoxLayout(grupo_resumen)
        self.lbl_resumen = QtWidgets.QLabel("Sin configurar.")
        self.lbl_resumen.setWordWrap(True)
        self.lbl_resumen.setStyleSheet(
            "QLabel { background-color: #f0f0f0; padding: 8px; "
            "border: 1px solid #ccc; font-family: monospace; }")
        layout_resumen.addWidget(self.lbl_resumen)
        main_layout.addWidget(grupo_resumen)


    def _on_chassis_changed(self, cfg):
        """Reacciona al cambio interactivo en el chasis 2D y actualiza el objeto."""
        if getattr(self, "_building", False):
            return
        if self.obj is not None:
            enc_sup = cfg.get("encuentros", {}).get("superior_izq", "tapa_domina")
            tapa_val = "externo" if enc_sup == "tapa_domina" else "interno"
            if hasattr(self.obj, "Tapa"):
                asignar_propiedades(self.obj, {"Tapa": tapa_val})

            enc_inf = cfg.get("encuentros", {}).get("inferior_izq", "lateral_domina")
            base_val = "externo" if enc_inf == "base_domina" else "interno"
            if hasattr(self.obj, "Base"):
                asignar_propiedades(self.obj, {"Base": base_val})

            fondo_act = cfg.get("caras", {}).get("fondo", {}).get("activa", True)
            if hasattr(self.obj, "TieneFondo"):
                asignar_propiedades(self.obj, {"TieneFondo": bool(fondo_act)})

            base_info = cfg.get("base", {})
            if "altura" in base_info and hasattr(self.obj, "AltoZocalo"):
                try:
                    asignar_propiedades(self.obj, {"AltoZocalo": float(base_info["altura"])})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo establecer AltoZocalo")
            if "separacion_frente" in base_info and hasattr(self.obj, "DistanciaFrente"):
                try:
                    asignar_propiedades(self.obj, {"DistanciaFrente": float(base_info["separacion_frente"])})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo establecer DistanciaFrente")

            try:
                if hasattr(self.obj, "VDO_Chassis_JSON"):
                    asignar_propiedades(self.obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
                elif hasattr(self.obj, "addProperty"):
                    anadir_propiedad_texto(self.obj, "VDO_Chassis_JSON", "VDO",
                                           "Configuración semiótica de Capa 1")
                    asignar_propiedades(self.obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo guardar VDO_Chassis_JSON")

            doc = getattr(self.obj, "Document", None)
            if doc is not None:
                try:
                    recalcular(doc)
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo recomputar el documento")
        self._actualizar_resumen()
