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
    try:
        spec = get_spec(module_key)
    except Exception as exc:
        import FreeCAD as App
        App.Console.PrintError(f"[VDO] {exc}\n")
        return None

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
        try:
            doc.openTransaction(
                f"Crear y colocar {spec.get('label', module_key)}")
            tx_propia = True
        except Exception as exc:
            import FreeCAD as App
            App.Console.PrintWarning(
                f"[VDO] No se pudo abrir transacción: {exc}\n")

    def cancelar():
        if tx_propia:
            try:
                doc.abortTransaction()
            except Exception:
                pass
        if obj is not None:
            try:
                if doc.getObject(obj.Name) is not None:
                    doc.removeObject(obj.Name)
            except Exception:
                pass
        try:
            doc.recompute()
        except Exception:
            pass

    def confirmar():
        try:
            doc.recompute()
        except Exception:
            pass
        if tx_propia:
            try:
                doc.commitTransaction()
            except Exception:
                pass

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

        try:
            obj.ViewObject.Visibility = False
        except Exception:
            pass

        panel_cls = resolver_panel(spec)
        estado = {"finalizado": False}

        def on_accept():
            if estado["finalizado"]:
                return
            estado["finalizado"] = True
            from freecad.vdo.core.vdo_ui_registry import obtener
            iniciar_colocacion = obtener("colocacion.iniciar")
            if iniciar_colocacion is not None:
                iniciar_colocacion(
                    obj,
                    on_done=confirmar,
                    on_cancel=cancelar,
                )

        def on_cancel():
            if estado["finalizado"]:
                return
            estado["finalizado"] = True
            cancelar()

        panel = panel_cls(
            obj,
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=False,
        )
        from freecad.vdo.core.vdo_ui_registry import obtener
        cerrar_activo = obtener("dialogo.cerrar_activo")
        if cerrar_activo is not None:
            cerrar_activo()
        mostrar = obtener("dialogo.mostrar")
        if mostrar is not None:
            mostrar(panel)
        return obj

    except Exception as exc:
        cancelar()
        import FreeCAD as App
        App.Console.PrintError(
            f"[VDO] Error creando módulo '{module_key}': {exc}\n")
        import traceback
        App.Console.PrintError(traceback.format_exc())
        return None
