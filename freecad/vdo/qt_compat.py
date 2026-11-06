"""Capa de compatibilidad Qt para todo el paquete VDO.

FreeCAD 1.1 trae PySide6 (verificado: PySide6 6.11.1 presente, PySide2 ausente).
Orden de búsqueda: PySide6 → PySide2 → PySide. Ningún otro módulo del paquete debe
importar PySide* directamente: se importa desde aquí.

Solo compatibilidad: sin widgets. Los widgets VDO están en ui/qt.py.
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
    except ImportError:
        from PySide import QtCore, QtGui, QtWidgets

try:
    from PySide6 import QtSvg
except ImportError:
    try:
        from PySide2 import QtSvg
    except ImportError:
        try:
            from PySide import QtSvg
        except ImportError:
            QtSvg = None

__all__ = ["QtCore", "QtGui", "QtSvg", "QtWidgets"]
