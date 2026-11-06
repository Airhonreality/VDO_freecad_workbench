# ADR-MN06: Tabla única de sistemas de apertura

**Estado:** aceptada (decisión delegada). Cumplida para la tabla; los motores de cálculo siguen separados, como dice la propia decisión.
**Decisión de origen:** no tiene D-xx propio. Está registrada en `docs/DECISIONES_DELEGADAS.md`, sección "Registro de ejecución de D-13 a D-18", punto 9 ("M2 y M3"), con los commits `e88ce23` y `602f686`.

## Contexto

Un mismo concepto (sistema de apertura: tirador, gola, inglete 45, push open) estaba definido en cinco sitios: `vdo_facade_contract`, `vdo_cajon_despiece`, `vdo_puerta_despiece` (con un mapa legado y `_normalizar_apertura`), `ui/vdo_puerta_task` (con `APERTURA_LABELS`) y `ui/vdo_cajon_task`.

## Decisión

Una tabla en `core/aperturas.py` con nombre, cantos, descuento de gola, bisel, expulsor, etiqueta y valor legado. Cajón y puerta la consultan. Los motores de cálculo de cajón y de puerta **no** se unifican.

## Consecuencias

- Hechos de aperturas en sitios distintos: 5 en la base; 1 en el final (`core/aperturas.py`). Verificado con grep (M10).
- Único cambio de salida: el orden de `SISTEMAS_APERTURA_VALIDOS`, visible solo en el texto de un error de validación.
- Goldens `cajon_despiece`, `puerta_despiece` y `facade_contract`: sin diferencias.
- Los motores de cajón y de puerta siguen separados, como fija la decisión. No se ha evaluado si podrían unificarse.

## Relacionado

ADR-MN04. Ver `docs/ARQUITECTURA.md`.
