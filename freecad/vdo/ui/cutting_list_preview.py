#!/usr/bin/env python3
"""
cutting_list_preview.py
Preview visual antes de exportar a OpenCutList

Flujo:
  1. Usuario elige: Selección / Grupo / Todo
  2. Preview colorea piezas en ROJO
  3. Task Panel muestra confirmación
  4. Usuario navega 3D, verifica
  5. Click "Aceptar" → CSV generado
"""

import logging
import sys
from pathlib import Path

try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError:
    raise ImportError("Este módulo requiere FreeCAD con GUI") from None

from freecad.vdo.core import manifest
from freecad.vdo.qt_compat import QtCore, QtWidgets
from freecad.vdo.ui import export_cutting_list, tema

_LOG = logging.getLogger(__name__)


class CuttingListPreviewPanel:
    """Task Panel para preview y confirmación"""

    def __init__(self, piezas, modo):
        self.piezas = piezas
        self.modo = modo
        self.piezas_coloreadas = []
        self._colores_originales = {}

        # Crear form
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        self._crear_cabecera(layout, modo, piezas)
        total_costo = self._crear_tabla(layout, piezas)
        self._crear_resumen(layout, total_costo)
        self._crear_botones(layout)

        self.form.setLayout(layout)
        self.colorear_piezas()

    def _crear_cabecera(self, layout, modo, piezas):
        # Header
        header = QtWidgets.QLabel()
        header.setText(f"<b>📊 Preview Exportación - {modo.upper()}</b>")
        tema.aplicar_estilo(header, tema.ESTILO_TITULO_14PX_OSCURO)
        layout.addWidget(header)

        # Info
        info = QtWidgets.QLabel()
        info.setText(f"Se va a exportar <b>{len(piezas)}</b> piezas de melamina")
        layout.addWidget(info)

    def _crear_tabla(self, layout, piezas):
        # Tabla de piezas
        self.tabla = QtWidgets.QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Material", "L×A×E", "Cantidad", "Costo"])  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
        self.tabla.setRowCount(len(piezas))
        self.tabla.setMaximumHeight(200)

        total_costo = 0

        for row, pieza in enumerate(piezas):
            nombre = QtWidgets.QTableWidgetItem(pieza.get("nombre", "???"))
            mat_id = pieza.get("material_ref", "")
            material = manifest.get_material(mat_id)
            mat_str = material["nombre"] if material else mat_id
            mat_item = QtWidgets.QTableWidgetItem(mat_str)

            dims = f"{pieza.get('largo', 0)}×{pieza.get('ancho', 0)}×{pieza.get('espesor', 0)}"  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
            dims_item = QtWidgets.QTableWidgetItem(dims)

            qty = QtWidgets.QTableWidgetItem(str(pieza.get("cantidad", 1)))

            # Costo
            if material:
                area_m2 = (pieza["largo"] * pieza["ancho"]) / 1000000
                costo = manifest.calcular_costo_material(mat_id, area_m2)
                total_costo += costo
                costo_item = QtWidgets.QTableWidgetItem(f"${costo:.2f}")
            else:
                costo_item = QtWidgets.QTableWidgetItem("???")

            self.tabla.setItem(row, 0, nombre)
            self.tabla.setItem(row, 1, mat_item)
            self.tabla.setItem(row, 2, dims_item)
            self.tabla.setItem(row, 3, qty)
            self.tabla.setItem(row, 4, costo_item)

        self.tabla.resizeColumnsToContents()
        layout.addWidget(self.tabla)
        return total_costo

    def _crear_resumen(self, layout, total_costo):
        # Resumen
        resumen = QtWidgets.QLabel()
        resumen.setText(f"<b>💰 Costo total material: ${total_costo:.2f}</b>")
        tema.aplicar_estilo(resumen, tema.ESTILO_RESUMEN_AZUL)
        layout.addWidget(resumen)

        # Instrucciones
        instrucciones = QtWidgets.QLabel()
        instrucciones.setText(
            "✅ Las piezas están <span style='color: red;'>COLOREADAS EN ROJO</span> en el 3D viewer\n"
            "👁️ Navega para verificar que se van a exportar las piezas correctas\n"
            "📋 Luego haz click en 'Aceptar' para generar el CSV"
        )
        layout.addWidget(instrucciones)

        layout.addSpacing(10)

    def _crear_botones(self, layout):
        # Botones
        btn_layout = QtWidgets.QHBoxLayout()

        btn_cancelar = QtWidgets.QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.cancelar)
        btn_layout.addWidget(btn_cancelar)

        btn_aceptar = QtWidgets.QPushButton("✅ Aceptar - Generar CSV")
        tema.aplicar_estilo(btn_aceptar, tema.ESTILO_BOTON_EXITO)
        btn_aceptar.clicked.connect(self.aceptar)
        btn_layout.addWidget(btn_aceptar)

        layout.addLayout(btn_layout)

    def colorear_piezas(self):
        """Colorea en rojo las piezas que se van a exportar"""
        doc = App.ActiveDocument

        # Nombres de las piezas a exportar. Un panel exportable comparte
        # Label con el objeto; un contenedor COCO exporta piezas cuyo
        # nombre es "<Label>_<sufijo>".
        piezas_ids = {pieza.get("nombre") for pieza in self.piezas if pieza.get("nombre")}

        for obj in doc.Objects:
            if not hasattr(obj, "VDO_Tipo"):
                continue

            etiqueta = obj.Label
            exportar = etiqueta in piezas_ids or any(
                nombre.startswith(etiqueta + "_") for nombre in piezas_ids)

            if obj.Name not in self._colores_originales:
                self._colores_originales[obj.Name] = obj.ViewObject.ShapeColor

            if exportar:
                # ROJO: se va a exportar
                obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0, 0.8)
                self.piezas_coloreadas.append(obj)
            else:
                # GRIS: no se exporta
                obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7, 0.5)

        App.Console.PrintMessage(f"✅ {len(self.piezas_coloreadas)} piezas coloreadas en ROJO")

    def aceptar(self):
        """Genera CSV y cierra dialog"""
        App.Console.PrintMessage(f"\n✅ Exportando {len(self.piezas)} piezas...")

        # Restaurar colores
        self._restaurar_colores()

        # Diálogo para elegir ubicación (con padre = ventana principal de FreeCAD)
        try:
            parent = Gui.getMainWindow()
        except Exception as exc:
            _LOG.warning("cutting_list_preview: ventana padre no obtenida: %s", exc)
            parent = None

        # Ruta sugerida en el HOME (siempre existe); NO usar ~/Desktop
        ruta_sugerida = str(Path.home() / "vdo_cutting_list.csv")

        try:
            output_file, _ = QtWidgets.QFileDialog.getSaveFileName(
                parent,
                "Guardar lista de corte CSV",
                ruta_sugerida,
                "CSV Files (*.csv);;All Files (*)"
            )
        except Exception as e:
            App.Console.PrintMessage(f"❌ Error abriendo el diálogo de archivo: {e}")
            App.Console.PrintError(f"[VDO] Error abriendo diálogo: {e}\n")
            return

        if not output_file:
            App.Console.PrintMessage("❌ Exportación cancelada (o el diálogo se cerró sin elegir archivo)")
            App.Console.PrintWarning("[VDO] Exportación cancelada\n")
            Gui.Control.closeDialog()
            return

        # Generar CSV
        try:
            ok = export_cutting_list.generar_csv_opencutlist(
                self.piezas, output_file)
        except Exception as e:
            App.Console.PrintMessage(f"❌ Error generando CSV: {e}")
            App.Console.PrintError(f"[VDO] Error generando CSV: {e}\n")
            return

        if ok:
            App.Console.PrintMessage(f"✅ CSV generado: {output_file}")
            App.Console.PrintMessage("\n📌 Próximo paso: Usa el archivo CSV con tu optimizador de corte")
            App.Console.PrintMessage(f"[VDO] Lista de corte exportada: {output_file}\n")

        Gui.Control.closeDialog()

    def cancelar(self):
        """Cancela y restaura colores"""
        App.Console.PrintMessage("❌ Exportación cancelada")
        self._restaurar_colores()
        Gui.Control.closeDialog()

    def _restaurar_colores(self):
        """Restaura los colores originales guardados antes del preview."""
        doc = App.ActiveDocument
        for obj in doc.Objects:
            if not hasattr(obj, "VDO_Tipo"):
                continue
            color = self._colores_originales.get(obj.Name)
            if color is None:
                # Fallback sólo si el objeto no fue coloreado previamente.
                color = (0.8, 0.8, 0.8, 1.0)
            obj.ViewObject.ShapeColor = color
        self._colores_originales.clear()


def mostrar_preview(piezas, modo):
    """Muestra el panel de preview"""
    panel = CuttingListPreviewPanel(piezas, modo)
    Gui.Control.showDialog(panel)


def main(modo="todo"):
    """
    Modo: "seleccion" | "grupo" | "todo"
    """
    App.Console.PrintMessage("=" * 70)
    App.Console.PrintMessage(f"🔍 CUTTING LIST PREVIEW - {modo.upper()}")
    App.Console.PrintMessage("=" * 70)

    doc = App.ActiveDocument
    if not doc:
        App.Console.PrintMessage("❌ No hay documento activo")
        return False

    # Extraer piezas según modo (lógica unificada: paneles + contenedores)
    App.Console.PrintMessage(f"\n📦 Extrayendo piezas (modo: {modo})...")
    piezas = export_cutting_list.extraer_piezas_del_documento(modo)

    if not piezas:
        App.Console.PrintMessage("❌ No se encontraron piezas de melamina para exportar")
        return False

    App.Console.PrintMessage(f"✅ {len(piezas)} piezas encontradas")

    # Mostrar preview
    App.Console.PrintMessage("\n🎨 Mostrando preview (piezas en ROJO)...")
    mostrar_preview(piezas, modo)

    return True


if __name__ == "__main__":
    main(modo="todo")
