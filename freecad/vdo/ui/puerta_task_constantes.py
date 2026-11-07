# =====================================================================
# puerta_task_constantes.py
# Constantes de presentacion y opciones del panel de puerta.
# Compartidas por puerta_task_cabecera y puerta_task_construccion.
# =====================================================================

# Las opciones de familia y sentido viven en la especificacion de datos (M6, D-72).
from freecad.vdo.datos.formularios import (
    FAMILIAS,
    SENTIDOS_BASCULANTE,
    SENTIDOS_BATIENTE,
    SENTIDOS_CORREDIZA,
)
from freecad.vdo.ui import tema_colores

# ---------------------------------------------------------------------
# Mapeo de nombres de visualización (UI) a constantes del contrato.
# ---------------------------------------------------------------------

# Colores del Manifiesto de UI VDO (tema oscuro)
COLOR_FONDO = tema_colores.FONDO
COLOR_TEXTO = tema_colores.TEXTO
