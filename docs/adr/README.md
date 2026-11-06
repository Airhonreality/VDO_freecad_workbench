# Decisiones de arquitectura (ADR) del plan de minimalismo

Un ADR por decisión estructural del plan `docs/PLAN_MINIMALISMO_VDO.md` §2 (MN-01 a MN-06 y MN-09). Las decisiones de menor alcance (D-xx) están en `docs/DECISIONES_DELEGADAS.md`.

| ADR | Decisión | Estado | Decisiones D-xx |
|---|---|---|---|
| [ADR-MN01](ADR-MN01-eliminar-app.md) | Se elimina `app/` | aceptada | D-22, D-23, D-25 |
| [ADR-MN02](ADR-MN02-tres-capas.md) | Tres capas y entrada | aceptada | D-31, D-39, D-40 |
| [ADR-MN03](ADR-MN03-reglas-dependencia.md) | Reglas de dependencia | aceptada | D-31, D-12, P-08 |
| [ADR-MN04](ADR-MN04-datos-en-datos.md) | Datos en `datos/` | aceptada (parcial) | D-16, D-17 |
| [ADR-MN05](ADR-MN05-catalogo-solo-json.md) | Catálogo de herrajes solo JSON | aceptada | H-21 |
| [ADR-MN06](ADR-MN06-tabla-unica-aperturas.md) | Tabla única de aperturas | aceptada | sin D-xx propio (registro de M2 y M3) |
| [ADR-MN09](ADR-MN09-renombrado-sin-prefijo.md) | Renombrado sin prefijo `vdo_` | aceptada (parcial) | D-77 |

## Sin ADR en esta fase

- MN-07, MN-08, MN-10 y MN-11 a MN-13: MN-11 limita los ADR a MN-01 a MN-06 y MN-09.

## ADR anteriores

Los archivos `ADR-000-indice.md`, `ADR-001-alcance-erp.md`, `ADR-004-capas.md` y `ADR-005-aislamiento-procesos.md` pertenecen al plan maestro anterior (M-01 a M-24). **No se han movido ni borrado en M11.** MN-11 los descarta; su destino (archivar o eliminar) es decisión humana, ver `docs/PENDIENTES_HUMANO.md`.
