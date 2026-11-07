"""Acciones de navegacion y edicion del inspector (migas, dimensiones, habitantes)."""

import json
import logging

import FreeCAD as App

from freecad.vdo.cad.documento import recalcular
from freecad.vdo.cad.propiedades import anadir_propiedad_texto, asignar_propiedades
from freecad.vdo.ui.inspector_cabecera import (
    _CLAVE_BREADCRUMB_A_NIVEL,
    _RUTA_BREADCRUMB_DEFECTO,
    _RUTA_BREADCRUMB_POR_TARGET,
)

_LOG = logging.getLogger(__name__)

try:
    from freecad.vdo.core.layout_matriz import Layout
    from freecad.vdo.core.layout_modelo import cavidad_interior
    from freecad.vdo.core.layout_resolucion import resolve_layout
except ImportError as exc:  # pragma: no cover
    _LOG.debug("inspector_acciones: Layout no disponible: %s", exc)
    Layout = None
    resolve_layout = None
    cavidad_interior = None


class AccionesInspectorMixin:
    """Acciones de navegacion y edicion del inspector (migas, dimensiones, habitantes)."""

    def _ir_a_nivel(self, page_index, target_type):
        if self.stack is None:
            return
        self.stack.setCurrentIndex(page_index)
        self._tipo_actual = target_type

        # Actualizar breadcrumbs
        ruta, activo = _RUTA_BREADCRUMB_POR_TARGET.get(
            target_type, _RUTA_BREADCRUMB_DEFECTO)
        self.breadcrumbs.set_ruta(list(ruta), activo=activo)

        self.sigNivelCambiado.emit(page_index, target_type)

    def _on_breadcrumb_clicked(self, clave):
        destino = _CLAVE_BREADCRUMB_A_NIVEL.get(clave)
        if destino is not None:
            self._ir_a_nivel(*destino)


    # ------------------------------------------------------------------
    # Ediciones de Usuario en MicroHeader y Páginas
    # ------------------------------------------------------------------
    def _on_dimensiones_header_cambiadas(self, w, h, d, e):
        obj = self._obj_actual
        if obj is not None:
            try:
                if hasattr(obj, "Ancho"):
                    asignar_propiedades(obj, {"Ancho": w})
                if hasattr(obj, "Alto"):
                    asignar_propiedades(obj, {"Alto": h})
                if hasattr(obj, "FondoModulo"):
                    asignar_propiedades(obj, {"FondoModulo": d})
                if hasattr(obj, "Espesor"):
                    try:
                        asignar_propiedades(obj, {"Espesor": e})
                    except TypeError as exc:
                        _LOG.debug("inspector_acciones: espesor asignado con firma alternativa: %s", exc)
                        asignar_propiedades(obj, {"Espesor": round(e)})
                doc = getattr(obj, "Document", None)
                if doc is not None:
                    recalcular(doc)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudieron actualizar las dimensiones del header")
        self._actualizar_vista_completa()

    def _on_habitante_vano_cambiado(self, tipo_hab, cfg):
        obj = self._obj_actual
        if obj is None or Layout is None:
            return

        def _guardar_prop(prop_name, prop_val):
            try:
                if hasattr(obj, prop_name):
                    asignar_propiedades(obj, {prop_name: prop_val})
                elif hasattr(obj, "addProperty"):
                    anadir_propiedad_texto(obj, prop_name, "VDO", prop_name)
                    asignar_propiedades(obj, {prop_name: prop_val})
            except Exception:
                App.Console.PrintWarning(
                    f"[VDO] No se pudo guardar propiedad {prop_name}")

        celda_lbl = cfg.get("celda", "(x1, y1)")
        texto_div = getattr(obj, "VDO_Divisiones", "") or ""
        layout = Layout.loads(texto_div)
        contenido = self._leer_contenido_vano(obj)

        self._aplicar_habitante_celda(tipo_hab, cfg, celda_lbl, layout, contenido, _guardar_prop)

        try:
            doc = getattr(obj, "Document", None)
            if doc is not None:
                recalcular(doc)
        except Exception:
            App.Console.PrintWarning(
                "[VDO] No se pudo recomputar el documento")

        self._actualizar_vista_completa()

    def _leer_contenido_vano(self, obj):
        texto_contenido = getattr(obj, "VDO_Contenido_JSON", "{}") or "{}"
        try:
            return json.loads(texto_contenido) if isinstance(texto_contenido, str) else dict(texto_contenido)
        except Exception as exc:
            App.Console.PrintWarning(f"[VDO] inspector_acciones: contenido no leido, usa vacio: {exc}\n")
            return {}

    def _aplicar_habitante_celda(self, tipo_hab, cfg, celda_lbl, layout, contenido, guardar_prop):
        if tipo_hab == "subdividir":
            cell = layout.find_label(celda_lbl)
            if cell is not None:
                layout.set_split(cell, cfg.get("eje", "Y"), int(cfg.get("n_partes", 2)))
                guardar_prop("VDO_Divisiones", layout.dumps())
        elif tipo_hab == "cajon" or tipo_hab == "puerta":
            contenido[celda_lbl] = cfg
            guardar_prop("VDO_Contenido_JSON", json.dumps(contenido))
        elif tipo_hab == "vacio":
            cell = layout.find_label(celda_lbl)
            if cell is not None:
                layout.disable_split(cell)
                guardar_prop("VDO_Divisiones", layout.dumps())
            if celda_lbl in contenido:
                del contenido[celda_lbl]
                guardar_prop("VDO_Contenido_JSON", json.dumps(contenido))
