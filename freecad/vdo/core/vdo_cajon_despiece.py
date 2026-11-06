# =====================================================================
# vdo_cajon_despiece.py
# Fórmulas de despiece del cajón con corredera oculta (Blum Tandem etc)
# Axioma 2: lógica pura, SIN FreeCAD ni UI (testable con python3)
#
# Datos de partida:
#   LI       = ancho libre interior del mueble (pared a pared)
#   ProfInt  = profundidad libre interior del mueble
#   LG       = largo nominal de la guía (auto: max(comerciales ≤ ProfInt))
#   Delta    = reducción por herraje (ej. Blum Tandem 16mm → 49 mm)
#   Gcaja    = grosor de laterales/trasera/frente interior (15-16 mm)
#   Gfondo   = grosor del piso (6-12 mm)
#   Gfrente  = grosor de la fachada (18 mm)
# =====================================================================

