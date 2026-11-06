"""Escritura en el objeto de cada bloque del panel COCO (D-75).

Medidas, anclaje y rotación, estructura (chasis), exposición y divisiones.
El orden de escritura lo fija CocoUnifiedTaskPanel._escribir_coco.
"""

import json

import FreeCAD as App

from freecad.vdo.cad.colocacion import aplicar_rotacion
from freecad.vdo.cad.propiedades import (
    anadir_propiedad_texto,
    asignar_propiedades,
)
from freecad.vdo.core import frames as VDO_FR
from freecad.vdo.datos.formularios import COCO_EXPOSICION


class CocoUnifiedEscrituraMixin:
    """Mixin del panel COCO: escritura de los bloques en el objeto."""

    def _asignar_dimensiones(self):
        # Campos simples desde la especificacion COCO_MEDIDAS (D-74).
        self.form_coco.interpretar_texto()
        for clave, prop in (("alto", "Alto"), ("ancho", "Ancho"),
                            ("fondo_modulo", "FondoModulo"),
                            ("espesor", "Espesor")):
            asignar_propiedades(self.obj, {prop: self.form_coco.valor(clave)})

    def _guardar_estructura(self):
        if hasattr(self, "box_chassis") and self.box_chassis is not None:
            cfg = self.box_chassis.getChassisConfig()
            enc_sup = cfg.get("encuentros", {}).get("superior_izq", "tapa_domina")
            enc_inf = cfg.get("encuentros", {}).get("inferior_izq", "lateral_domina")
            asignar_propiedades(self.obj, {"Tapa": "externo" if enc_sup == "tapa_domina" else "interno"})
            asignar_propiedades(self.obj, {"Base": "externo" if enc_inf == "base_domina" else "interno"})
            asignar_propiedades(self.obj, {"TieneFondo": bool(cfg.get("caras", {}).get("fondo", {}).get("activa", True))})

            base_info = cfg.get("base", {})
            if "altura" in base_info and hasattr(self.obj, "AltoZocalo"):
                try:
                    asignar_propiedades(self.obj, {"AltoZocalo": float(base_info["altura"])})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo establecer AltoZocalo")
            if "separacion_frente" in base_info and hasattr(self.obj, "DistanciaFrente"):
                try:
                    asignar_propiedades(self.obj, {"DistanciaFrente": float(base_info["separacion_frente"])})
                except Exception:
                    App.Console.PrintWarning(
                        "[VDO] No se pudo establecer DistanciaFrente")

            try:
                if hasattr(self.obj, "VDO_Chassis_JSON"):
                    asignar_propiedades(self.obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
                elif hasattr(self.obj, "addProperty"):
                    anadir_propiedad_texto(self.obj, "VDO_Chassis_JSON", "VDO",
                                       "Configuración semiótica de Capa 1")
                    asignar_propiedades(self.obj, {"VDO_Chassis_JSON": json.dumps(cfg)})
            except Exception:
                App.Console.PrintWarning(
                    "[VDO] No se pudo persistir VDO_Chassis_JSON")

    def _asignar_anclaje_rotacion(self):
        anclaje = self.form_coco.valor("anclaje")
        if anclaje:
            asignar_propiedades(self.obj, {"VDO_Anclaje": anclaje})
        aplicar_rotacion(self.obj, self.form_coco.valor("rotacion"))

    def _guardar_exposicion(self):
        vistos = []
        apoyados = []
        for lado, _espec in COCO_EXPOSICION:
            estado = self.form_coco.valor(f"exp_{lado}")
            if estado == "visto":
                vistos.append(lado)
            elif estado == "apoyado":
                apoyados.append(lado)
        VDO_FR.guardar_exposicion(self.obj, vistos, apoyados)

    def _guardar_divisiones(self):
        if not hasattr(self.obj, "VDO_Divisiones"):
            anadir_propiedad_texto(
                self.obj, "VDO_Divisiones", "Divisiones",
                "Matriz de vanos v2 (JSON)")
        asignar_propiedades(self.obj, {"VDO_Divisiones": self.editor_divisiones.dumps()})
        asignar_propiedades(self.obj, {"VDO_Reengrose_JSON": (
            self.editor_divisiones.dumps_reengroses())})
        asignar_propiedades(self.obj, {"VDO_Contenido_JSON": (
            self.editor_divisiones.dumps_contenido())})
