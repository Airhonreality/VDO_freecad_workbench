# =====================================================================
# vdo_zocalo_task.py
# Task Panel PySide del zócalo paramétrico VDO.
# =====================================================================

import FreeCAD as App

from freecad.vdo.cad.propiedades import aplicar_rotacion
from freecad.vdo.core import vdo_module_props
from freecad.vdo.core.vdo_module_props import (
    ANCLAJE_DEFAULT,
    ANCLAJE_LABELS,
    ANCLAJES,
)
from freecad.vdo.cad.propiedades import add_common_props
from freecad.vdo.core.vdo_zocalo_core import ZocaloError, calcular_geometria_zocalo
from freecad.vdo.qt_compat import QtGui, QtWidgets
from freecad.vdo.ui.vdo_form_builder import FormBuilder
from freecad.vdo.ui.vdo_task_base import VDOTransactionMixin, cerrar_dialogo
from freecad.vdo.ui.vdo_widgets_coco import PanelHeaderWidget

CANTOS_FRENTE = {
    "norte": "RIG", "sur": "RIG", "este": "RIG", "oeste": "RIG"}


class ZocaloTaskPanel(VDOTransactionMixin):
    """Panel de tareas para editar un zócalo."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self.obj = obj
        self._vdo_aceptado = False
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name="Editar zócalo",
        )
        self.form = self._crear_widget()
        if obj:
            add_common_props(obj)
            self._cargar_valores(obj)
        self._actualizar_header()

    # -----------------------------------------------------------------
    def _crear_widget(self):
        widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(widget)

        self.header = PanelHeaderWidget()
        main_layout.addWidget(self.header)

        self._form_builder = FormBuilder(widget)

        grupo_dim = QtWidgets.QGroupBox("Dimensiones del mueble")
        grid_dim = QtWidgets.QGridLayout(grupo_dim)

        self.spin_ancho = self._campo(grid_dim, 0, "Ancho (mm):",
                                      "ancho", "double_spin", (1, 4000), 1,
                                      " mm",
                                      "Ancho total del mueble; define el "
                                      "largo de la tira frontal.")
        self.spin_fondo = self._campo(grid_dim, 1, "Fondo (mm):",
                                      "fondo", "double_spin", (1, 2000), 1,
                                      " mm",
                                      "Fondo total del mueble; limita el "
                                      "largo de los laterales.")
        self.spin_alto = self._campo(grid_dim, 2, "Alto zócalo (mm):",
                                     "alto", "double_spin", (1, 400), 1,
                                     " mm",
                                     "Altura física del zócalo (por ejemplo "
                                     "100 o 120 mm).")
        self.spin_espesor = self._campo(grid_dim, 3, "Espesor tablero (mm):",
                                        "espesor", "spin", (1, 40), None,
                                        " mm",
                                        "Espesor de las tiras de melamina "
                                        "del zócalo.")

        main_layout.addWidget(grupo_dim)

        grupo_sep = QtWidgets.QGroupBox("Separación y encuentros")
        grid_sep = QtWidgets.QGridLayout(grupo_sep)

        self.spin_frente = self._campo(grid_sep, 0, "Separación frontal:",
                                       "frente", "double_spin", (0, 500), 1,
                                       " mm",
                                       "Distancia desde el frente del mueble "
                                       "hacia adentro. Deja espacio libre "
                                       "para no golpear los pies.")
        self.spin_costados = self._campo(grid_sep, 1, "Distancia costados:",
                                         "costados", "double_spin", (0, 500),
                                         1, " mm",
                                         "Separación desde cada costado del "
                                         "mueble (0 = al ras).")
        self.spin_trasera = self._campo(grid_sep, 2, "Distancia trasera:",
                                        "trasera", "double_spin", (0, 500),
                                        1, " mm",
                                        "Separación desde el fondo del mueble "
                                        "para librar el rodapié de la pared.")
        self.chk_trasera = self._campo(grid_sep, 3, "Tiene trasera",
                                       "trasera_habilitada", "checkbox",
                                       None, None, None,
                                       "Cierra el cajón del zócalo por "
                                       "detrás.", fila=3, colspan=2)

        main_layout.addWidget(grupo_sep)

        grupo_est = QtWidgets.QGroupBox("Estructura")
        grid_est = QtWidgets.QGridLayout(grupo_est)

        self.spin_amarres = self._campo(grid_est, 0, "Divisiones interiores:",
                                        "amarres", "spin", (0, 20), None, None,
                                        "Partes iguales del hueco interior "
                                        "entre frente y trasera. Se resuelven "
                                        "con el motor de división de vanos "
                                        "(vdo_layout).")

        main_layout.addWidget(grupo_est)

        grupo_coloc = QtWidgets.QGroupBox("Colocación")
        grid_coloc = QtWidgets.QGridLayout(grupo_coloc)

        self.spin_rotacion = self._campo(grid_coloc, 0, "Rotación Z:",
                                         "rotacion", "double_spin",
                                         (-360.0, 360.0), 1, " °",
                                         "Rotación de colocación alrededor "
                                         "de Z. No cambia la geometría.",
                                         wrapping=True)

        grid_coloc.addWidget(QtWidgets.QLabel("Anclaje:"), 1, 0)
        self.combo_anclaje = QtWidgets.QComboBox()
        for anclaje in ANCLAJES:
            self.combo_anclaje.addItem(
                ANCLAJE_LABELS.get(anclaje, anclaje), anclaje)
        self.combo_anclaje.setToolTip(
            "Esquina del zócalo que se apoya en el punto de colocación.")
        grid_coloc.addWidget(self.combo_anclaje, 1, 1)

        main_layout.addWidget(grupo_coloc)
        main_layout.addStretch()

        botones = QtWidgets.QDialogButtonBox()
        btn_ok = botones.addButton(
            "Crear y colocar" if not self.auto_transaction else "Aplicar",
            QtWidgets.QDialogButtonBox.AcceptRole)
        btn_cancelar = botones.addButton(
            "Cancelar", QtWidgets.QDialogButtonBox.RejectRole)
        botones.accepted.connect(self._on_ok)
        botones.rejected.connect(self._on_cancel)
        btn_ok.setToolTip(
            "Guarda los cambios del zócalo y recalcula la geometría.")
        btn_cancelar.setToolTip("Cierra sin aplicar los cambios.")
        main_layout.addWidget(botones)

        for senal in (
                self.spin_ancho.valueChanged,
                self.spin_fondo.valueChanged,
                self.spin_alto.valueChanged,
                self.spin_espesor.valueChanged,
                self.spin_frente.valueChanged,
                self.spin_costados.valueChanged,
                self.spin_trasera.valueChanged):
            senal.connect(self._actualizar_header)
        self.chk_trasera.toggled.connect(self._on_trasera)
        self.chk_trasera.toggled.connect(self._actualizar_header)
        self.chk_trasera.setChecked(True)

        return widget

    def _campo(self, grid, fila, etiqueta, clave, tipo, rango=None,
               decimales=None, sufijo=None, tooltip=None, wrapping=False,
               fila_check=None, colspan=1):
        """Añade un campo al builder y lo coloca en el grid del grupo."""
        espec = {
            "tipo": tipo,
            "etiqueta": etiqueta,
            "clave": clave,
            "valor_defecto": self._valor_defecto(clave, tipo),
            "rango": rango,
            "decimales": decimales,
            "sufijo": sufijo,
            "tooltip": tooltip,
        }
        if tipo == "combo":
            espec["items"] = [
                (ANCLAJE_LABELS.get(a, a), a) for a in ANCLAJES]
        campo = self._form_builder.agregar(espec)
        w = campo.crear_widget()
        if wrapping and tipo == "double_spin":
            w.setWrapping(True)
        if tipo == "checkbox":
            grid.addWidget(QtWidgets.QLabel(etiqueta), fila_check, 0)
            grid.addWidget(w, fila_check, 1, 1, colspan)
        elif tipo == "combo":
            grid.addWidget(QtWidgets.QLabel(etiqueta), fila, 0)
            grid.addWidget(w, fila, 1)
        else:
            grid.addWidget(QtWidgets.QLabel(etiqueta), fila, 0)
            grid.addWidget(w, fila, 1)
        return w

    @staticmethod
    def _valor_defecto(clave, tipo):
        defectos = {
            "ancho": 600.0, "fondo": 580.0, "alto": 120.0, "espesor": 18,
            "frente": 0.0, "costados": 0.0, "trasera": 0.0,
            "amarres": 0, "rotacion": 0.0, "trasera_habilitada": True,
        }
        valor = defectos.get(clave, 0.0)
        if tipo == "spin":
            return int(valor)
        return valor

    # -----------------------------------------------------------------
    def _on_trasera(self, activo):
        self.spin_trasera.setEnabled(bool(activo))

    def _actualizar_header(self, *_args):
        ancho = self.spin_ancho.value()
        alto = self.spin_alto.value()
        espesor = float(self.spin_espesor.value())
        self.header.set_panel(
            "Zocalo_Frente", ancho, alto, espesor, CANTOS_FRENTE)

    def _cargar_valores(self, obj):
        if hasattr(obj, "Ancho"):
            self.spin_ancho.setValue(float(obj.Ancho))
        if hasattr(obj, "Fondo"):
            self.spin_fondo.setValue(float(obj.Fondo))
        if hasattr(obj, "AltoZocalo"):
            self.spin_alto.setValue(float(obj.AltoZocalo))
        if hasattr(obj, "EspesorTablero"):
            self.spin_espesor.setValue(
                round(float(obj.EspesorTablero)))
        if hasattr(obj, "DistanciaFrente"):
            self.spin_frente.setValue(float(obj.DistanciaFrente))
        if hasattr(obj, "DistanciaCostados"):
            self.spin_costados.setValue(float(obj.DistanciaCostados))
        if hasattr(obj, "DistanciaTrasera"):
            self.spin_trasera.setValue(float(obj.DistanciaTrasera))
        if hasattr(obj, "TieneTrasera"):
            self.chk_trasera.setChecked(bool(obj.TieneTrasera))
        if hasattr(obj, "AmarresIntermedios"):
            self.spin_amarres.setValue(int(obj.AmarresIntermedios))
        self.spin_rotacion.setValue(
            float(getattr(obj, "VDO_RotacionZ", 0.0)))
        anclaje = getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

    # -----------------------------------------------------------------
    def _on_ok(self):
        if self.accept():
            cerrar_dialogo()

    def _on_cancel(self):
        self.reject()
        cerrar_dialogo()

    def accept(self):
        if not self.obj:
            return True
        try:
            self._vdo_begin()
            for spin in (
                    self.spin_ancho, self.spin_fondo, self.spin_alto,
                    self.spin_frente, self.spin_costados,
                    self.spin_trasera, self.spin_rotacion):
                spin.interpretText()
            self.spin_espesor.interpretText()
            self.spin_amarres.interpretText()

            calcular_geometria_zocalo(
                self.spin_ancho.value(),
                self.spin_fondo.value(),
                self.spin_alto.value(),
                self.spin_espesor.value(),
                self.spin_frente.value(),
                self.spin_costados.value(),
                self.spin_trasera.value(),
                self.chk_trasera.isChecked(),
                self.spin_amarres.value(),
            )

            self.obj.Ancho = self.spin_ancho.value()
            self.obj.Fondo = self.spin_fondo.value()
            self.obj.AltoZocalo = self.spin_alto.value()
            self.obj.EspesorTablero = self.spin_espesor.value()
            self.obj.DistanciaFrente = self.spin_frente.value()
            self.obj.DistanciaCostados = self.spin_costados.value()
            self.obj.DistanciaTrasera = self.spin_trasera.value()
            self.obj.TieneTrasera = self.chk_trasera.isChecked()
            self.obj.AmarresIntermedios = self.spin_amarres.value()
            anclaje = self.combo_anclaje.currentData()
            if anclaje:
                self.obj.VDO_Anclaje = anclaje
            aplicar_rotacion(self.obj, self.spin_rotacion.value())
            App.ActiveDocument.recompute()
            self._vdo_commit()
            self._vdo_aceptado = True
            self._vdo_call_accept()
            return True
        except ZocaloError as exc:
            self._vdo_abort()
            QtWidgets.QMessageBox.warning(
                self.form, "Zócalo", str(exc))
            return False
        except Exception as exc:
            self._vdo_abort()
            App.Console.PrintError(
                f"[VDO] Error aceptando el zócalo: {exc}\n")
            return False

