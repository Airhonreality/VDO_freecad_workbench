# ADR-001: Alcance y extracción ERP (M-01)

## Estado
aceptada

## Contexto
El repositorio incluye `tools/vdo_erp_sync/` que documenta un árbol que ya no existe. Debe extraerse y excluirse del ZIP de distribución.

## Decisión
- Mover `tools/vdo_erp_sync/` a `tools/erp_sync/` con README propio.
- Excluir `tools/erp_sync/` del ZIP de distribución (`tools/build_zip.py`).
- Verificar con `tsc --noEmit`.
- La URL del ERP se pasa por variable de entorno `VDO_ERP_URL` (sin valor por defecto).

## Consecuencias
- El componente ERP es independiente y verificable por separado.
- No hay secretos hardcodeados en el repositorio.

## Referencia
- Plan maestro: M-01
- Commit: `8580f1d` (etiqueta `vdo10-f1`)
