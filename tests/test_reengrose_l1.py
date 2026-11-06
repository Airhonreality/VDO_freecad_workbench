import os
import unittest

import FreeCAD as App
import Part

try:
    from PySide import QtWidgets
except BaseException:
    QtWidgets = None

from freecad.vdo.cad import panel as P
from freecad.vdo.core import vdo_reengrose as R
try:
    from freecad.vdo.ui import vdo_export_cutting_list as E
except ImportError:
    E = None  # sin FreeCADGui el módulo se niega a cargar; los tests que lo usan lo exigen

try:
    from freecad.vdo.ui.vdo_panel_task import PanelTaskPanel
except ImportError:
    PanelTaskPanel = None

from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_gui, requiere_qt



def _sin_solapes(shape):
    solidos = list(shape.Solids)
    for i in range(len(solidos)):
        for j in range(i + 1, len(solidos)):
            if solidos[i].common(solidos[j]).Volume > 1e-6:
                return False
    return True


@requiere_freecad
class ReengroseL1Tests(unittest.TestCase):
    def setUp(self):
        self.doc = App.newDocument("TestReengroseL1")

    def tearDown(self):
        App.closeDocument(self.doc.Name)

    def crear(self, nombre, **reengrose):
        obj = P.crear_pieza(self.doc, {
            "nombre": nombre,
            "orientacion": "vertical",
            "largo": 600,
            "ancho": 400,
            "espesor": 18,
            "usar_params": False,
            "cantos": {"norte": "RIG"},
            "reengrose": dict({"activo": True}, **reengrose),
        })
        self.doc.recompute()
        return obj

    def test_independiente(self):
        obj = self.crear(
            "P_Ind", modo_fabricacion="independiente", ancho=70)
        self.assertTrue(obj.Shape.isValid())
        self.assertEqual(len(obj.Shape.Solids), 2)
        self.assertTrue(_sin_solapes(obj.Shape))
        piezas = E.extraer_piezas_panel(obj)
        self.assertEqual(len(piezas), 2)
        self.assertEqual(piezas[0]["operacion"], "Cantear por separado")

    def test_pacha_parcial(self):
        obj = self.crear(
            "P_Pacha", modo_fabricacion="pacha", ancho=70)
        self.assertTrue(obj.Shape.isValid())
        self.assertEqual(len(obj.Shape.Solids), 2)
        self.assertTrue(_sin_solapes(obj.Shape))
        piezas = E.extraer_piezas_panel(obj)
        self.assertEqual(piezas[0]["grupo_pacha"], "Pacha_P_Pacha")
        self.assertEqual(piezas[0]["cantos"]["norte"], "FX")
        self.assertEqual(piezas[0]["cantos_bloque"]["norte"], "RIG")

    def test_pacha_total(self):
        obj = self.crear(
            "P_Total", modo_fabricacion="pacha", alcance="total")
        self.assertTrue(obj.Shape.isValid())
        self.assertEqual(len(obj.Shape.Solids), 2)
        piezas = E.extraer_piezas_panel(obj)
        self.assertEqual(piezas[1]["largo"], 600.0)
        self.assertEqual(piezas[1]["ancho"], 400.0)

    def test_panel_viejo_sin_propiedades(self):
        obj = self.doc.addObject("Part::FeaturePython", "P_Viejo")
        P.PanelFeature(obj)
        obj.Largo = 300
        obj.Ancho = 200
        obj.Espesor = 18
        self.doc.recompute()
        self.assertTrue(obj.Shape.isValid())
        P.add_reengrose_props(obj)
        self.assertIn("VDO_Reengrose_Activo", obj.PropertiesList)

    def test_desde_objeto(self):
        obj = self.crear(
            "P_Json", modo_fabricacion="independiente",
            orientacion="transversal", ancho=55)
        mod = R.desde_objeto(obj)
        self.assertTrue(mod.activo)
        self.assertEqual(mod.orientacion, "transversal")
        self.assertEqual(mod.ancho, 55.0)

    @requiere_qt
    def test_ui_tooltips_y_accept(self):
        qapplication()
        obj = self.crear(
            "P_UI", modo_fabricacion="independiente", ancho=70)
        panel = PanelTaskPanel(obj=obj, auto_transaction=False)
        self.assertTrue(panel.chk_reengrose.isChecked())
        self.assertTrue(panel.chk_reengrose.toolTip())
        self.assertTrue(panel.spin_re_ancho.toolTip())
        panel.chk_reengrose.setChecked(False)
        self.assertFalse(panel.spin_re_ancho.isEnabled())
        panel.chk_reengrose.setChecked(True)
        self.assertTrue(panel.spin_re_ancho.isEnabled())
        panel.spin_re_ancho.setValue(55)
        self.assertTrue(panel.accept())
        self.doc.recompute()
        self.assertAlmostEqual(float(obj.VDO_Reengrose_Ancho), 55.0)

