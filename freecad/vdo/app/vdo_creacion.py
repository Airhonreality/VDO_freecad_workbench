# -*- coding: utf-8 -*-
# =====================================================================
# app/vdo_creacion.py
# Caso de uso: crear módulo VDO (movido de core/vdo_creation_flow.py en F4).
#
# Orquesta: obtiene el documento (cad/guardian), crea el objeto vía la
# factory del módulo (core/module_specs), añade propiedades comunes
# (cad/propiedades) y abre el panel de colocación (UI, vía registro).
# =====================================================================

from __future__ import annotations

import re

from freecad.vdo.app.puertos import Documento
from freecad.vdo.cad.vdo_guardian import vdo_guard as _cad_vdo_guard
from freecad.vdo.cad.propiedades import add_common_props as _cad_add_common_props
from freecad.vdo.core.vdo_module_specs import get_spec, resolver_panel
from freecad.vdo.core.vdo_view_base import diagnostico_viewprovider


def _sanitizar_nombre(nombre: str) -> str:
    nombre = re.sub(r"[^A-Za-z0-9_]", "_", str(nombre or "Modulo"))
    if not nombre or nombre[0].isdigit():
        nombre = "Modulo_" + nombre
    return nombre


def _nombre_unico(doc: Documento, base: str) -> str:
    base = _sanitizar_nombre(base)
    if doc.getObject(base) is None:
        return base
    i = 1
    while doc.getObject(f"{base}_{i:03d}") is not None:
        i += 1
    return f"{base}_{i:03d}"


def crear_modulo_interactivo(module_key: str, config: dict | None = None):
    """Crea un módulo VDO y lo coloca con el mouse.

    En FreeCADCmd (sin GUI) crea el módulo y lo deja en el origen,
    sin panel ni colocación interactiva.
    """
    spec = get_spec(module_key)

    doc = _cad_vdo_guard()
    if doc is None:
        import FreeCAD as App
        App.Console.PrintError(
            "[VDO] No hay documento activo para crear el módulo.\n")
        return None

    cfg = dict(spec.get("config", {}))
    if config:
        cfg.update(config)
    cfg["nombre"] = _nombre_unico(
        doc, cfg.get("nombre") or spec.get("label", module_key))

    obj = None
    tx_propia = False
    if not doc.HasPendingTransaction:
        doc.openTransaction(
            f"Crear y colocar {spec.get('label', module_key)}")
        tx_propia = True

    def cancelar():
        if tx_propia:
            doc.abortTransaction()
        if obj is not None:
            if doc.getObject(obj.Name) is not None:
                doc.removeObject(obj.Name)
        doc.recompute()

    def confirmar():
        doc.recompute()
        if tx_propia:
            doc.commitTransaction()

    try:
        obj = spec["factory_fn"](cfg)
        if obj is None:
            raise RuntimeError("La factory no devolvió un objeto")

        _cad_add_common_props(obj)
        import FreeCAD as App
        if not App.GuiUp:
            confirmar()
            return obj

        App.Console.PrintMessage(
            "[VDO] " + diagnostico_viewprovider(obj) + "\n")

        obj.ViewObject.Visibility = False

        panel_cls = resolver_panel(spec)
        estado = {"finalizado": False}

        def on_accept():
            if estado["finalizado"]:
                return
            estado["finalizado"] = True
            # La colocacion se maneja desde app/composicion (F6).
            if confirmar is not None:
                confirmar()

        def on_cancel():
            if estado["finalizado"]:
                return
            estado["finalizado"] = True
            cancelar()

        panel_cls = resolver_panel(spec)
        # La vista/señal del panel se conecta desde app/composicion (F6).
        return obj
