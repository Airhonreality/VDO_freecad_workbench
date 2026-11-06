# =====================================================================
# cajon_autotest.py
# Autoprueba del cálculo del cajón. Separada de vdo_cajon_despiece.py (M7, D-36).
# =====================================================================

import logging

from freecad.vdo.core.cajon_calculo import calcular_despiece
from freecad.vdo.datos.valores import BLUM_TANDEM

_LOG = logging.getLogger(__name__)

# =====================================================================
# SELF-TEST (desde la raíz del repo: python3 -m freecad.vdo.core.cajon_autotest)
# =====================================================================
if __name__ == "__main__":
    from freecad.vdo.core.helpers import _get_app
    App = _get_app()
    App.Console.PrintMessage("=" * 64)
    App.Console.PrintMessage("[VDO] Self-test vdo_cajon_despiece.py")
    App.Console.PrintMessage("=" * 64)

    config = {
        "ancho_libre": 600.0,      # LI
        "prof_libre": 580.0,       # ProfInt
        "ancho_modulo": 640.0,
        "alto_frente": 225.0,
        "marca": BLUM_TANDEM,
        "alto_caja": 120.0,
        "grosor_caja": 16.0,
        "grosor_fondo": 6.0,
        "grosor_fachada": 18.0,
    }
    d = calcular_despiece(config)

    # --- Aritmética de referencia ---
    assert d["guia"]["lg"] == 550.0, d["guia"]          # 580 → 550
    assert d["guia"]["delta"] == 49.0
    assert d["caja"]["ancho_exterior"] == 551.0         # 600 - 49
    assert d["caja"]["ancho_contra"] == 519.0           # 551 - 32
    assert abs(d["caja"]["alto_contra"] - 102.5) < 1e-9  # 120 - 17.5
    assert d["caja"]["ancho_piso"] == 539.0             # 519 + 2*10
    assert d["caja"]["largo_piso"] == 550.0
    assert d["fachada"]["ancho"] == 581.0               # 551 + 2*16 - 2 (parche)
    assert d["fachada"]["alto"] == 221.0                # 225 - 4
    assert d["fachada"]["tipo_montaje"] == "parche"
    assert d["posiciones"]["fachada"]["x"] == -15.0     # centrada sobre la caja
    assert len(d["piezas"]) == 6

    # --- Montaje a testa ---
    d2 = calcular_despiece(dict(config, montaje_trasera="testa"))
    assert d2["caja"]["ancho_contra"] == 551.0          # ancho completo

    # --- Guía manual ---
    d3 = calcular_despiece(dict(config, longitud_guia=500))
    assert d3["guia"]["lg"] == 500.0 and d3["guia"]["auto"] is False

    # --- Guía imposible ---
    lanzó_value_error = False
    try:
        calcular_despiece(dict(config, prof_libre=200))
    except ValueError as exc:
        _LOG.debug("cajon_autotest: ValueError esperado en la prueba de autotest: %s", exc)
        lanzó_value_error = True
    if not lanzó_value_error:
        raise AssertionError("Debía fallar con ProfInt=200")

    # --- Grosor 18mm avisa ---
    d4 = calcular_despiece(dict(config, grosor_caja=18.0))
    assert any("15/16" in a for a in d4["avisos"]), d4["avisos"]

    App.Console.PrintMessage("✅ Todas las aserciones pasaron")
    App.Console.PrintMessage(f"   LG={d['guia']['lg']}  ancho_ext={d['caja']['ancho_exterior']}"
          f"  ancho_contra={d['caja']['ancho_contra']}"
          f"  piso={d['caja']['ancho_piso']}x{d['caja']['largo_piso']}")
    App.Console.PrintMessage(f"   Piezas: {[p['nombre'] for p in d['piezas']]}")
    if d["avisos"]:
        App.Console.PrintMessage(f"   ⚠️  Avisos: {d['avisos']}")
