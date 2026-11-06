# ADR-MN02: Tres capas más entrada

**Estado:** aceptada (decisión delegada).
**Decisiones de origen:** D-31 (alcance de `ui/`), D-39 (división de `cad/coco`), D-40 (división de `ui/vdo_widgets_coco`).

## Contexto

El paquete mezclaba cálculo, escritura en FreeCAD, widgets y coordinación en los mismos archivos y en `app/`. El plan (MN-02) pide el mínimo que separe lo que cambia por motivos distintos: dominio, plataforma y presentación.

## Decisión

Tres capas y una entrada:
- `core/`: datos y cálculo puro, sin FreeCAD ni Qt.
- `cad/`: escritura en el documento FreeCAD.
- `ui/`: Qt y presentación.
- Entrada: `commands.py`, `creacion.py`, `Init.py`, `InitGui.py`.

`datos/` agrupa las tablas (ver ADR-MN04).

## Consecuencias

- Medidas finales (`docs/metricas/minimalismo_final.json`): `core` 47 archivos, 7.943 líneas; `cad` 19 archivos, 2.854 líneas; `ui` 79 archivos, 14.374 líneas.
- `ui/` sube en líneas (13.507 en la base a 14.374). La meta del plan (`ui` reducido a presentación) no se cumple en líneas. Ver `docs/PROGRESO_MINIMALISMO.md` (M10).
- `cad/` pasa de 5 a 19 archivos al dividir `cad/coco` y otros módulos por concepto. Es el coste de P5 (un concepto por archivo).

## Relacionado

ADR-MN01, ADR-MN03. Ver `docs/ARQUITECTURA.md` §1.
