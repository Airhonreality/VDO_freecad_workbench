# ADR-MN01: Se elimina el paquete `app/`

**Estado:** aceptada (decisión delegada).
**Registro:** fases M3 a M5 en `docs/PROGRESO_MINIMALISMO.md`.
**Decisión de origen:** D-22 (stubs eliminados), D-23 (DTO a `core/dto.py`), D-25 y D-31 (pruebas de capas alineadas).

## Contexto

`app/` tenía casos de uso esqueleto y DTO. Eran una capa que no decidía nada: solo coordinaba llamadas entre `ui/` y `core/`/`cad/`. El plan (`docs/PLAN_MINIMALISMO_VDO.md` §2, MN-01) la declaró innecesaria. Medida base: 21 archivos y 941 líneas según `docs/metricas/minimalismo_base.json` (el plan cita 518 líneas; la diferencia no está explicada en el registro).

## Decisión

Eliminar `app/`. Cada función:
- con lógica de dominio pasa a `core/` (DTO a `core/dto.py`);
- que escribe en el documento pasa a `cad/`;
- que solo coordina pasa a `commands.py`.

Los stubs sin lógica (`app/casos_uso/exportar_lista_corte.py`, `app/casos_uso/recargar_catalogo.py`) se borraron (D-22).

## Consecuencias

- `minimalismo_final.json` mide `app` con 0 archivos y 0 líneas.
- La prueba `test_app_no_importa_ui` se mantiene solo si `app/` existe (D-25).
- `tools/auditoria/verificar.py` (congelado) tiene una regla R4 que exigía los stubs; falla por diseño tras D-22.
- Se pierde una capa de indirección entre `ui/` y `core/`. Eso aumenta el acoplamiento directo de `ui/` con `core/` y `cad/`, que MN-03 permite (ver ADR-MN03).

## Relacionado

ADR-MN02, ADR-MN03. Detalle en `docs/DECISIONES_DELEGADAS.md` (D-22, D-23, D-25).
