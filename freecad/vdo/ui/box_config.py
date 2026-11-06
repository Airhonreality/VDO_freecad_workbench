"""API publica de configuracion. Parte de ui/vdo_box_controller.py (M7, D-44)."""

from freecad.vdo.core import (
    vdo_reengrose_modelo as VDO_RE_MODELO,
    vdo_reengrose_modificador as VDO_RE_MODIFICADOR,
)

from freecad.vdo.ui.box_constantes import ESQUINAS, obtener_svg_icon


class BoxConfigMixin:
    """Mixin de VDOBoxControllerWidget: API publica de configuracion. Sin cambios de codigo (D-44)."""

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
            activo = self._aplicar_activo(cfg)
            self._aplicar_esquinas(cfg)
            bordes_data, activos = self._aplicar_bordes(cfg)
            # Formato legacy sin bordes explícitos
            if not bordes_data and activo:
                self.btn_borde["frente"].setChecked(True)
                activos.append("frente")

            self._aplicar_modo_uniforme(cfg, activos)
            self._aplicar_fabricacion(cfg)

            self._seleccionar_margen(self._margen_seleccionado)
            self._actualizar_estado_all()
            self._actualizar_estado_habilitacion()
            self._actualizar_canvas_concentrico()
            self._actualizar_resumen()

        finally:
            self._cargando = False

    def _aplicar_activo(self, cfg):
        # 1. Activo
        activo = bool(cfg.get("activo", False))
        self.chk_activo.setChecked(activo)
        return activo

    def _aplicar_esquinas(self, cfg):
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

    def _aplicar_bordes(self, cfg):
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
        return bordes_data, activos

    def _aplicar_modo_uniforme(self, cfg, activos):
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

    def _aplicar_fabricacion(self, cfg):
        # 5. Espesor y parámetros de fabricación
        esp = cfg.get("espesor")
        self.spin_espesor.setValue(0.0 if esp is None else float(esp))
        self._fabricacion = cfg.get("fabricacion", "pacha")
        self._choque_nucleo = cfg.get("choque_nucleo", "retroceso")
        self._cara = cfg.get("cara", "cara_a")

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

    def cargar(self, modifier):
        """Alias para cargar un dict o ReengroseModifier."""
        self.setConfig(modifier)

    def leer_modificador(self):
        """Devuelve un objeto ReengroseModifier listo para el cálculo."""
        return VDO_RE_MODIFICADOR.ReengroseModifier(self.getConfig())

    def set_dimensiones_panel(self, ancho, fondo):
        """Referencia de medidas brutas."""
        pass
