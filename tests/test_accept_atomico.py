"""
tests/test_accept_atomico.py
Regresión F2 (D-88): si el accept de un panel falla a mitad de la escritura o
del recálculo, el objeto debe quedar con exactamente las propiedades que tenía
antes del accept. Un test por panel: zócalo, panel, puerta, cajón y coco.

El fallo se fuerza parcheando el recálculo del módulo de UI, que es la última
escritura del accept. La foto son los valores de las propiedades del objeto con
igualdad por valor: se excluyen las de forma (Part::PropertyPartShape, no se
pueden escribir) y las de objeto sin __eq__ (material, Proxy), que no se pueden
comparar por valor.
"""

import contextlib
import unittest
from unittest import mock

try:
    import FreeCAD as App
except ImportError:  # sin FreeCAD la clase se omite (requiere_freecad)
    App = None

from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_qt

_DOC = "DocAcceptAtomicoVDO"
_FALLO = "fallo forzado de prueba"


def _foto(obj):
    """Valores de las propiedades del objeto con igualdad por valor."""
    foto = {}
    for nombre in obj.PropertiesList:
        if obj.getTypeIdOfProperty(nombre) == "Part::PropertyPartShape":
            continue
        valor = getattr(obj, nombre)
        if type(valor).__eq__ is object.__eq__:
            continue
        foto[nombre] = valor
    return foto


@requiere_freecad
class TestAcceptAtomico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        qapplication()

    def setUp(self):
        with contextlib.suppress(BaseException):
            App.closeDocument(_DOC)
        self.doc = App.newDocument(_DOC)
        App.setActiveDocument(self.doc.Name)

    def tearDown(self):
        with contextlib.suppress(BaseException):
            App.closeDocument(_DOC)

    def _comprobar_accept_atomico(self, modulo_ui, obj, panel):
        antes = _foto(obj)
        with mock.patch.object(modulo_ui, "recalcular_activo",
                               side_effect=RuntimeError(_FALLO)):
            resultado = panel.accept()
        self.assertFalse(resultado)
        self.assertEqual(_foto(obj), antes)

    @requiere_qt
    def test_zocalo(self):
        from freecad.vdo.cad.zocalo import make_zocalo
        from freecad.vdo.ui import zocalo_task
        from freecad.vdo.ui.zocalo_task import ZocaloTaskPanel
        obj = make_zocalo(self.doc, {"nombre": "Z_Atomico"})
        panel = ZocaloTaskPanel(obj=obj, auto_transaction=False)
        panel.spin_ancho.setValue(700.0)
        self._comprobar_accept_atomico(zocalo_task, obj, panel)

    @requiere_qt
    def test_panel(self):
        from freecad.vdo.cad import panel as P
        from freecad.vdo.ui import panel_task
        from freecad.vdo.ui.panel_task import PanelTaskPanel
        obj = P.crear_pieza(self.doc, {
            "nombre": "P_Atomico", "orientacion": "vertical",
            "largo": 600, "ancho": 400, "espesor": 18})
        panel = PanelTaskPanel(obj=obj, auto_transaction=False)
        self._comprobar_accept_atomico(panel_task, obj, panel)

    @requiere_qt
    def test_puerta(self):
        from freecad.vdo.cad.puerta import make_puerta
        from freecad.vdo.ui import puerta_task
        from freecad.vdo.ui.puerta_task import PuertaTaskPanel
        obj = make_puerta(self.doc, {"nombre": "Pu_Atomico"})
        panel = PuertaTaskPanel(obj=obj, auto_transaction=False)
        self._comprobar_accept_atomico(puerta_task, obj, panel)

    @requiere_qt
    def test_cajon(self):
        from freecad.vdo.cad.cajon import make_cajon
        from freecad.vdo.ui import cajon_task
        from freecad.vdo.ui.cajon_task import CajonTaskPanel
        obj = make_cajon(self.doc, {"nombre": "Ca_Atomico"})
        panel = CajonTaskPanel(obj=obj, auto_transaction=False)
        self._comprobar_accept_atomico(cajon_task, obj, panel)

    @requiere_qt
    def test_coco(self):
        from freecad.vdo.cad.coco import make_coco
        from freecad.vdo.ui import coco_unified_task
        from freecad.vdo.ui.coco_unified_task import CocoUnifiedTaskPanel
        obj = make_coco(self.doc, {
            "nombre": "C_Atomico", "alto": 720, "ancho": 600,
            "fondo_modulo": 580, "espesor": 18})
        self.doc.recompute()
        panel = CocoUnifiedTaskPanel(obj=obj, auto_transaction=False)
        self._comprobar_accept_atomico(coco_unified_task, obj, panel)


if __name__ == "__main__":
    unittest.main()
