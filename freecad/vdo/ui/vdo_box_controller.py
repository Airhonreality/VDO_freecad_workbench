"""
vdo_box_controller.py

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

from freecad.vdo.core import (
    vdo_reengrose_modelo as VDO_RE_MODELO,
    vdo_reengrose_modificador as VDO_RE_MODIFICADOR,
)
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets

from freecad.vdo.ui.box_constantes import (
    ENCUENTRO_LABELS,
    ENCUENTRO_TOOLTIPS,
    ESQUINAS,
    TIPOS_ENCUENTRO,
    _TEXTO_BOTON_BORDE,
    obtener_svg_icon,
)
from freecad.vdo.ui.box_construccion import BoxConstruccionMixin
from freecad.vdo.ui.box_hoja_estilos import ESTILO_WIDGET

_LOG = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Widget Principal VDOBoxControllerWidget
# ----------------------------------------------------------------------
class VDOBoxControllerWidget(
    BoxConstruccionMixin,
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
        self.setStyleSheet(ESTILO_WIDGET)

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

    # ------------------------------------------------------------------
    # Lógica de Interacción (State Machine y Poka-Yoke)
    # ------------------------------------------------------------------
    def _on_activo_toggled(self, activo):
        if self._cargando:
            return
        if activo and not self._hay_bordes_activos():
            self._cargando = True
            self.btn_borde["frente"].setChecked(True)
            self._cargando = False
        self._actualizar_estado_habilitacion()
        self._actualizar_estado_all()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _hay_bordes_activos(self):
        return any(self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D)

    def _on_all_clicked(self):
        if self._cargando:
            return
        activos_actuales = sum(1 for b in VDO_RE_MODELO.BORDES_2D if self.btn_borde[b].isChecked())
        nuevo_estado = (activos_actuales < len(VDO_RE_MODELO.BORDES_2D))

        self._cargando = True
        for b in VDO_RE_MODELO.BORDES_2D:
            self.btn_borde[b].setChecked(nuevo_estado)
        self.btn_all.setChecked(nuevo_estado)
        if nuevo_estado and not self.chk_activo.isChecked():
            self.chk_activo.setChecked(True)
        self._cargando = False

        self._actualizar_estado_habilitacion()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_borde_clicked(self, borde):
        if self._cargando:
            return
        self._seleccionar_margen(borde)
        if self.btn_borde[borde].isChecked() and not self.chk_activo.isChecked():
            self._cargando = True
            self.chk_activo.setChecked(True)
            self._cargando = False
        self._actualizar_estado_all()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _seleccionar_margen(self, margen):
        self._margen_seleccionado = margen
        self._borde_seleccionado = margen

        # Actualizar estilo de chips de margen
        for b, btn in self.btn_margenes.items():
            btn.blockSignals(True)
            btn.setChecked(b == margen)
            btn.blockSignals(False)

        # Actualizar etiquetas de botones de borde
        for b, btn in self.btn_borde.items():
            btn.setProperty("selected", "true" if b == margen else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.lbl_margen_tag.setText(f"Margen: <b>{margen.upper()}</b>")

        # Cargar valores en los spinboxes principales si estamos en modo individual
        if not self.btn_centro.isChecked():
            self._cargando = True
            w = self._valores_bordes[margen]["ancho"]
            d = self._valores_bordes[margen]["offset"]
            self.spin_ancho.setValue(w)
            self.spin_offset.setValue(d)
            self._cargando = False

        self._actualizar_canvas_concentrico()

    def _aplicar_chip_offset(self, val):
        self.spin_offset.setValue(float(val))

    def _on_spin_ancho_changed(self):
        if self._cargando:
            return
        w = self.spin_ancho.value()
        if self.btn_centro.isChecked():
            # Uniforme: replicar a todos los bordes
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["ancho"] = w
                self.spin_ancho_borde[b].setValue(w)
        else:
            # Individual: aplicar solo al margen seleccionado
            m = self._margen_seleccionado
            self._valores_bordes[m]["ancho"] = w
            self.spin_ancho_borde[m].setValue(w)

        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_spin_offset_changed(self):
        if self._cargando:
            return
        d = self.spin_offset.value()
        if self.btn_centro.isChecked():
            # Uniforme: replicar a todos los bordes
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["offset"] = d
                self.spin_offset_borde[b].setValue(d)
        else:
            # Individual: aplicar solo al margen seleccionado
            m = self._margen_seleccionado
            self._valores_bordes[m]["offset"] = d
            self.spin_offset_borde[m].setValue(d)

        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_uniforme_toggled(self):
        if self._cargando:
            return
        uniforme = self.btn_centro.isChecked()
        self._cargando = True
        if uniforme:
            self.btn_centro.setText(" Uniforme")
            self.btn_centro.setIcon(obtener_svg_icon("link"))
            ancho_u = self.spin_ancho.value()
            dist_u = self.spin_offset.value()
            for b in VDO_RE_MODELO.BORDES_2D:
                self._valores_bordes[b]["ancho"] = ancho_u
                self._valores_bordes[b]["offset"] = dist_u
                self.spin_ancho_borde[b].setValue(ancho_u)
                self.spin_offset_borde[b].setValue(dist_u)
        else:
            self.btn_centro.setText(" Individual")
            self.btn_centro.setIcon(obtener_svg_icon("unlink"))
            m = self._margen_seleccionado
            self.spin_ancho.setValue(self._valores_bordes[m]["ancho"])
            self.spin_offset.setValue(self._valores_bordes[m]["offset"])

        self._cargando = False
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _actualizar_estado_all(self):
        todos = all(self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D)
        self.btn_all.blockSignals(True)
        self.btn_all.setChecked(todos)
        self.btn_all.blockSignals(False)

    def _actualizar_canvas_concentrico(self):
        activos = {b: self.btn_borde[b].isChecked() for b in VDO_RE_MODELO.BORDES_2D}
        self.canvas_concentrico.actualizar(
            activos, self._valores_bordes, self._esquinas, self._margen_seleccionado)

        # Actualizar texto explicativo en los 4 botones de borde
        for b in VDO_RE_MODELO.BORDES_2D:
            btn = self.btn_borde[b]
            w = self._valores_bordes[b]["ancho"]
            d = self._valores_bordes[b]["offset"]
            texto_offset = "0 mm (ras)" if d == 0.0 else f"⇥ {d:.0f} mm"

            plantilla = _TEXTO_BOTON_BORDE.get(b)
            if plantilla is not None:
                btn.setText(plantilla(w, texto_offset))

    def _on_esquina_clicked(self, esquina):
        if self._cargando:
            return
        esquina = {
            "no": "fondo_izquierda", "ne": "fondo_derecha",
            "so": "frente_izquierda", "se": "frente_derecha"
        }.get(esquina.lower(), esquina)
        actual = self._esquinas[esquina]
        idx = (TIPOS_ENCUENTRO.index(actual) + 1) % len(TIPOS_ENCUENTRO)
        nuevo_tipo = TIPOS_ENCUENTRO[idx]

        self._cargando = True
        self.combo_esquina[esquina].blockSignals(True)
        idx_c = self.combo_esquina[esquina].findData(nuevo_tipo)
        if idx_c >= 0:
            self.combo_esquina[esquina].setCurrentIndex(idx_c)
        self.combo_esquina[esquina].blockSignals(False)
        self._cargando = False

        self._on_combo_esquina_changed(esquina)

    def _on_combo_esquina_changed(self, esquina):
        if self._cargando:
            return
        esquina = {
            "no": "fondo_izquierda", "ne": "fondo_derecha",
            "so": "frente_izquierda", "se": "frente_derecha"
        }.get(esquina.lower(), esquina)
        tipo = self.combo_esquina[esquina].currentData()
        if not tipo:
            return
        self._esquinas[esquina] = tipo

        if self.chk_sync_esquinas.isChecked():
            self._cargando = True
            for e in ESQUINAS:
                if e != esquina:
                    self._esquinas[e] = tipo
                    self._set_combo_silencioso(self.combo_esquina[e], tipo)
            self._cargando = False

        self._actualizar_iconos_esquinas()
        self._actualizar_canvas_concentrico()
        self._emitir_cambio()

    def _on_sync_esquinas_toggled(self, activo):
        if self._cargando:
            return
        if activo:
            tipo = self._esquinas["frente_izquierda"]
            self._cargando = True
            for e in ESQUINAS:
                self._esquinas[e] = tipo
                self._set_combo_silencioso(self.combo_esquina[e], tipo)
            self._cargando = False
            self._actualizar_iconos_esquinas()
            self._actualizar_canvas_concentrico()
            self._emitir_cambio()

    def _actualizar_iconos_esquinas(self):
        for e in ESQUINAS:
            tipo = self._esquinas[e]
            btn = self.btn_esquina[e]
            btn.setIcon(obtener_svg_icon(tipo, 20))
            btn.setToolTip(f"Esquina {e}:\n{ENCUENTRO_TOOLTIPS.get(tipo, tipo)}")

    def _actualizar_estado_habilitacion(self):
        activo = self.chk_activo.isChecked()
        self.container_canvas.setEnabled(activo)
        self.btn_all.setEnabled(activo)
        self.chk_sync_esquinas.setEnabled(activo)
        self.panel_medidas.setEnabled(activo)

    def _actualizar_estado(self):
        """Alias retrocompatible."""
        self._actualizar_estado_habilitacion()

    @staticmethod
    def _set_combo_data(combo, valor):
        """Establece el valor de un QComboBox buscando en su userData."""
        idx = combo.findData(valor)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _actualizar_resumen(self):
        if not self.chk_activo.isChecked():
            self.lbl_resumen.setText("Reengrose desactivado.")
            return
        activos = [b for b in VDO_RE_MODELO.BORDES_2D if self.btn_borde[b].isChecked()]
        if not activos:
            self.lbl_resumen.setText("Sin bordes perimetrales activos.")
            return

        nombres = [b.capitalize() for b in activos]
        if self.btn_centro.isChecked():
            offset_val = self.spin_offset.value()
            offset_txt = "al ras (offset 0)" if offset_val == 0 else f"offset {offset_val:.1f} mm"
            medidas = f"ancho {self.spin_ancho.value():.1f} mm · {offset_txt}"
        else:
            detalles = []
            for b in activos:
                w = self._valores_bordes[b]["ancho"]
                d = self._valores_bordes[b]["offset"]
                detalles.append(f"{b.capitalize()}: {w:.0f}mm @ {d:.0f}mm")
            medidas = " · ".join(detalles)

        tipos_esq = set(self._esquinas.values())
        if len(tipos_esq) == 1:
            texto_esq = ENCUENTRO_LABELS[next(iter(tipos_esq))]
        else:
            texto_esq = "Esquinas mixtas"

        esp = self.spin_espesor.value()
        texto_esp = f" · Espesor {esp:.1f} mm" if esp > 0 else ""

        self.lbl_resumen.setText(
            f"<b>{len(activos)} bordes</b> ({', '.join(nombres)})<br/>"
            f"{medidas}{texto_esp} · <i>{texto_esq}</i>"
        )

    def _emitir_cambio(self):
        if self._cargando:
            return
        self._actualizar_resumen()
        cfg = self.getConfig()
        self.sigConfigChanged.emit(cfg)
        self.changed.emit()

    @staticmethod
    def _set_combo_silencioso(combo, valor):
        combo.blockSignals(True)
        idx = combo.findData(valor)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.blockSignals(False)

    # ------------------------------------------------------------------
    # API Pública del Widget
    # ------------------------------------------------------------------
    def setConfig(self, cfg):
        """Carga la configuración existente en la UI sin emitir señales redundantes."""
        if cfg is None:
            cfg = {}
        elif hasattr(cfg, "to_dict"):
            cfg = cfg.to_dict()

        self._cargando = True
        try:
            # 1. Activo
            activo = bool(cfg.get("activo", False))
            self.chk_activo.setChecked(activo)

            # 2. Esquinas
            esquinas_raw = cfg.get("esquinas", VDO_RE_MODELO.ENCUENTRO_ESQUINAS_DEFAULT)
            esquinas_norm = VDO_RE_MODIFICADOR._normalizar_encuentro(esquinas_raw)
            for e in ESQUINAS:
                tipo = esquinas_norm.get(e, "vertical_domina")
                self._esquinas[e] = tipo
                self._set_combo_silencioso(self.combo_esquina[e], tipo)

            esquinas_unicas = len(set(self._esquinas.values())) == 1
            self.chk_sync_esquinas.setChecked(esquinas_unicas)
            self._actualizar_iconos_esquinas()

            # 3. Bordes
            bordes_data = cfg.get("bordes", {})
            activos = []
            for b in VDO_RE_MODELO.BORDES_2D:
                b_cfg = bordes_data.get(b, {})
                if hasattr(b_cfg, "to_dict"):
                    b_cfg = b_cfg.to_dict()
                b_activo = bool(b_cfg.get("activo", False))
                w = float(b_cfg.get("ancho", cfg.get("ancho", 70.0)))
                d = float(b_cfg.get("distancia_al_canto",
                                   b_cfg.get("offset_borde",
                                             cfg.get("offset", 0.0))))

                self.btn_borde[b].setChecked(b_activo)
                if b_activo:
                    activos.append(b)

                self._valores_bordes[b]["ancho"] = w
                self._valores_bordes[b]["offset"] = d
                self.spin_ancho_borde[b].setValue(w)
                self.spin_offset_borde[b].setValue(d)

            # Formato legacy sin bordes explícitos
            if not bordes_data and activo:
                self.btn_borde["frente"].setChecked(True)
                activos.append("frente")

            # 4. Modo Uniforme
            es_uniforme = cfg.get("uniforme")
            if es_uniforme is None:
                if activos:
                    w0 = self._valores_bordes[activos[0]]["ancho"]
                    d0 = self._valores_bordes[activos[0]]["offset"]
                    es_uniforme = all(
                        abs(self._valores_bordes[b]["ancho"] - w0) < 1e-4
                        and abs(self._valores_bordes[b]["offset"] - d0) < 1e-4
                        for b in activos
                    )
                else:
                    es_uniforme = True

            self.btn_centro.setChecked(es_uniforme)
            if es_uniforme:
                self.btn_centro.setText(" Uniforme")
                self.btn_centro.setIcon(obtener_svg_icon("link"))
            else:
                self.btn_centro.setText(" Individual")
                self.btn_centro.setIcon(obtener_svg_icon("unlink"))

            primero = activos[0] if activos else "frente"
            ancho_ref = self._valores_bordes[primero]["ancho"]
            dist_ref = self._valores_bordes[primero]["offset"]
            self.spin_ancho.setValue(float(cfg.get("ancho_uniforme", ancho_ref)))
            self.spin_offset.setValue(float(cfg.get("distancia_uniforme", dist_ref)))

            # 5. Espesor y parámetros de fabricación
            esp = cfg.get("espesor")
            self.spin_espesor.setValue(0.0 if esp is None else float(esp))
            self._fabricacion = cfg.get("fabricacion", "pacha")
            self._choque_nucleo = cfg.get("choque_nucleo", "retroceso")
            self._cara = cfg.get("cara", "cara_a")

            self._seleccionar_margen(self._margen_seleccionado)
            self._actualizar_estado_all()
            self._actualizar_estado_habilitacion()
            self._actualizar_canvas_concentrico()
            self._actualizar_resumen()

        finally:
            self._cargando = False

    def getConfig(self) -> dict:
        """Retorna la estructura compatible con vdo_reengrose.py."""
        uniforme = self.btn_centro.isChecked()
        ancho_u = float(self.spin_ancho.value())
        dist_u = float(self.spin_offset.value())
        esp_val = self.spin_espesor.value()
        espesor = float(esp_val) if esp_val > 0.0 else None

        bordes = {}
        for b in VDO_RE_MODELO.BORDES_2D:
            activo = self.btn_borde[b].isChecked()
            if uniforme:
                w = ancho_u
                d = dist_u
            else:
                w = float(self._valores_bordes[b]["ancho"])
                d = float(self._valores_bordes[b]["offset"])
            bordes[b] = {
                "activo": activo,
                "ancho": w,
                "offset_borde": d,
                "distancia_al_canto": d,
                "largo_tira": "marco_interior",
                "espesor": espesor,
            }

        esquinas = {e: self._esquinas[e] for e in ESQUINAS}

        return {
            "activo": bool(self.chk_activo.isChecked()),
            "uniforme": bool(uniforme),
            "ancho_uniforme": ancho_u,
            "distancia_uniforme": dist_u,
            "esquinas": esquinas,
            "bordes": bordes,
            "fabricacion": self._fabricacion,
            "choque_nucleo": self._choque_nucleo,
            "cara": self._cara,
            "espesor": espesor,
            "usa_bordes": True,
        }

    # Métodos compatibles con ReengroseModifier / ReengroseDTO / Convenciones Snake Case
    get_config = getConfig
    set_config = setConfig
    seleccionar_margen = _seleccionar_margen

    def cargar(self, modifier):
        """Alias para cargar un dict o ReengroseModifier."""
        self.setConfig(modifier)

    def leer_modificador(self):
        """Devuelve un objeto ReengroseModifier listo para el cálculo."""
        return VDO_RE_MODIFICADOR.ReengroseModifier(self.getConfig())

    def set_dimensiones_panel(self, ancho, fondo):
        """Referencia de medidas brutas."""
        pass


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
