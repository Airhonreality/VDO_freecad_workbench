# =====================================================================
# selection_bridge.py
# Puente de reactividad de selección nativa (Sistema VDO).
#
# Observa Gui.Selection de forma desacoplada: detecta qué objeto tocó el
# usuario en el canvas 3D o en el árbol, sin abrir diálogos modales y sin
# arrojar excepciones a la Report View durante un clic del ratón.
#
# No acopla lógica de Qt. Es un puente puro entre FreeCAD Selection y
# eventos de datos.
# =====================================================================

import logging

import FreeCAD as App

_LOG = logging.getLogger(__name__)

try:
    import FreeCADGui as Gui
except ImportError as exc:  # FreeCADCmd / entorno headless
    _LOG.debug("selection_bridge: Gui no disponible (entorno headless): %s", exc)
    Gui = None


# Tabla de despacho (P3): nombre de clase del Proxy -> TARGET.
# Claves distintas entre sí: no hay solapamiento, el orden no altera el resultado.
_TARGET_POR_PROXY = {
    "CocoFeature": "COCO",
    "PanelFeature": "PANEL",
    "CajonFeature": "CAJON",
    "PuertaFeature": "PUERTA",
    "ZocaloFeature": "ZOCALO",
    "VanoFeature": "VANO",
    "Vano": "VANO",
}


class VDOSelectionBridge:
    """Observer de selección nativa de FreeCAD.

    Implementa la interfaz de ``FreeCAD.SelectionObserver``:
        - addSelection(doc_name, obj_name, sub_name, pos)
        - clearSelection(doc_name)

    Clasifica los objetos mediante el tipo de su Proxy (FeaturePython) y,
    como fallback, por propiedades de firma. Nunca depende del ``Label``
    ni de nombres arbitrarios.
    """

    TARGET_COCO = "COCO"
    TARGET_PANEL = "PANEL"
    TARGET_CAJON = "CAJON"
    TARGET_PUERTA = "PUERTA"
    TARGET_ZOCALO = "ZOCALO"
    TARGET_VANO = "VANO"
    TARGET_UNKNOWN = "UNKNOWN"

    def __init__(self, on_target_changed=None):
        self._observador_activo = False
        self._callback = on_target_changed
        self._ultimo_objeto = None
        self._ultimo_tipo = self.TARGET_UNKNOWN

    # ------------------------------------------------------------------
    # Registro / desregistro
    # ------------------------------------------------------------------
    def attach(self):
        """Registra el observer en Gui.Selection (idempotente)."""
        try:
            if Gui is None:
                return False
            if self._observador_activo:
                return True
            Gui.Selection.addObserver(self)
            self._observador_activo = True
            return True
        except Exception as exc:
            App.Console.PrintWarning(f"[VDO] selection_bridge: observador no activado: {exc}\n")
            self._observador_activo = False
            return False

    def detach(self):
        """Desregistra el observer de forma idempotente."""
        try:
            if Gui is None:
                self._observador_activo = False
                return True
            if not self._observador_activo:
                return True
            Gui.Selection.removeObserver(self)
            self._observador_activo = False
            return True
        except Exception as exc:
            App.Console.PrintWarning(f"[VDO] selection_bridge: observador no desactivado: {exc}\n")
            self._observador_activo = False
            return False

    # ------------------------------------------------------------------
    # Clasificación determinista (firma de FeaturePython, no Label)
    # ------------------------------------------------------------------
    @staticmethod
    def _tiene_prop(obj, nombre):
        try:
            return hasattr(obj, nombre)
        except Exception as exc:
            App.Console.PrintWarning(f"[VDO] selection_bridge: comprobacion fallida, devuelve False: {exc}\n")
            return False

    def classify_object(self, obj) -> str:
        """Clasifica un DocumentObject en COCO/PANEL/CAJON/PUERTA/ZOCALO/UNKNOWN.

        Orden de prioridad:
          1. Tipo del Proxy (más determinista).
          2. Combinaciones de propiedades de firma (fallback).
        """
        if obj is None:
            return self.TARGET_UNKNOWN

        try:
            proxy = getattr(obj, "Proxy", None)
            if proxy is not None:
                target = _TARGET_POR_PROXY.get(type(proxy).__name__)
                if target is not None:
                    return target
        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error clasificando objeto de selección")

        # Fallback por propiedades de firma (sin depender del Label)
        try:
            if (self._tiene_prop(obj, "VDO_Tipo") and getattr(obj, "VDO_Tipo", None) == "vano") or (
                    self._tiene_prop(obj, "LuzLibreX") and self._tiene_prop(obj, "LuzLibreY")):
                return self.TARGET_VANO
            if (self._tiene_prop(obj, "AnchoLibre")
                    and self._tiene_prop(obj, "ProfLibre")
                    and self._tiene_prop(obj, "MarcaCorredera")):
                return self.TARGET_CAJON

            if (self._tiene_prop(obj, "TipoSistema")
                    and self._tiene_prop(obj, "SentidoApertura")
                    and self._tiene_prop(obj, "HardwareSKU")):
                return self.TARGET_PUERTA

            if (self._tiene_prop(obj, "AltoZocalo")
                    and self._tiene_prop(obj, "DistanciaFrente")
                    and self._tiene_prop(obj, "TieneTrasera")):
                return self.TARGET_ZOCALO

            if (self._tiene_prop(obj, "VDO_Divisiones")
                    and self._tiene_prop(obj, "Hijos")
                    and getattr(obj, "VDO_Subtipo", None) == "COCO_4C"):
                return self.TARGET_COCO

            if (getattr(obj, "VDO_Tipo", None) == "panel"
                    and self._tiene_prop(obj, "VDO_Orientacion")):
                return self.TARGET_PANEL
        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error en fallback de clasificación por propiedades")

        return self.TARGET_UNKNOWN

    # ------------------------------------------------------------------
    # Interfaz SelectionObserver (cuerpo 100% encapsulado en try/except)
    # ------------------------------------------------------------------
    def addSelection(self, doc_name, obj_name, sub_name, pos):
        """Se dispara cuando el usuario selecciona un objeto (canvas/árbol)."""
        try:
            doc = App.getDocument(doc_name)
            if doc is None:
                return
            obj = doc.getObject(obj_name)
            if obj is None:
                return
            target_type = self.classify_object(obj)
            self._ultimo_objeto = obj
            self._ultimo_tipo = target_type
            if self._callback is not None:
                self._callback(obj, target_type)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error en addSelection del puente")

    def clearSelection(self, doc_name):
        """Se dispara cuando se limpia la selección."""
        try:
            self._ultimo_objeto = None
            self._ultimo_tipo = self.TARGET_UNKNOWN
            if self._callback is not None:
                self._callback(None, self.TARGET_UNKNOWN)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] Error en clearSelection del puente")

    # ------------------------------------------------------------------
    # Consulta de estado
    # ------------------------------------------------------------------
    @property
    def ultimo_objeto(self):
        return self._ultimo_objeto

    @property
    def ultimo_tipo(self):
        return self._ultimo_tipo

    @property
    def esta_activo(self):
        return self._observador_activo
