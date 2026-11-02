# vdo_erp_sync

Componente de sincronización con el ERP/Neon para el workbench VDO.

## Alcance

Este componente se **extrae** a `tools/erp_sync/` (decisión M-01), se **excluye del ZIP**
de distribución y se verifica de forma independiente con `tsc --noEmit`.

## Requisitos

- Node.js
- TypeScript (`npm install` en esta carpeta)

## Configuración

La URL del catálogo ERP se pasa exclusivamente por la variable de entorno
`VDO_ERP_URL`. No hay valor por defecto: si falta, el comando falla con un
mensaje claro.

```bash
export VDO_ERP_URL="https://erp.ejemplo.com/v1/catalog/hardware"
```

## Comandos

```bash
# Instalar dependencias
npm install

# Verificar tipos (debe salir con código 0)
npm run typecheck
```

## Archivos

- `src/sync_pull_catalog.ts`: extrae el catálogo de hardware desde el ERP y lo
  escribe en `vdo_hardware_catalog.json`.
- `src/schemas.ts`: esquemas de validación (Zod) del catálogo entrante.
