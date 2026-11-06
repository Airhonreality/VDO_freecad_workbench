"""Construccion de la interfaz del panel COCO."""

import json

import FreeCAD as App

from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import (
    anadir_propiedad_texto,
    asignar_propiedades,
)
from freecad.vdo.datos.formularios import (
    COCO_ANCLAJE,
    COCO_EXPOSICION,
    COCO_MEDIDAS,
    COCO_PESTANAS,
    COCO_ROTACION,
    COCO_ROTACION_PASOS,
)
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import tema
from freecad.vdo.ui.chassis_widget import VDOChassisControllerWidget
from freecad.vdo.ui.coco_construccion_widgets import DivisionesEditor
from freecad.vdo.ui.form_builder import FormBuilder


class CocoUnifiedConstruccionMixin:
    """Mixin del panel COCO: Construccion de la interfaz del panel COCO."""

    def _crear_widget(self):
        self.form_coco = FormBuilder(parent=self)
        widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(widget)

        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)
        # Pestañas en el orden y con el titulo de COCO_PESTANAS.
        pestanas = []
        for pestana in COCO_PESTANAS:
            tab = QtWidgets.QWidget()
            self._crear_contenido_pestana(pestana["clave"], tab)
            pestanas.append((tab, pestana["titulo"]))
        for tab, titulo in pestanas:
            self.tabs.addTab(tab, titulo)

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

    def _crear_contenido_pestana(self, clave, tab):
        """Rellena una pestaña de COCO_PESTANAS según su clave."""
        if clave == "medidas":
            self._crear_pestana_medidas(tab)
        elif clave == "estructura":
            self._crear_contenido_estructura(tab)
        elif clave == "divisiones":
            self._crear_contenido_divisiones(tab)
        else:
            raise ValueError(f"Pestaña COCO desconocida: {clave!r}")

    def _crear_pestana_medidas(self, tab_medidas):
        layout_medidas = QtWidgets.QVBoxLayout(tab_medidas)
        self._crear_grupo_medidas(layout_medidas)
        self._crear_grupo_coloc(layout_medidas)
        self._crear_grupo_exposicion(layout_medidas)

    def _crear_grupo_medidas(self, layout_medidas):
        titulo, filas = COCO_MEDIDAS
        self.form_coco.construir_grupo(layout_medidas, titulo, filas)
        self.spin_alto = self.form_coco.widget("alto")
        self.spin_ancho = self.form_coco.widget("ancho")
        self.spin_fondo = self.form_coco.widget("fondo_modulo")
        self.spin_espesor = self.form_coco.widget("espesor")

    def _crear_grupo_coloc(self, layout_medidas):
        # --- Colocación (pose, no geometría) ---
        grupo_coloc = QtWidgets.QGroupBox("Colocación")
        grid_coloc = QtWidgets.QGridLayout(grupo_coloc)

        grid_coloc.addWidget(QtWidgets.QLabel(COCO_ROTACION["etiqueta"]), 0, 0)
        layout_rot = QtWidgets.QHBoxLayout()
        self.spin_rotacion = self.form_coco.crear(COCO_ROTACION)
        layout_rot.addWidget(self.spin_rotacion)
        for paso in COCO_ROTACION_PASOS:
            layout_rot.addWidget(self._crear_boton_giro(paso))
        grid_coloc.addLayout(layout_rot, 0, 1)

        self.form_coco.construir_celda(grid_coloc, 1, 0, COCO_ANCLAJE)
        self.combo_anclaje = self.form_coco.widget("anclaje")

        layout_medidas.addWidget(grupo_coloc)

    def _crear_boton_giro(self, paso):
        """Boton de giro de 90 grados, desde COCO_ROTACION_PASOS."""
        boton = QtWidgets.QPushButton(paso["texto"])
        boton.setMaximumWidth(50)
        boton.setToolTip(paso["tooltip"])

        def _girar(*_args, delta=paso["delta"]):
            self.spin_rotacion.setValue(self.spin_rotacion.value() + delta)

        boton.clicked.connect(_girar)
        return boton

    def _crear_grupo_exposicion(self, layout_medidas):
        grupo_exp = QtWidgets.QGroupBox("Exposición")
        grid_exp = QtWidgets.QGridLayout(grupo_exp)
        self.combos_exposicion = {}
        for i, (lado, espec) in enumerate(COCO_EXPOSICION):
            fila = i // 2
            col = (i % 2) * 2
            self.form_coco.construir_celda(grid_exp, fila, col, espec)
            self.combos_exposicion[lado] = self.form_coco.widget(espec["clave"])
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
        tema.aplicar_estilo(self.lbl_resumen, tema.ESTILO_RESUMEN_CLARO)
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
