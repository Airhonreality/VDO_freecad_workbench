#!/usr/bin/env python3
"""
export_cutting_list.py
Exporta lista de corte desde modelo VDO a CSV para OpenCutList

Sin hardcode: Lee especificaciones desde datos/manifest.json
Filtro: Solo exporta paneles de melamina (excluye muros, paneles BIM, etc)
"""

try:
    import FreeCAD as App
    import FreeCADGui
except ImportError:
    raise ImportError("Este módulo requiere FreeCAD con GUI") from None

from freecad.vdo.cad.lista_corte import extraer_piezas_del_documento


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
    from freecad.vdo.ui import cutting_list_preview
    cutting_list_preview.main(modo=modo)

    return True


if __name__ == "__main__":
    main(modo="todo")
