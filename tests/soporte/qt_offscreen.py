"""Fija QT_QPA_PLATFORM=offscreen (si no esta fijado) al importarse.

Debe importarse antes que cualquier modulo que cargue Qt.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
