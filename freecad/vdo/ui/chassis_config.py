"""API publica de configuracion del chasis. Parte de ui/vdo_chassis_widget.py (M7, D-45)."""


from freecad.vdo.ui.chassis_constantes import (
    CARAS,
    ENCUENTROS,
)


class ChassisConfigMixin:
    """Mixin de VDOChassisControllerWidget: API publica de configuracion. Sin cambios de codigo (D-45)."""

    def _emitir_cambio(self):
        if not self._cargando:
            self.sigChassisChanged.emit(self.getChassisConfig())

    # ------------------------------------------------------------------
    # Contrato Público API (Capa 1)
    # ------------------------------------------------------------------
    def setChassisConfig(self, cfg: dict):
        """Carga la configuración sin emitir señales redundantes."""
        if not isinstance(cfg, dict):
            return

        self._cargando = True
        try:
            # Caras
            caras_cfg = cfg.get("caras", {})
            for c in CARAS:
                if c in caras_cfg:
                    self._caras[c] = dict(caras_cfg[c])

            # Encuentros
            enc_cfg = cfg.get("encuentros", {})
            for e in ENCUENTROS:
                if e in enc_cfg:
                    self._encuentros[e] = enc_cfg[e]

            # Base
            base_cfg = cfg.get("base", {})
            if base_cfg:
                self._base.update(base_cfg)

            self._actualizar_ui()
        finally:
            self._cargando = False

    def getChassisConfig(self) -> dict:
        """Devuelve el diccionario canónico de Capa 1 para el chasis."""
        return {
            "caras": {
                c: dict(self._caras[c]) for c in CARAS
            },
            "encuentros": {
                e: self._encuentros[e] for e in ENCUENTROS
            },
            "base": {
                "estrategia": self._base.get("estrategia", "zocalo"),
                "altura": float(self._base.get("altura", 100.0)),
                "separacion_frente": float(self._base.get("separacion_frente", 50.0)),
            }
        }

    # Aliases de compatibilidad y estilo snake_case
    set_chassis_config = setChassisConfig
    get_chassis_config = getChassisConfig
