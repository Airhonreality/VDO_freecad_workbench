# Índice de ADR (Architecture Decision Records)

Este directorio contiene una decisión por cada una de M-01…M-24 definidas en
`docs/PLAN_MAESTRO_VDO.md` (§3). Cada archivo se denomina `ADR-NNN-<slug>.md`
y sigue la plantilla:

```
# ADR-NNN: <título>

## Estado
propuesta | aceptada | rechazada | obsoleta

## Contexto
...

## Decisión
...

## Consecuencias
...

## Referencia
- Plan maestro: M-NN
- Commit/etiqueta: git tag vdo10-fX
```

## Decisiones M-01 … M-24

| ID | Tema | ADR | Estado |
|----|------|-----|--------|
| M-01 | Alcance y extracción ERP | `ADR-001-alcance-erp.md` | propuesta |
| M-02 | Ramas e historia | `ADR-002-ramas-historia.md` | aceptada |
| M-03 | Idioma y glosario | `ADR-003-idioma-glosario.md` | propuesta |
| M-04 | Capas (core/cad/app/ui/entrada) | `ADR-004-capas.md` | aceptada |
| M-05 | Dependencias de FreeCAD solo en cad/ y entrada | `ADR-005-dependencias-freecad.md` | aceptada |
| M-06 | Puerto único `app/puertos.py` | `ADR-006-puerto-documento.md` | propuesta |
| M-07 | Eliminar `vdo_ui_registry` del core | `ADR-007-eliminar-ui-registry.md` | propuesta |
| M-08 | Sin estado mutable de módulo | `ADR-008-estado-inmutable.md` | aceptada |
| M-09 | Validación de manifiesto propia | `ADR-009-validacion-manifiesto.md` | propuesta |
| M-10 | Formularios declarativos `FormBuilder` | `ADR-010-formularios.md` | propuesta |
| M-11 | Task panels `accept()` ≤ 15 líneas | `ADR-011-task-panels.md` | propuesta |
| M-12 | Tema único, acento `#007acc` | `ADR-012-tema-acento.md` | propuesta |
| M-13 | Jerarquía de errores tipados | `ADR-013-errores-tipados.md` | propuesta |
| M-14 | Canal único de logging | `ADR-014-logging.md` | propuesta |
| M-15 | Límite 100 líneas / complejidad 12 | `ADR-015-limite-funcion.md` | aceptada |
| M-16 | Tabla compartida de aperturas | `ADR-016-tabla-aperturas.md` | propuesta |
| M-17 | Geometría con números/tuplas inmutables | `ADR-017-geometria-inmutable.md` | propuesta |
| M-18 | Sin mocks en `sys.modules` al importar | `ADR-018-sin-mocks.md` | aceptada |
| M-19 | Golden masters por módulo | `ADR-019-golden-masters.md` | propuesta |
| M-20 | Eliminar prefijo `vdo_` en módulos | `ADR-020-nombres-modulos.md` | propuesta |
| M-21 | `_module_dir` solo en Init.py/InitGui.py | `ADR-021-module-dir.md` | aceptada |
| M-22 | Herramientas: eliminar `matriz_mapeo.py` | `ADR-022-herramientas.md` | propuesta |
| M-23 | Versión `2.0.0` | `ADR-023-version-2.md` | propuesta |
| M-24 | Documentación final | `ADR-024-documentacion.md` | propuesta |

**Convención:** una decisión pasa de `propuesta` a `aceptada` cuando la fase que la
implementa cierra y se etiqueta. Las decisiones `M-02`, `M-04`, `M-05`, `M-08`,
`M-15`, `M-18`, `M-21` están marcadas `aceptada` porque ya estaban vigentes en
la línea base o se aplican desde F0.
