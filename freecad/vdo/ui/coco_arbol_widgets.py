"""Arbol de la matriz COCO: reconstruccion, resolucion y piezas (pintado en coco_arbol_pintado).

Extraido de vdo_widgets_coco.py (M7, D-40). Sin cambios de codigo."""

import logging

_LOG = logging.getLogger(__name__)

import FreeCAD as App

from freecad.vdo.core import (
    finish as VDO_FIN,
)
from freecad.vdo.core import (
    frames as VDO_FR,
)
from freecad.vdo.core import (
    reengrose_despiece as VDO_RE_DESPIECE,
)
from freecad.vdo.core import (
    reengrose_geometria as VDO_RE_GEOMETRIA,
)
from freecad.vdo.core import (
    reengrose_modificador as VDO_RE_MODIFICADOR,
)
from freecad.vdo.core.layout_modelo import AXIS_X, AXIS_Y
from freecad.vdo.core.layout_resolucion import resolve_layout
from freecad.vdo.ui.coco_arbol_pintado import ArbolPintadoMixin


class ArbolDivisionesMixin(ArbolPintadoMixin):
    """Mixin de DivisionesEditor (ver coco_construccion_widgets.py)."""

    # -----------------------------------------------------------------
    # Resolución y árbol
    # -----------------------------------------------------------------
    def _rebuild(self):
        if self.inner_w <= 0 or self.inner_h <= 0:
            self._resolved = resolve_layout(
                self.layout, max(0.0, self.inner_w),
                max(0.0, self.inner_h), self.thickness,
                reengroses=self.reengroses)
        else:
            self._resolved = resolve_layout(
                self.layout, self.inner_w, self.inner_h, self.thickness,
                reengroses=self.reengroses)
        self._resolved_map = {
            cell.label: cell for cell in self._resolved.walk_cells()
        }
        self._items_by_label = {}
        self._items_by_key = {}
        # Mapeo label de celda -> (col, row) para el preview 2D
        self._label_to_colrow = {}
        for j, _row in enumerate(self._resolved.rows):
            for i, _col in enumerate(self._resolved.columns):
                cell = self.layout.get_cell(i, j)
                if cell is not None:
                    resuelto = self._resolved_map.get(cell.label)
                    if resuelto is not None:
                        self._label_to_colrow[resuelto.label] = (i, j)
        self._pintar_arbol()
        self.preview.set_layout(
            self._resolved, self.outer_w, self.outer_h,
            selected=self._label_seleccionado(),
            reengroses=self.reengroses,
            entities=self._piezas_fisicas(),
            fondo=self._fondo,
            contenido_por_celda=self._contenido_por_celda,
            label_to_colrow=self._label_to_colrow)
        self.lbl_resumen.setText(self.resumen())
        self._poblar_elementos_reengrose()
        self._restaurar_seleccion()

    def _on_modo_changed(self, index):
        if self._building:
            return
        modo = "vanos" if index == 0 else "estructura"
        if modo == self.mode:
            return
        self.mode = modo
        if modo == "vanos":
            self._selected_key = (
                "cell", self.layout.columns[0].id,
                self.layout.rows[0].id)
        else:
            piezas = self._piezas_fisicas()
            self._selected_key = (
                ("piece", piezas[0]["key"]) if piezas
                else ("cell", self.layout.columns[0].id,
                      self.layout.rows[0].id))
        self._selected_data = None
        self._rebuild()


    def _vistos(self):
        if self._obj is not None:
            try:
                vistos, _apoyados = VDO_FR.cargar_exposicion(self._obj)
                if vistos:
                    return list(vistos)
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo leer la exposición del objeto")
        return [VDO_FR.FRENTE]

    def _cantos_pieza(self, rol, clave=None, es_reengrose=False):
        try:
            cantos = VDO_FIN.cantos_para_rol(
                rol, self._vistos(), tapa=self._tapa, base=self._base)
        except Exception as exc:
            App.Console.PrintWarning(f"[VDO] coco_arbol_widgets: cantos no calculados, usa FX: {exc}\n")
            cantos = {borde: "FX" for borde in VDO_FIN.BORDES}
        if es_reengrose and clave:
            datos = self.reengroses.get(clave)
            if datos:
                try:
                    mod = VDO_RE_MODIFICADOR.ReengroseModifier(datos)
                    plan = VDO_RE_DESPIECE.resolver_politica_cantos(
                        {"cantos": cantos}, mod)
                    cantos = (
                        plan.get("tira") or plan.get("bloque") or cantos)
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo resolver la política de cantos")
        return cantos

    def _piezas_fisicas(self):
        """Registro 2D de piezas físicas para árbol, header y preview."""
        t = float(self.thickness)
        outer_w = float(self.outer_w)
        outer_h = float(self.outer_h)
        fondo = float(self._fondo)
        inner_w = float(self.inner_w)
        inner_h = float(self.inner_h)
        lat_h = outer_h
        if self._tapa == "externo":
            lat_h -= t
        if self._base == "externo":
            lat_h -= t
        base_len = outer_w if self._base == "externo" else max(
            0.0, outer_w - 2.0 * t)
        techo_len = outer_w if self._tapa == "externo" else max(
            0.0, outer_w - 2.0 * t)

        piezas = []

        def agregar(clave, nombre, grupo, rol, largo, ancho, espesor,
                    caja, ejes):
            piezas.append({
                "key": clave,
                "nombre": nombre,
                "grupo": grupo,
                "rol": rol,
                "largo": float(largo),
                "ancho": float(ancho),
                "espesor": float(espesor),
                "caja": caja,
                "ejes": ejes,
                "cantos": self._cantos_pieza(rol, clave, False),
            })

        self._piezas_estructura(agregar, t, fondo, inner_w, inner_h, lat_h, base_len, techo_len)
        self._piezas_divisiones(agregar, fondo, t)
        return piezas

    def _piezas_estructura(self, agregar, t, fondo, inner_w, inner_h, lat_h, base_len, techo_len):
        agregar(
            "base", "Base", "horizontal", "base",
            base_len, fondo, t,
            {"nombre": "Base", "x": 0.0, "y": 0.0, "z": 0.0,
             "w": inner_w, "h": fondo, "d": t},
            {"largo": "x", "ancho": "y", "espesor": "z"})
        agregar(
            "techo", "Techo", "horizontal", "techo",
            techo_len, fondo, t,
            {"nombre": "Techo", "x": 0.0, "y": 0.0, "z": inner_h,
             "w": inner_w, "h": fondo, "d": t},
            {"largo": "x", "ancho": "y", "espesor": "z"})

        agregar(
            "lateral_izquierdo", "Lateral Izq", "vertical",
            "lateral_izquierdo", fondo, lat_h, t,
            {"nombre": "Lateral Izq", "x": 0.0, "y": 0.0, "z": 0.0,
             "w": t, "h": fondo, "d": inner_h},
            {"largo": "z", "ancho": "y", "espesor": "x"})
        agregar(
            "lateral_derecho", "Lateral Der", "vertical",
            "lateral_derecho", fondo, lat_h, t,
            {"nombre": "Lateral Der", "x": max(0.0, inner_w - t),
             "y": 0.0, "z": 0.0, "w": t, "h": fondo, "d": inner_h},
            {"largo": "z", "ancho": "y", "espesor": "x"})
        if self._tiene_fondo:
            agregar(
                "fondo", "Fondo", "vertical", "fondo",
                inner_w, inner_h, t,
                {"nombre": "Fondo", "x": 0.0, "y": max(0.0, fondo - t),
                 "z": 0.0, "w": inner_w, "h": t, "d": inner_h},
                {"largo": "x", "ancho": "z", "espesor": "y"})

    def _piezas_divisiones(self, agregar, fondo, t):
        h_seq = 0
        v_seq = 0
        for pieza in (self._resolved.pieces if self._resolved else []):
            clave = (
                f"division_x:{pieza.path}" if pieza.axis == AXIS_X
                else f"division_y:{pieza.path}")
            if pieza.axis == AXIS_Y:
                h_seq += 1
                nombre = f"H{h_seq} · {pieza.nombre}"
                agregar(
                    clave, nombre, "horizontal", "division_y",
                    pieza.w, fondo, t,
                    {"nombre": pieza.nombre, "x": pieza.x, "y": 0.0,
                     "z": pieza.z, "w": pieza.w, "h": fondo, "d": t},
                    {"largo": "x", "ancho": "y", "espesor": "z"})
            else:
                v_seq += 1
                nombre = f"V{v_seq} · {pieza.nombre}"
                agregar(
                    clave, nombre, "vertical", "division_x",
                    fondo, pieza.h, t,
                    {"nombre": pieza.nombre, "x": pieza.x, "y": 0.0,
                     "z": pieza.z, "w": t, "h": fondo, "d": pieza.h},
                    {"largo": "z", "ancho": "y", "espesor": "x"})

    def _pieza_por_clave(self, clave):
        for pieza in self._piezas_fisicas():
            if pieza["key"] == clave:
                return pieza
        return None

    def _reengroses_invasores(self, resuelto):
        if resuelto is None:
            return []
        x0, z0 = resuelto.nominal_x, resuelto.nominal_z
        x1 = x0 + resuelto.nominal_w
        z1 = z0 + resuelto.nominal_h
        invasores = []
        for clave, datos in self.reengroses.items():
            if not datos:
                continue
            pieza = self._pieza_por_clave(clave)
            if pieza is None:
                continue
            try:
                mod = VDO_RE_MODIFICADOR.ReengroseModifier(datos)
                geo = VDO_RE_GEOMETRIA.calcular_geometria_caja(
                    pieza["caja"], mod, pieza["ejes"])
            except Exception as exc:
                _LOG.debug("coco_arbol_widgets: reengrose malformado, se omite: %s", exc)
                continue
            for ref in geo.get("refuerzos") or []:
                rx0, rz0 = float(ref["x"]), float(ref["z"])
                rx1 = rx0 + float(ref["w"])
                rz1 = rz0 + float(ref["d"])
                if (min(x1, rx1) - max(x0, rx0) > 1e-6
                        and min(z1, rz1) - max(z0, rz0) > 1e-6):
                    invasores.append(pieza["nombre"])
                    break
        return invasores
