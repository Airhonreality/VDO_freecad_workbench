"""Carga, lectura y resumen de valores del panel COCO."""

import json
import logging

from freecad.vdo.core import frames as VDO_FR
from freecad.vdo.core.module_props import ANCLAJE_DEFAULT
from freecad.vdo.ui.task_base import cerrar_dialogo

_LOG = logging.getLogger(__name__)


class CocoUnifiedValoresMixin:
    """Mixin del panel COCO: Carga, lectura y resumen de valores del panel COCO."""

    def _cargar_valores(self, obj):
        """Carga todas las propiedades del objeto en el panel."""
        self._building = True

        self.spin_alto.setValue(float(obj.Alto))
        self.spin_ancho.setValue(float(obj.Ancho))
        self.spin_fondo.setValue(float(obj.FondoModulo))
        self.spin_espesor.setValue(int(obj.Espesor))
        self._cargar_chassis(obj)
        self._cargar_orientacion(obj)
        self._cargar_divisiones(obj)

        self._actualizar_resumen()
        self._building = False

    def _cargar_chassis(self, obj):
        if hasattr(self, "box_chassis") and self.box_chassis is not None:
            raw_cfg = getattr(obj, "VDO_Chassis_JSON", None)
            cfg = None
            if raw_cfg:
                try:
                    cfg = json.loads(raw_cfg) if isinstance(raw_cfg, str) else raw_cfg
                except Exception as exc:
                    _LOG.warning("coco_unified_valores: configuracion de chasis no leida: %s", exc)
                    cfg = None
            if not cfg or not isinstance(cfg, dict):
                tapa = getattr(obj, "Tapa", "externo")
                base = getattr(obj, "Base", "interno")
                tiene_fondo = getattr(obj, "TieneFondo", True)
                cfg = {
                    "caras": {
                        "superior": {"activa": True, "tipo": "estructural"},
                        "inferior": {"activa": True, "tipo": "estructural"},
                        "izquierda": {"activa": True, "tipo": "estructural"},
                        "derecha": {"activa": True, "tipo": "estructural"},
                        "fondo": {"activa": bool(tiene_fondo), "tipo": "ranurado_5mm"},
                    },
                    "encuentros": {
                        "superior_izq": "tapa_domina" if tapa == "externo" else "lateral_domina",
                        "superior_der": "tapa_domina" if tapa == "externo" else "lateral_domina",
                        "inferior_izq": "base_domina" if base == "externo" else "lateral_domina",
                        "inferior_der": "base_domina" if base == "externo" else "lateral_domina",
                    },
                    "base": {
                        "estrategia": "zocalo",
                        "altura": float(getattr(obj, "AltoZocalo", 100.0) or 100.0),
                        "separacion_frente": float(getattr(obj, "DistanciaFrente", 50.0) or 50.0),
                    }
                }
            self.box_chassis.setChassisConfig(cfg)

    def _cargar_orientacion(self, obj):
        self.spin_rotacion.setValue(
            float(getattr(obj, "VDO_RotacionZ", 0.0)))
        anclaje = getattr(obj, "VDO_Anclaje", ANCLAJE_DEFAULT)
        for i in range(self.combo_anclaje.count()):
            if self.combo_anclaje.itemData(i) == anclaje:
                self.combo_anclaje.setCurrentIndex(i)
                break

        vistos, apoyados = VDO_FR.cargar_exposicion(obj)
        for lado, combo in self.combos_exposicion.items():
            estado = "oculto"
            if lado in vistos:
                estado = "visto"
            elif lado in apoyados:
                estado = "apoyado"
            idx = combo.findData(estado)
            if idx >= 0:
                combo.setCurrentIndex(idx)

    def _cargar_divisiones(self, obj):
        self._rows_x = []
        self._rows_y = []
        self._selected_paths = {"X": [], "Y": []}

        self.editor_divisiones.set_dimensions(
            self.spin_alto.value(), self.spin_ancho.value(),
            self.spin_espesor.value())
        self.editor_divisiones.cargar_desde_objeto(obj)

    def _leer_valores_ui(self):
        cfg = self.box_chassis.getChassisConfig() if hasattr(self, "box_chassis") and self.box_chassis else {}
        enc_sup = cfg.get("encuentros", {}).get("superior_izq", "tapa_domina")
        enc_inf = cfg.get("encuentros", {}).get("inferior_izq", "lateral_domina")
        tapa_val = "externo" if enc_sup == "tapa_domina" else "interno"
        base_val = "externo" if enc_inf == "base_domina" else "interno"
        return {
            "alto": self.spin_alto.value(),
            "ancho": self.spin_ancho.value(),
            "fondo": self.spin_fondo.value(),
            "espesor": self.spin_espesor.value(),
            "tapa": tapa_val,
            "base": base_val,
        }

    def _actualizar_resumen(self):
        valores = self._leer_valores_ui()
        espesor = float(valores["espesor"])
        ancho_util = valores["ancho"] - (espesor * 2)
        alto_util = valores["alto"] - (espesor * 2)
        texto = (
            f"COCO {valores['ancho']:.0f} × {valores['alto']:.0f} × "  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
            f"{valores['fondo']:.0f} mm\n"
            f"Cavidad interior: {ancho_util:.1f} × {alto_util:.1f} mm\n"  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
            f"Tapa: {valores['tapa']} · Base: {valores['base']} · "
            f"Espesor: {espesor:.0f} mm\n\n")
        texto += self.editor_divisiones.resumen()
        if self.editor_divisiones.tiene_overflow():
            texto += ("\n\n⚠ OVERFLOW: corrige las medidas fijas "
                      "antes de aplicar.")
        self.lbl_resumen.setText(texto)

    def _on_ok(self):
        if self.accept():
            cerrar_dialogo()

    def _on_cancel(self):
        self.reject()
        cerrar_dialogo()
