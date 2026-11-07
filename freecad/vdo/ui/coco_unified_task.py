# =====================================================================
# coco_unified_task.py
# Task Panel UNIFICADO para COCO: edita TODO (básico + espacios + pose).
# Se abre por clic derecho, doble clic o flujo de creación.
# =====================================================================

import json
import logging

import FreeCAD as App

from freecad.vdo.cad.documento import (
    crear_objeto,
    eliminar_objeto,
    recalcular_activo,
)
from freecad.vdo.cad.propiedades import (
    add_common_props,
    anadir_propiedad_texto,
    asignar_placement_local,
    asignar_propiedades,
)
from freecad.vdo.cad.transaccion import foto_propiedades, restaurar_propiedades
from freecad.vdo.core.aperturas import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
)
from freecad.vdo.core.facade_contract import CALLE_ENTRE_FRENTES_DEFAULT
from freecad.vdo.datos.valores import BLUM_TANDEM
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.coco_unified_celdas import CocoUnifiedCeldasMixin
from freecad.vdo.ui.coco_unified_construccion import (
    CocoUnifiedConstruccionMixin,
)
from freecad.vdo.ui.coco_unified_escritura import CocoUnifiedEscrituraMixin
from freecad.vdo.ui.coco_unified_valores import CocoUnifiedValoresMixin
from freecad.vdo.ui.task_base import VDOTransactionMixin

_LOG = logging.getLogger(__name__)


class CocoUnifiedTaskPanel(
    CocoUnifiedConstruccionMixin,
    CocoUnifiedValoresMixin,
    CocoUnifiedCeldasMixin,
    CocoUnifiedEscrituraMixin,
    VDOTransactionMixin,
):
    """Task Panel UNIFICADO: Medidas + Estructura + Divisiones + Colocación."""

    def __init__(self, obj=None, on_accept=None, on_cancel=None,
                 auto_transaction=True):
        self.obj = obj
        self._vdo_aceptado = False
        self._current_axis = "X"
        self._rows_x = []
        self._rows_y = []
        self._selected_paths = {"X": [], "Y": []}
        self._building = False
        self.spin_dividir = {}
        self.spin_dividir_hijo = {}
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name="Editar COCO Completo",
        )
        self.form = self._crear_widget()
        if obj:
            add_common_props(obj)
            if not hasattr(obj, "VDO_Reengrose_JSON"):
                anadir_propiedad_texto(
                    obj, "VDO_Reengrose_JSON",
                    "Reengrose",
                    "Modificadores de reengrose por pieza (JSON)"
                ).VDO_Reengrose_JSON = "{}"
            if not hasattr(obj, "VDO_Contenido_JSON"):
                anadir_propiedad_texto(
                    obj, "VDO_Contenido_JSON",
                    "Contenido",
                    "Contenido de vanos (puertas, cajones) (JSON)"
                ).VDO_Contenido_JSON = "{}"
            self._cargar_valores(obj)

    def _construir_insertos(self, coco_obj):
        """Crea o actualiza los objetos hijos (puertas, cajones) del COCO.

        Se llama solo al presionar "Aceptar". No muta el documento antes.
        Gestiona huérfanos: elimina hijos cuyo vano ya no tenga contenido.
        """
        doc = App.ActiveDocument
        if doc is None:
            return
        contenido_tuplas = self._leer_contenido_tuplas(coco_obj)

        # Resolved map para obtener cotas de celdas
        editor = self.editor_divisiones
        resolved_map = getattr(editor, "_resolved_map", {})
        layout = getattr(editor, "layout", None)

        hijos_nuevos = []
        celdas_procesadas = set()

        self._insertar_hijos_vanos(doc, coco_obj, contenido_tuplas, layout,
                                   resolved_map, celdas_procesadas, hijos_nuevos)

        self._eliminar_huerfanos(doc, coco_obj, hijos_nuevos)

        asignar_propiedades(coco_obj, {"Hijos": hijos_nuevos})


    def _leer_contenido_tuplas(self, coco_obj):
        # Leer contenido persistido
        texto = getattr(coco_obj, "VDO_Contenido_JSON", "") or "{}"
        try:
            contenido = json.loads(texto) if isinstance(texto, str) else {}
        except (ValueError, TypeError) as exc:
            App.Console.PrintWarning(f"[VDO] coco_unified_task: contenido de celdas no valido, usa vacio: {exc}\n")
            contenido = {}
        # Convertir claves "i,j" a tuplas (col, row)
        contenido_tuplas = {}
        for k, v in contenido.items():
            try:
                col, row = map(int, str(k).split(","))
                contenido_tuplas[(col, row)] = v
            except (ValueError, TypeError) as exc:
                _LOG.debug("coco_unified_task: celda malformada, se omite: %s", exc)
                continue
        return contenido_tuplas

    def _insertar_hijos_vanos(self, doc, coco_obj, contenido_tuplas, layout,
                              resolved_map, celdas_procesadas, hijos_nuevos):
        for (col, row), datos in contenido_tuplas.items():
            celdas_procesadas.add((col, row))
            tipo = datos.get("tipo", "vacio")
            cfg = datos.get("config", {})

            if layout is None:
                continue
            cell = layout.get_cell(col, row)
            if cell is None:
                continue
            resuelto = resolved_map.get(cell.label)
            if resuelto is None:
                continue

            x = float(getattr(resuelto, "nominal_x", 0.0))
            z = float(getattr(resuelto, "nominal_z", 0.0))
            w = float(resuelto.w)
            h = float(resuelto.h)

            if tipo == "puerta":
                self._construir_puerta(
                    doc, coco_obj, cfg, x, z, w, h, hijos_nuevos)
            elif tipo == "cajon" or tipo == "cajon_torre":
                self._construir_cajones(
                    doc, coco_obj, cfg, x, z, w, h, hijos_nuevos)

    def _eliminar_huerfanos(self, doc, coco_obj, hijos_nuevos):
        # --- Gestión de huérfanos ---
        hijos_actuales = list(coco_obj.Hijos or [])
        claves_activas = set()
        for hijo in hijos_nuevos:
            claves_activas.add(hijo.Name)
        for hijo in hijos_actuales:
            if hijo.Name not in claves_activas:
                try:
                    eliminar_objeto(doc, hijo.Name)
                except Exception:
                    App.Console.PrintWarning(
                        f"[VDO] No se pudo remover el hijo {hijo.Name}")

    def _construir_puerta(self, doc, coco_obj, cfg, x, z, w, h, hijos_nuevos):
        """Crea o actualiza una puerta como hijo del COCO."""
        nombre = cfg.get("nombre", f"Puerta_{coco_obj.Name}")
        # Buscar si ya existe
        existente = None
        for hijo in list(coco_obj.Hijos or []):
            if hijo.Name == nombre:
                existente = hijo
                break

        if existente is None:
            existente = crear_objeto(doc, "Part::FeaturePython", nombre)
            from freecad.vdo.cad.puerta import PuertaFeature
            PuertaFeature(existente)
            if App.GuiUp:
                from freecad.vdo.ui.view_provider_base import ViewProviderPuerta
                ViewProviderPuerta(existente.ViewObject)

        # Propiedades de la puerta
        asignar_propiedades(existente, {"TipoSistema": cfg.get("tipo_sistema", "Batiente Vertical")})
        asignar_propiedades(existente, {"TipoMontaje": cfg.get("tipo_montaje", "Parche")})
        asignar_propiedades(existente, {"SentidoApertura": cfg.get("sentido_apertura", "Izquierda")})
        asignar_propiedades(existente, {"SistemaApertura": cfg.get(
            "sistema_apertura", APERTURA_TIRADOR)})
        asignar_propiedades(existente, {"HardwareSKU": cfg.get("hardware_sku", "")})
        asignar_propiedades(existente, {"VDO_Vano_ID": cfg.get("vdo_vano_id", "")})
        asignar_propiedades(existente, {"Ancho": float(cfg.get("ancho", w))})
        asignar_propiedades(existente, {"Alto": float(cfg.get("alto", h))})
        asignar_propiedades(existente, {"Espesor": int(cfg.get("espesor", 18))})
        asignar_propiedades(existente, {"PosX": float(cfg.get("pos_x", x))})
        asignar_propiedades(existente, {"PosY": float(cfg.get("pos_y", 0.0))})
        asignar_propiedades(existente, {"PosZ": float(cfg.get("pos_z", z))})
        asignar_propiedades(existente, {"VDO_Anclaje": cfg.get("anclaje", "inferior_izquierda_frente")})

        # Vínculo padre-hijo
        asignar_propiedades(existente, {"ParentCOCO": coco_obj})
        asignar_placement_local(existente, App.Placement(
            App.Vector(
                float(cfg.get("pos_x", x)),
                float(cfg.get("pos_y", 0.0)),
                float(cfg.get("pos_z", z)),
            ), App.Rotation()))

        hijos_nuevos.append(existente)

    def _construir_cajones(self, doc, coco_obj, cfg, x, z, w, h, hijos_nuevos):
        """Crea o actualiza cajones (1 o más, torre apilada) como hijos del COCO."""
        cantidad = int(cfg.get("cantidad", 1))
        corredera = cfg.get("corredera", "Oculta")
        apertura = cfg.get("apertura", "Tirador")
        nombre_base = cfg.get("nombre", f"Cajon_{coco_obj.Name}")

        # Calcular altura individual de frente para torre N cajones
        h_frente = (h - (cantidad - 1) * CALLE_ENTRE_FRENTES_DEFAULT) / cantidad
        if h_frente <= 0:
            h_frente = max(10.0, h / max(cantidad, 1))

        from freecad.vdo.core.cajon_correderas import (
            CORREDERA_OCULTA,
            CORREDERA_TELESCOPICA,
        )
        tipo_corredera = CORREDERA_OCULTA if corredera == "Oculta" else CORREDERA_TELESCOPICA

        apertura_map = {
            "Tirador": APERTURA_TIRADOR,
            "Gola": APERTURA_GOLA,
            "45°": APERTURA_45_GRADOS,
            "Push": APERTURA_PUSH_OPEN,
        }
        sistema_apertura = apertura_map.get(apertura, APERTURA_TIRADOR)

        for i in range(cantidad):
            nombre = f"{nombre_base}_{i + 1:02d}"
            # Buscar si ya existe
            existente = None
            for hijo in list(coco_obj.Hijos or []):
                if hijo.Name == nombre:
                    existente = hijo
                    break

            if existente is None:
                existente = crear_objeto(doc, "Part::FeaturePython", nombre)
                from freecad.vdo.cad.cajon import CajonFeature
                CajonFeature(existente)
                if App.GuiUp:
                    from freecad.vdo.ui.view_provider_base import ViewProviderCajon
                    ViewProviderCajon(existente.ViewObject)

            # Propiedades del cajón
            self._asignar_propiedades_cajon(
                existente, w, coco_obj, h_frente, tipo_corredera, sistema_apertura)

            # Vínculo padre-hijo con z escalonado
            z_local = z + i * (h_frente + CALLE_ENTRE_FRENTES_DEFAULT)
            asignar_propiedades(existente, {"ParentCOCO": coco_obj})
            asignar_placement_local(existente, App.Placement(
                App.Vector(x, 0.0, z_local), App.Rotation()))

            hijos_nuevos.append(existente)

    def _asignar_propiedades_cajon(self, existente, w, coco_obj, h_frente,
                                   tipo_corredera, sistema_apertura):
        # Propiedades de fabricación por defecto del cajón.
        asignar_propiedades(existente, {"AnchoLibre": w})
        asignar_propiedades(existente, {"ProfLibre": float(getattr(coco_obj, "FondoModulo", 580.0))})
        asignar_propiedades(existente, {"AnchoModulo": w})
        asignar_propiedades(existente, {"AltoFrente": h_frente})
        # default 90mm
        asignar_propiedades(existente, {"AltoCaja": float(getattr(coco_obj, "Espesor", 18)) * 5})
        asignar_propiedades(existente, {"GrosorCaja": 16.0})
        asignar_propiedades(existente, {"GrosorFondo": 6.0})
        asignar_propiedades(existente, {"GrosorFachada": 18.0})
        asignar_propiedades(existente, {"MarcaCorredera": BLUM_TANDEM})
        asignar_propiedades(existente, {"LongitudGuia": 0.0})
        asignar_propiedades(existente, {"MontajeTrasera": "entre_laterales"})
        asignar_propiedades(existente, {"TipoCorredera": tipo_corredera})
        asignar_propiedades(existente, {"SistemaApertura": sistema_apertura})

    def accept(self):
        if not self.obj:
            return True
        foto = foto_propiedades(self.obj)
        try:
            self._vdo_begin()
            if self._escribir_coco() and self._confirmar():
                return True
        except Exception as exc:
            resultado = self._fallar_accept(exc)
            restaurar_propiedades(self.obj, foto)
            return resultado
        restaurar_propiedades(self.obj, foto)
        return False

    def _escribir_coco(self):
        self._asignar_dimensiones()
        self._guardar_estructura()
        self._asignar_anclaje_rotacion()
        if not self._comprobar_divisiones():
            return False
        self._guardar_exposicion()
        self._guardar_divisiones()
        self._construir_insertos(self.obj)
        return True

    def _comprobar_divisiones(self):
        if not self.editor_divisiones.tiene_overflow():
            return True
        QtWidgets.QMessageBox.warning(
            self.form, "Divisiones VDO",
            "Las medidas fijas no caben en la cavidad interior.\n"
            "Reduce alguna medida antes de aplicar.")
        self._vdo_cerrar("abort")
        return False

    def _confirmar(self):
        recalcular_activo()
        self._vdo_cerrar("commit")
        self._vdo_aceptado = True
        self._vdo_call_accept()
        return True

    def _fallar_accept(self, exc):
        self._vdo_cerrar("abort")
        App.Console.PrintError(
            f"[VDO] Error aceptando COCO: {exc}\n")
        import traceback
        App.Console.PrintError(traceback.format_exc())
        return False
