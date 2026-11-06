# =====================================================================
# tests/test_despiece_snapshots.py
# Tests de snapshot del motor de despiece (F5, paso 1).
#
# Fijan la salida actual (BOM + dimensiones de piezas) de cajon y puerta
# para configuraciones representativas. Cualquier cambio posterior al
# motor de despiece que altere estos valores hará fallar estos tests,
# lo que obliga a revertir la fase (§0.7 del plan).
# =====================================================================

import json
import os
import sys
import unittest

try:
    _AQUI = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _AQUI = os.getcwd()
_RAIZ = os.path.dirname(_AQUI)

from freecad.vdo.core import puerta_despiece as D
from freecad.vdo.core.cajon_calculo import calcular_despiece
from freecad.vdo.core.cajon_correderas import (
    CAJA_METALICA,
    CORREDERA_OCULTA,
    CORREDERA_TELESCOPICA,
)
from freecad.vdo.core.facade_contract import (
    APERTURA_45_GRADOS,
    APERTURA_GOLA,
    APERTURA_PUSH_OPEN,
    APERTURA_TIRADOR,
)

FIXTURES = os.path.join(_RAIZ, "tests", "fixtures")

CONFIG_BASE = {
    "ancho_libre": 600.0, "prof_libre": 580.0, "ancho_modulo": 640.0,
    "alto_frente": 225.0, "marca": "blum_tandem", "alto_caja": 120.0,
    "grosor_caja": 16.0, "grosor_fondo": 6.0, "grosor_fachada": 18.0,
    "longitud_guia": 0.0, "montaje_trasera": "entre_laterales",
    "penetracion_ranura": 10.0, "eje_ranura": 11.5,
    "holgura_lateral_fachada": 2.0, "holgura_superior_fachada": 2.0,
    "holgura_inferior_fachada": 2.0, "material_ref": "melamina_standar",
}


def _cargar(nombre):
    with open(os.path.join(FIXTURES, nombre), encoding="utf-8") as f:
        return json.load(f)


class TestDespieceSnapshotsCajon(unittest.TestCase):
    """Snapshot del despiece de cajon por tipologia y sistema de apertura."""

    def _ejecutar(self, nombre, tipo_corredera, marca=None, sistema_apertura=None,
                  extra=None):
        config = dict(CONFIG_BASE, tipo_corredera=tipo_corredera)
        if marca is not None:
            config["marca"] = marca
        if sistema_apertura is not None:
            config["sistema_apertura"] = sistema_apertura
        if extra:
            config.update(extra)
        actual = calcular_despiece(config)
        esperado = _cargar(f"cajon_{nombre}.json")
        self.assertEqual(actual, esperado,
                         f"El snapshot de cajon '{nombre}' cambio respecto al "
                         "fixture. Revertir cambios en el motor de despiece.")

    def test_oculta_blum(self):
        self._ejecutar("oculta_blum", CORREDERA_OCULTA)

    def test_oculta_generica(self):
        self._ejecutar("oculta_generica", CORREDERA_OCULTA, marca="generica")

    def test_telescopica(self):
        self._ejecutar("telescopica", CORREDERA_TELESCOPICA)

    def test_metalica(self):
        self._ejecutar("metalica", CAJA_METALICA)

    def test_gola(self):
        self._ejecutar("gola", CORREDERA_OCULTA, sistema_apertura=APERTURA_GOLA)

    def test_inglete_45(self):
        self._ejecutar("45", CORREDERA_OCULTA, sistema_apertura=APERTURA_45_GRADOS)

    def test_push_open(self):
        self._ejecutar("push", CORREDERA_OCULTA, sistema_apertura=APERTURA_PUSH_OPEN)

    def test_tirador(self):
        self._ejecutar("tirador", CORREDERA_OCULTA, sistema_apertura=APERTURA_TIRADOR)


class TestDespieceSnapshotsPuerta(unittest.TestCase):
    """Snapshot del despiece / mediciones de puerta."""

    def test_batiente_parche(self):
        actual = D.calcular_dimensiones_batiente(600, 800, "parche")
        self.assertEqual(actual, _cargar("puerta_batiente_parche.json"))

    def test_batiente_semiparche(self):
        actual = D.calcular_dimensiones_batiente(600, 800, "semiparche")
        self.assertEqual(actual, _cargar("puerta_batiente_semiparche.json"))

    def test_batiente_embebida(self):
        actual = D.calcular_dimensiones_batiente(600, 800, "embebida")
        self.assertEqual(actual, _cargar("puerta_batiente_embebida.json"))

    def test_corrediza_2hojas(self):
        actual = D.calcular_corrediza(1200, 2000, "closet", 2)
        self.assertEqual(actual, _cargar("puerta_corrediza_2hojas.json"))

    def test_bisagras_para_puerta_800(self):
        actual = D.bisagras_para_puerta(800)
        self.assertEqual(actual, _cargar("puerta_bisagras_para_puerta_800.json"))


if __name__ == "__main__":
    resultado = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    sys.exit(0 if resultado.wasSuccessful() else 1)
