"""Paginas de detalle del inspector: constantes de pagina, base, chasis y cierre."""

import json
import FreeCAD as App
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui.selection_bridge import VDOSelectionBridge
try:
    from freecad.vdo.ui.chassis_widget import VDOChassisControllerWidget
except ImportError:  # pragma: no cover
    VDOChassisControllerWidget = None
from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import anadir_propiedad_texto, asignar_propiedades
from freecad.vdo.core import hardware_hub as HH
from freecad.vdo.datos.valores import BLUM_TANDEM, OCULTA
from freecad.vdo.ui import tema


# ----------------------------------------------------------------------
# Constantes de navegación del QStackedWidget
# ----------------------------------------------------------------------
PAGE_CHASIS = 0   # COCO / Chasis L2 (VDOChassisControllerWidget)
PAGE_VANO = 1     # Vano libre L0 (Luz neta + Dock de Habitantes)
PAGE_PIEZA = 2    # PANEL L1 (Header + Cuadrado Figma)
PAGE_CIERRE = 3   # CAJON / PUERTA / ZOCALO (Herrajes y Capa H)
_TARGET_TO_PAGE = {
    VDOSelectionBridge.TARGET_COCO: PAGE_CHASIS,
    getattr(VDOSelectionBridge, "TARGET_VANO", "VANO"): PAGE_VANO,
    VDOSelectionBridge.TARGET_PANEL: PAGE_PIEZA,
    VDOSelectionBridge.TARGET_CAJON: PAGE_CIERRE,
    VDOSelectionBridge.TARGET_PUERTA: PAGE_CIERRE,
    VDOSelectionBridge.TARGET_ZOCALO: PAGE_CIERRE,
}


def _float_seguro(valor, default=0.0):
    try:
        if valor is None:
            return default
        return float(valor)
    except (TypeError, ValueError, AttributeError) as exc:
        App.Console.PrintWarning(f"[VDO] inspector_paginas: valor no convertible, usa defecto: {exc}\n")
        return default


def _str_seguro(valor, default=""):
    try:
        if valor is None:
            return default
        return str(valor)
    except Exception as exc:
        App.Console.PrintWarning(f"[VDO] inspector_paginas: valor no leido, usa defecto: {exc}\n")
        return default


# ----------------------------------------------------------------------
# Páginas del QStackedWidget (Con Contenedores Scrollables)
# ----------------------------------------------------------------------
class _PaginaBase(QtWidgets.QWidget):
    """Página base con contenedor scrollable de datos."""

    def __init__(self, titulo, parent=None):
        super().__init__(parent)
        self._titulo = titulo

        layout_externo = QtWidgets.QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        layout_externo.setSpacing(0)

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        tema.aplicar_estilo(self.scroll, tema.ESTILO_SCROLL_TRANSPARENTE)

        self.contenido = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout(self.contenido)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(4)

        self.lbl_titulo = QtWidgets.QLabel(titulo)
        self.lbl_titulo.setObjectName("lblPaginaTitulo")
        tema.aplicar_estilo(self.lbl_titulo, tema.ESTILO_PAGINA_TITULO)
        self._layout.addWidget(self.lbl_titulo)

        self.contenedor_datos = QtWidgets.QVBoxLayout()
        self.contenedor_datos.setSpacing(4)
        self._layout.addLayout(self.contenedor_datos)
        self._layout.addStretch()

        self.scroll.setWidget(self.contenido)
        layout_externo.addWidget(self.scroll)

    def _add_dato(self, etiqueta, valor):
        fila = QtWidgets.QHBoxLayout()
        lbl_key = QtWidgets.QLabel(etiqueta)
        lbl_key.setFixedWidth(110)
        tema.aplicar_estilo(lbl_key, tema.ESTILO_CLAVE_10PX)
        lbl_val = QtWidgets.QLabel(str(valor))
        tema.aplicar_estilo(lbl_val, tema.ESTILO_VALOR_11PX_NEGRITA)
        fila.addWidget(lbl_key)
        fila.addWidget(lbl_val)
        fila.addStretch()
        self.contenedor_datos.addLayout(fila)
        return lbl_val


# ----------------------------------------------------------------------
# PÁGINA 0: CHASIS L2 (VDOChassisControllerWidget)
# ----------------------------------------------------------------------
class PaginaChasis(_PaginaBase):
    """Nivel Chasis / Envolvente (L2): Corte Transversal 2D interactivo."""

    def __init__(self, parent=None):
        super().__init__("Chasis / Envolvente (L2)", parent)
        self._obj_actual = None

        # Etiquetas dummy de compatibilidad para tests existentes (ocultas)
        self.lbl_alto = QtWidgets.QLabel("—")
        self.lbl_ancho = QtWidgets.QLabel("—")
        self.lbl_fondo = QtWidgets.QLabel("—")
        self.lbl_anclaje = QtWidgets.QLabel("—")
        self.lbl_subtipo = QtWidgets.QLabel("—")

        # Widget de corte transversal interactivo 2D
        self.box_chassis = None
        if VDOChassisControllerWidget is not None:
            self.box_chassis = VDOChassisControllerWidget()
            self.box_chassis.sigChassisChanged.connect(self._on_chassis_changed)
            self.contenedor_datos.addWidget(self.box_chassis)

    def cargar_coco(self, obj):
        """Carga los parámetros del chasis desde un objeto FreeCAD."""
        self._obj_actual = obj
        alto = _float_seguro(getattr(obj, "Alto", None))
        ancho = _float_seguro(getattr(obj, "Ancho", None))
        fondo = _float_seguro(getattr(obj, "FondoModulo", None))
        anclaje = _str_seguro(getattr(obj, "VDO_Anclaje", None))
        subtipo = _str_seguro(getattr(obj, "VDO_Subtipo", None))

        self.lbl_alto.setText(f"{alto:.1f} mm" if alto else "—")
        self.lbl_ancho.setText(f"{ancho:.1f} mm" if ancho else "—")
        self.lbl_fondo.setText(f"{fondo:.1f} mm" if fondo else "—")
        self.lbl_anclaje.setText(anclaje if anclaje else "—")
        self.lbl_subtipo.setText(subtipo if subtipo else "—")

        if self.box_chassis is not None:
            raw_cfg = getattr(obj, "VDO_Chassis_JSON", None)
            if raw_cfg:
                try:
                    cfg = json.loads(raw_cfg) if isinstance(raw_cfg, str) else raw_cfg
                    self.box_chassis.setChassisConfig(cfg)
                    return
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo cargar VDO_Chassis_JSON")

            cfg_default = {
                "caras": {
                    "superior": {"activa": True, "tipo": "estructural"},
                    "inferior": {"activa": True, "tipo": "estructural"},
                    "izquierda": {"activa": True, "tipo": "estructural"},
                    "derecha": {"activa": True, "tipo": "estructural"},
                    "fondo": {"activa": True, "tipo": "ranurado_5mm"},
                },
                "encuentros": {
                    "superior_izq": "tapa_domina",
                    "superior_der": "tapa_domina",
                    "inferior_izq": "lateral_domina",
                    "inferior_der": "lateral_domina",
                },
                "base": {
                    "estrategia": "zocalo" if getattr(obj, "AltoZocalo", None) else "zocalo",
                    "altura": _float_seguro(getattr(obj, "AltoZocalo", None), 100.0),
                    "separacion_frente": _float_seguro(getattr(obj, "DistanciaFrente", None), 50.0),
                }
            }
            self.box_chassis.setChassisConfig(cfg_default)

    def _on_chassis_changed(self, cfg):
        """Persiste la configuración modificada en el objeto FreeCAD."""
        obj = self._obj_actual
        if obj is None:
            return
        try:
            if hasattr(obj, "VDO_Chassis_JSON"):
                asignar_propiedades(obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
            elif hasattr(obj, "addProperty"):
                try:
                    anadir_propiedad_texto(obj, "VDO_Chassis_JSON", "VDO",
                                           "Configuración semiótica de Capa 1")
                    asignar_propiedades(obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo añadir propiedad VDO_Chassis_JSON")

            doc = getattr(obj, "Document", None)
            if doc is not None:
                recalcular(doc)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo persistir la configuración del chasis")


# ----------------------------------------------------------------------
# PÁGINA 3: CIERRES Y HERRAJES (CAJON / PUERTA / ZOCALO / CAPA H)
# ----------------------------------------------------------------------
class PaginaCierre(_PaginaBase):
    """Nivel Cierre / Herraje (CAJON / PUERTA / ZOCALO): Capa H y Fresado CNC."""

    def __init__(self, parent=None):
        super().__init__("Cierre / Herraje (Capa H)", parent)
        self._obj_actual = None

        self.lbl_tipo = self._add_dato("Tipo de cierre", "—")
        self.lbl_subtipo = self._add_dato("Subtipo", "—")
        self.lbl_sistema = self._add_dato("Sistema", "—")
        self.lbl_ancho_libre = self._add_dato("Ancho libre", "—")
        self.lbl_alto_frente = self._add_dato("Alto frente", "—")

        self.grp_herraje = QtWidgets.QGroupBox("Herrajes y Fresado CNC (Capa H)")
        tema.aplicar_estilo(self.grp_herraje, tema.ESTILO_GRUPO_HERRAJE)
        lay_h = QtWidgets.QVBoxLayout(self.grp_herraje)
        lay_h.setContentsMargins(6, 6, 6, 6)
        lay_h.setSpacing(3)

        def _fila_h(etiqueta):
            f = QtWidgets.QHBoxLayout()
            k = QtWidgets.QLabel(etiqueta)
            k.setFixedWidth(90)
            tema.aplicar_estilo(k, tema.ESTILO_CLAVE_10PX)
            v = QtWidgets.QLabel("—")
            tema.aplicar_estilo(v, tema.ESTILO_VALOR_BLANCO_10PX)
            f.addWidget(k)
            f.addWidget(v, 1)
            lay_h.addLayout(f)
            return v

        self.lbl_sku = _fila_h("SKU:")
        self.lbl_proveedor = _fila_h("Proveedor:")
        self.lbl_precio = _fila_h("Precio:")
        self.lbl_fresado = _fila_h("Fresado:")

        self.contenedor_datos.addWidget(self.grp_herraje)

    def cargar_cierre(self, obj, target_type):
        self._obj_actual = obj
        subtipo = _str_seguro(getattr(obj, "VDO_Subtipo", None))
        sistema = _str_seguro(getattr(obj, "SistemaApertura", None))
        ancho_libre = _float_seguro(getattr(obj, "AnchoLibre", None))
        alto_frente = _float_seguro(getattr(obj, "AltoFrente", None))

        self.lbl_tipo.setText(target_type)
        self.lbl_subtipo.setText(subtipo if subtipo else "—")
        self.lbl_sistema.setText(sistema if sistema else "—")
        self.lbl_ancho_libre.setText(f"{ancho_libre:.1f} mm" if ancho_libre else "—")
        self.lbl_alto_frente.setText(f"{alto_frente:.1f} mm" if alto_frente else "—")

        sku = _str_seguro(getattr(obj, "HardwareSKU", getattr(obj, "VDO_Herraje_Ref", None)))

        if target_type == "PUERTA":
            montaje = _str_seguro(getattr(obj, "TipoMontaje", "parche")).lower()
            h = HH.resolve_hinge(montaje, prefer_sku=sku if sku else None)
            if h:
                sku_txt = sku if sku else h.get("sku", "GEN-CAZ-35-PARCHE")
                self.lbl_sku.setText(sku_txt)
                self.lbl_proveedor.setText(h.get("proveedor", "Genérico"))
                self.lbl_precio.setText(f"${h.get('precio_unitario', 0.0):.2f} {h.get('moneda', 'USD')}")
                params = h.get("parametros_tecnicos", {})
                self.lbl_fresado.setText(
                    f"Cazoleta {params.get('diametro_cazoleta', 35):.0f}mm × {params.get('profundidad_cazoleta', 11.5):.1f}mm | K={params.get('cota_k_default', 4):.0f}mm")
                return

        elif target_type == "CAJON":
            marca = _str_seguro(getattr(obj, "MarcaCorredera", BLUM_TANDEM)).lower()
            tipo_cor = _str_seguro(getattr(obj, "TipoCorredera", OCULTA)).lower()
            s = HH.resolve_drawer_slide(tipo_cor, marca)
            if s:
                self.lbl_sku.setText(s.get("sku", "BLUM-TANDEM"))
                self.lbl_proveedor.setText(s.get("proveedor", "Blum"))
                self.lbl_precio.setText(f"${s.get('precio_unitario', 0.0):.2f} {s.get('moneda', 'USD')}")
                params = s.get("parametros_tecnicos", {})
                self.lbl_fresado.setText(
                    f"Delta: {params.get('delta_ancho', 49):.0f}mm | Pin: {params.get('diametro_pin_trasero', 6):.0f}mm")
                return

        self.lbl_sku.setText(sku if sku else "STD-VDO")
        self.lbl_proveedor.setText("Taller Estándar")
        self.lbl_precio.setText("—")
        self.lbl_fresado.setText("Perforaciones de ensamble estándar")

    def cargar_cierre_desde_config(self, tipo_cierre, cfg):
        """Carga datos de cierre desde un diccionario de configuración de vano."""
        tipo_tag = "CAJON" if "cajon" in tipo_cierre.lower() else "PUERTA"
        self.lbl_tipo.setText(tipo_tag)
        self.lbl_subtipo.setText(str(cfg.get("tipo", tipo_tag)))
        self.lbl_sistema.setText(str(cfg.get("sistema", cfg.get("corredera", "Estándar"))))
        self.lbl_ancho_libre.setText("—")
        self.lbl_alto_frente.setText("—")

        if tipo_tag == "PUERTA":
            h = HH.resolve_hinge("parche")
            if h:
                self.lbl_sku.setText(h.get("sku", "GEN-CAZ-35-PARCHE"))
                self.lbl_proveedor.setText(h.get("proveedor", "Genérico"))
                self.lbl_precio.setText(f"${h.get('precio_unitario', 0.0):.2f} {h.get('moneda', 'USD')}")
                self.lbl_fresado.setText("Cazoleta 35mm × 11.5mm | K=4mm")
        else:
            s = HH.resolve_drawer_slide(OCULTA, BLUM_TANDEM)
            if s:
                self.lbl_sku.setText(s.get("sku", "BLUM-TANDEM"))
                self.lbl_proveedor.setText(s.get("proveedor", "Blum"))
                self.lbl_precio.setText(f"${s.get('precio_unitario', 0.0):.2f} {s.get('moneda', 'USD')}")
                self.lbl_fresado.setText("Delta: 49mm | Pin: 6mm")
