# ADR-MN04: Datos en `freecad/vdo/datos/`

**Estado:** aceptada (decisión delegada). Cumplida de forma parcial: hay datos fuera de `datos/` (ver Consecuencias).
**Decisiones de origen:** D-16 (`datos/valores.py`, literales de dominio), D-17 (`MODULE_SPECS` como datos).

## Contexto

Los valores de dominio y las especificaciones de módulo estaban escritos como código: `MODULE_SPECS` de 162 líneas, cadenas repetidas como `"melamina_standar"` (26 usos) o `"blum_tandem"` (14 usos), y tablas idénticas en dos archivos.

## Decisión

- Lo que es información y no comportamiento vive en `freecad/vdo/datos/`.
- JSON para catálogos y tablas de especificación. Un módulo `.py` solo cuando el dato necesita referencias a código.
- Cada valor de dominio tiene una constante en `datos/valores.py`. El código la importa; no escribe el literal.

## Consecuencias

- `datos/` contiene `formularios.py` (especificación de formularios, MN-08), `valores.py`, y los JSON `anclajes.json`, `modulos.json` y `vigilados.json`.
- `core/module_specs.py` pasa de 162 líneas de código a 43 líneas que cargan `MODULE_SPECS` con `json.load` (medido en M10). El golden de `MODULE_SPECS` no cambió.
- Literales de dominio repetidos: 53 usos en la base, 0 hallazgos en el final (`minimalismo.py literales`).
- **Salvedad:** `core/vdo_hardware_catalog.json` y `core/vdo_manifest.json` siguen en `core/`, no en `datos/`. Esto no cumple la letra de MN-04. No está registrado si se decidió dejarlo; ver `docs/DEUDA_TECNICA.md`.

## Relacionado

ADR-MN05, ADR-MN06. Ver `docs/ARQUITECTURA.md` §1.
