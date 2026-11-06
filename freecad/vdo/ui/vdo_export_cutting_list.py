#!/usr/bin/env python3
"""
vdo_export_cutting_list.py
Exporta lista de corte desde modelo VDO a CSV para OpenCutList

Sin hardcode: Lee especificaciones desde vdo_manifest.json
Filtro: Solo exporta paneles de melamina (excluye muros, paneles BIM, etc)
"""

import csv
import sys
from pathlib import Path

try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError:
    raise ImportError("Este módulo requiere FreeCAD con GUI") from None

# Importar loader
from freecad.vdo.core import vdo_manifest
from freecad.vdo.core import vdo_reengrose_despiece as VDO_RE_DESPIECE
from freecad.vdo.core import vdo_reengrose_modelo as VDO_RE_MODELO
from freecad.vdo.core import vdo_reengrose_modificador as VDO_RE_MODIFICADOR
from freecad.vdo.datos.valores import MELAMINA_ESTANDAR


def _datos_panel(obj):
    orientacion = getattr(obj, "VDO_Orientacion", "horizontal")
    if hasattr(obj, "Largo"):
        largo = float(obj.Largo)
        ancho = float(obj.Ancho)
        espesor = float(obj.Espesor)
    else:
        length = obj.Length if hasattr(obj, "Length") else 0
        width = obj.Width if hasattr(obj, "Width") else 0
        height = obj.Height if hasattr(obj, "Height") else 0
        if orientacion == "vertical":
            largo, ancho, espesor = height, width, length
        else:
            largo, ancho, espesor = length, width, height

    cantos = {}
    for direccion in ("Norte", "Sur", "Este", "Oeste"):
        cantos[direccion.lower()] = getattr(
            obj, f"VDO_Canto_{direccion}", "FX")
    return largo, ancho, espesor, cantos, orientacion


def extraer_piezas_panel(obj):
    """Extrae las subpiezas fisicas del panel (base + reengrose/pacha)."""
    largo, ancho, espesor, cantos, orientacion = _datos_panel(obj)
    try:
        mod = VDO_RE_MODIFICADOR.desde_objeto(obj)
    except Exception:
        mod = VDO_RE_MODIFICADOR.ReengroseModifier()
    try:
        piezas = VDO_RE_DESPIECE.despiece_panel(
            obj.Label, largo, ancho, espesor, mod, cantos=cantos,
            material_ref=getattr(obj, "VDO_Material_Ref", MELAMINA_ESTANDAR),
            orientacion=orientacion)
    except VDO_RE_MODELO.ReengroseError as exc:
        App.Console.PrintMessage(f"⚠️  Reengrose inválido en '{obj.Label}': {exc}")
        piezas = VDO_RE_DESPIECE.despiece_panel(
            obj.Label, largo, ancho, espesor, VDO_RE_MODIFICADOR.ReengroseModifier(),
            cantos=cantos,
            material_ref=getattr(obj, "VDO_Material_Ref", MELAMINA_ESTANDAR),
            orientacion=orientacion)
    for pieza in piezas:
        pieza.setdefault("herrajes", getattr(obj, "VDO_Hardware", ""))
        pieza.setdefault("herrajes_qty", getattr(obj, "VDO_HardwareQty", 0))
    return piezas


def extraer_piezas_del_documento(modo="todo"):
    """
    Extrae piezas de melamina del documento

    modo: "todo" | "seleccion" | "grupo"
    Filtro: Paneles (VDO_Tipo == "panel") y Contenedores (VDO_Tipo == "contenedor")
    Excluye: muros, paneles BIM, otros objetos
    """
    import json

    doc = App.ActiveDocument
    if not doc:
        App.Console.PrintMessage("❌ No hay documento activo")
        return []

    piezas = []

    if modo == "seleccion":
        _piezas_seleccion(piezas, json)
    elif modo == "grupo":
        # Solo el módulo activo
        modulo = doc.ActiveObject
        if modulo and hasattr(modulo, "VDO_Tipo"):
            if modulo.VDO_Tipo == "panel":
                piezas.extend(extraer_piezas_panel(modulo))
            elif modulo.VDO_Tipo == "contenedor":
                if hasattr(modulo, "VDO_Paneles_JSON") and modulo.VDO_Paneles_JSON:
                    try:
                        paneles_json = json.loads(modulo.VDO_Paneles_JSON)
                        piezas.extend(paneles_json)
                    except Exception as exc:
                        App.Console.PrintWarning(
                            f"[VDO] JSON de paneles invalido: {exc}\n")

    else:  # "todo":
        _piezas_todo(piezas, json, doc)

    return piezas


def _piezas_seleccion(piezas, json):
    # Solo objetos seleccionados
    selected = Gui.Selection.getSelectionEx()
    for sel in selected:
        obj = sel.Object
        if hasattr(obj, "VDO_Tipo"):
            if obj.VDO_Tipo == "panel":
                piezas.extend(extraer_piezas_panel(obj))
            elif obj.VDO_Tipo == "contenedor":
                # Extraer paneles del contenedor (ej: COCO_4C)
                if hasattr(obj, "VDO_Paneles_JSON") and obj.VDO_Paneles_JSON:
                    try:
                        paneles_json = json.loads(obj.VDO_Paneles_JSON)
                        piezas.extend(paneles_json)
                    except Exception as exc:
                        App.Console.PrintWarning(
                            f"[VDO] JSON de paneles invalido: {exc}\n")


def _piezas_todo(piezas, json, doc):
    # Todas las piezas del documento
    for obj in doc.Objects:
        if hasattr(obj, "VDO_Tipo"):
            if obj.VDO_Tipo == "panel":
                piezas.extend(extraer_piezas_panel(obj))
            elif obj.VDO_Tipo == "contenedor":
                # Extraer paneles del contenedor (ej: COCO_4C)
                if hasattr(obj, "VDO_Paneles_JSON") and obj.VDO_Paneles_JSON:
                    try:
                        paneles_json = json.loads(obj.VDO_Paneles_JSON)
                        piezas.extend(paneles_json)
                    except Exception as exc:
                        App.Console.PrintWarning(
                            f"[VDO] JSON de paneles invalido: {exc}\n")


def _escribir_cabecera_csv(writer):
    # Header para OpenCutList
    writer.writerow([
        "Length",
        "Width",
        "Thickness",
        "Quantity",
        "Material",
        "Name",
        "Unit Cost",
        "Total Cost",
        "Edge N",
        "Edge S",
        "Edge E",
        "Edge W",
        "Group",
        "Operation"
    ])


def _escribir_piezas_csv(writer, piezas):
    total_costo = 0
    for pieza in piezas:
        mat_id = pieza["material_ref"]
        material = vdo_manifest.get_material(mat_id)

        if not material:
            App.Console.PrintMessage(f"⚠️  Material no encontrado: {mat_id}")
            continue

        # Construir string de material (sin hardcode)
        # Prioriza el espesor real de la pieza (multi-espesor:
        # cajón caja=16, fondo=6, fachada=18); fallback al
        # primer espesor del material.
        espesor_pieza = pieza.get("espesor") or 0
        if espesor_pieza:
            espesor = espesor_pieza
        else:
            espesor = material["espesores"][0] if material["espesores"] else 18
        material_str = f"{espesor}mm_{material['referencia']}_{material['tipo']}"

        # Calcular costo
        area_m2 = (pieza["largo"] * pieza["ancho"]) / 1000000
        costo_unitario = vdo_manifest.calcular_costo_material(mat_id, area_m2)
        costo_total = costo_unitario * pieza["cantidad"]
        total_costo += costo_total

        cantos = pieza.get("cantos", {})
        writer.writerow([
            pieza["largo"],
            pieza["ancho"],
            espesor,
            pieza["cantidad"],
            material_str,
            pieza["nombre"],
            f"{costo_unitario:.2f}",
            f"{costo_total:.2f}",
            cantos.get("norte", "FX"),
            cantos.get("sur", "FX"),
            cantos.get("este", "FX"),
            cantos.get("oeste", "FX"),
            pieza.get("grupo", ""),
            pieza.get("operacion", "")
        ])
    return total_costo


def _escribir_fila_total_csv(writer, total_costo):
    # Fila de total
    writer.writerow([])
    writer.writerow([
        "TOTAL COSTO MATERIAL", "", "", "", "", "", "",
        f"{total_costo:.2f}", "", "", "", "", "", ""])


def generar_csv_opencutlist(piezas, output_path):
    """Genera CSV compatible con OpenCutList"""

    if not vdo_manifest.get_loader():
        App.Console.PrintMessage("❌ No se pudo cargar configuración VDO")
        return False

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            _escribir_cabecera_csv(writer)

            total_costo = _escribir_piezas_csv(writer, piezas)

            _escribir_fila_total_csv(writer, total_costo)

        App.Console.PrintMessage(f"✅ Exportado: {output_path}")
        App.Console.PrintMessage(f"💰 Costo total de material: ${total_costo:.2f}")
        return True

    except Exception as e:
        App.Console.PrintMessage(f"❌ Error escribiendo CSV: {e}")
        return False


def main(modo="todo"):
    """Main: Extrae, previsualia, exporta"""
    App.Console.PrintMessage("=" * 70)
    App.Console.PrintMessage(f"📊 VDO EXPORT CUTTING LIST - {modo.upper()}")
    App.Console.PrintMessage("=" * 70)

    # Extraer piezas
    App.Console.PrintMessage(f"\n🔍 Extrayendo piezas ({modo})...")
    piezas = extraer_piezas_del_documento(modo)

    if not piezas:
        App.Console.PrintMessage("⚠️  No se encontraron piezas de melamina para exportar")
        return False

    App.Console.PrintMessage(f"✅ {len(piezas)} piezas encontradas")

    # Mostrar preview (colorear y confirmar)
    App.Console.PrintMessage("\n🎨 Mostrando preview...")
    from freecad.vdo.ui import vdo_cutting_list_preview
    vdo_cutting_list_preview.main(modo=modo)

    return True


if __name__ == "__main__":
    main(modo="todo")
