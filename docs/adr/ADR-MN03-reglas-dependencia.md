# ADR-MN03: Reglas de dependencia entre capas

**Estado:** aceptada (decisión delegada). Cumplida en el código, con una salvedad sobre `datos/` (ver Consecuencias).
**Decisiones de origen:** D-31 (el director fijó que `ui/` puede importar `core` y `cad`), D-12 (ciclo dentro de `cad` resuelto), P-08 (ciclo `core` ↔ `cad` resuelto).

## Contexto

Antes del plan había ciclos de importación entre `core` y `cad` y entre módulos de `ui/`. No había una dirección única de dependencia.

## Decisión

- `core` no importa `cad`, `ui` ni `app`.
- `cad` importa `core`.
- `ui` importa `core` y `cad`. No escribe en FreeCAD.
- La entrada (`commands.py`, `Init.py`, `InitGui.py`) importa todo.

Se verifica con `tests/test_arquitectura.py` (clase `CapasTests`) y `tests/test_capas_arquitectura.py`.

## Consecuencias

- Aristas `core -> cad`: 0 (`python3 -I tools/auditoria/ciclos.py`). Tras P-08 subieron a 8; la herramienta mide 0 en el estado actual.
- Quedan 3 componentes cíclicos dentro de `ui/` (U-01 a U-03). MN-03 no los cubre, y romperlos requiere mover lógica entre módulos de UI. Ver `docs/DEUDA_TECNICA.md`.
- La regla "`core` no importa nada del paquete" se cumple en la medición, pero la pureza de `core` se verifica solo con las pruebas de imports, no con un análisis de efectos.
- Los datos de solo lectura cargados una vez (p. ej. `MODULE_SPECS`) no cuentan como estado mutable de módulo (D-18).

## Relacionado

ADR-MN02. Ver `docs/ARQUITECTURA.md` §2 y §4.
