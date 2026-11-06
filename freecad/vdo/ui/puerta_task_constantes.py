# =====================================================================
# puerta_task_constantes.py
# Constantes de presentacion y opciones del panel de puerta.
# Compartidas por puerta_task_cabecera y puerta_task_construccion.
# =====================================================================

# Las opciones de familia y sentido viven en la especificacion de datos (M6, D-72).
from freecad.vdo.datos.formularios import (  # noqa: F401 (reexportacion)
    FAMILIAS,
    SENTIDOS_BASCULANTE,
    SENTIDOS_BATIENTE,
    SENTIDOS_CORREDIZA,
)

# ---------------------------------------------------------------------
# Mapeo de nombres de visualización (UI) a constantes del contrato.
# ---------------------------------------------------------------------

# Colores del Manifiesto de UI VDO (tema oscuro)
COLOR_FONDO = "#1e1e1e"
COLOR_ACENTO = "#007acc"
COLOR_TEXTO = "#e0e0e0"
COLOR_BORDE = "#4a4a4a"
