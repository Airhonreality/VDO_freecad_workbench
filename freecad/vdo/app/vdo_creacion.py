# =====================================================================
# app/vdo_creacion.py
# Caso de uso: crear módulo VDO (movido de core/vdo_creation_flow.py en F4).
#
# Orquesta: obtiene el documento (cad/guardian), crea el objeto vía la
# factory del módulo (core/module_specs), añade propiedades comunes
# (cad/propiedades), abre el panel de configuración y, al aceptarlo,
# inicia la colocación con clic.
#
# app/ no importa ui/. La interfaz llega por parámetro (abrir_panel,
# colocar) desde commands.py, que es la entrada y sí puede importar ui/.
# Sin interfaz (FreeCADCmd, pruebas) el módulo se confirma en el origen.
# =====================================================================

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from freecad.vdo.app.puertos import Documento
from freecad.vdo.cad.propiedades import add_common_props as _cad_add_common_props
from freecad.vdo.cad.propiedades import ocultar_vista as _cad_ocultar_vista
from freecad.vdo.cad.vdo_guardian import vdo_guard as _cad_vdo_guard
from freecad.vdo.core.vdo_module_specs import get_spec
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


def crear_modulo_interactivo(
    module_key: str,
    config: dict[str, Any] | None = None,
    *,
    abrir_panel: Callable[..., None] | None = None,
    colocar: Callable[..., None] | None = None,
) -> Any:
    """Crea un módulo VDO, abre su panel y, al aceptarlo, lo coloca con clic.

    abrir_panel(spec, obj, on_accept, on_cancel): muestra el panel de configuración.
    colocar(obj, on_done, on_cancel): inicia la colocación con el mouse.
    Si no se pasan (FreeCADCmd, pruebas), el módulo se confirma en el origen.
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

    tx_propia = False
    if not doc.HasPendingTransaction:
        doc.openTransaction(
            f"Crear y colocar {spec.get('label', module_key)}")
        tx_propia = True

    obj = spec["factory_fn"](doc, cfg)
    if obj is None:
        raise RuntimeError("La factory no devolvió un objeto")

    def cancelar() -> None:
        if tx_propia:
            doc.abortTransaction()
        if doc.getObject(obj.Name) is not None:
            doc.removeObject(obj.Name)
        doc.recompute()

    def confirmar() -> None:
        doc.recompute()
        if tx_propia:
            doc.commitTransaction()

    _cad_add_common_props(obj)

    if abrir_panel is None or colocar is None:
        confirmar()
        return obj

    import FreeCAD as App
    App.Console.PrintMessage("[VDO] " + diagnostico_viewprovider(obj) + "\n")
    _cad_ocultar_vista(obj)

    estado = {"aceptado": False}

    def on_accept() -> None:
        # Un panel puede disparar Aceptar dos veces: solo la primera cuenta.
        if estado["aceptado"]:
            return
        estado["aceptado"] = True
        colocar(obj, on_done=confirmar, on_cancel=cancelar)

    def on_cancel() -> None:
        if estado["aceptado"]:
            return
        estado["aceptado"] = True
        cancelar()

    try:
        abrir_panel(spec, obj, on_accept, on_cancel)
    except (RuntimeError, ValueError, TypeError, KeyError):
        # Error de la interfaz: se deshace lo creado y se propaga (no se oculta).
        cancelar()
        raise
    return obj
