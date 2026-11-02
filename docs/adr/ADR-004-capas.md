# ADR-004: Capas (core/cad/app/ui/entrada) (M-04)

## Estado
aceptada

## Contexto
El plan anterior permitía FreeCAD en `core/`, lo que acoplaba el dominio a FreeCAD y dificultaba las pruebas puras.

## Decisión
Cuatro capas + entrada con dependencias unidireccionales:
- `core/` → dominio puro, solo stdlib y `core/`
- `cad/` → adaptador FreeCAD (único con App/Part/FreeCADGui)
- `app/` → casos de uso y composición
- `ui/` → Qt, solo habla con `app/` y `qt_compat`
- `entrada` → `commands.py`, `Init.py`, `InitGui.py`

## Consecuencias
- `core/` puede probarse con `python3 -I` sin FreeCAD.
- La arquitectura es verificable con `tests/test_capas_arquitectura.py`.
- Los cambios de FreeCAD solo afectan a `cad/` y entrada.

## Referencia
- Plan maestro: M-04
- Commit: `d5e6300` (etiqueta `vdo10-f7`)
