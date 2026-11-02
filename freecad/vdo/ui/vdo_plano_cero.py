# -*- coding: utf-8 -*-
"""Malla del plano de trabajo 0 (suelo) en la vista 3D.

FreeCAD dibuja esa malla con el Snapper de Draft (Gui.Snapper). Dos hechos del código de
Draft (verificados en la instalación 1.1.3) obligan a este diseño:

1. Gui.Snapper solo existe después de `import DraftTools`, y Draft solo hace ese import en
   su Initialize(), es decir, cuando se activa el workbench Draft. Un workbench propio que
   no pasa por Draft no tiene Snapper. Por eso se importa DraftTools aquí, igual que haría
   Draft (es idempotente).
2. La malla es un tracker por vista 3D, creado en Snapper.setTrackers(). Si todavía no hay
   vista 3D activa, no se crea. Por eso se reintenta unas veces, con un pequeño retardo.

Sin GUI, o sin Draft, no hace nada.
"""

import FreeCAD as App

from freecad.vdo.qt_compat import QtCore

_REINTENTOS = 10
_RETARDO_MS = 250


def _vista_3d_disponible():
    from draftutils import gui_utils
    return gui_utils.get_3d_view() is not None


def mostrar_plano_cero(reintentos=_REINTENTOS):
    """Muestra la malla del plano 0. Devuelve True si queda visible en este momento.

    Si aún no hay vista 3D, programa reintentos (no bloquea la activación del workbench).
    """
    try:
        import FreeCADGui as Gui
    except ImportError:
        return False
    if not getattr(App, "GuiUp", False):
        return False
    try:
        import DraftTools  # noqa: F401  crea Gui.Snapper (ver punto 1 del docstring)
        import WorkingPlane

        if not _vista_3d_disponible():
            if reintentos > 0:
                QtCore.QTimer.singleShot(
                    _RETARDO_MS, lambda: mostrar_plano_cero(reintentos - 1))
            return False

        Gui.Snapper.show()
        Gui.Snapper.setTrackers(update_grid=False)
        grid = Gui.Snapper.grid
        if not grid.Visible:
            grid.set()
            WorkingPlane.get_working_plane()
            grid.show_always = True
        return bool(grid.Visible)
    except Exception as exc:  # la malla es cosmética: nunca bloquear el workbench
        App.Console.PrintWarning(f"[VDO] No se pudo mostrar la malla del plano 0: {exc}\n")
        return False
