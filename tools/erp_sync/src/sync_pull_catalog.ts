import * as path from 'path';
import * as fs from 'fs';
import { CatalogIngestionSchema, type CatalogIngestion } from './schemas';

const CATALOG_OUT = path.resolve(__dirname, '../../vdo_hardware_catalog.json');

async function fetchCatalogFromNeon(): Promise<unknown> {
  // Integración con Neon/MCP: la URL viene de VDO_ERP_URL (sin valor por defecto).
  const url = process.env.VDO_ERP_URL;
  if (!url) {
    throw new Error(
      "VDO_ERP_URL no definida: establece la variable de entorno con la URL del catálogo ERP.");
  }
  const resp = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!resp.ok) throw new Error(`Neon fetch failed: ${resp.status}`);
  return resp.json();
}

export async function syncPullCatalog(): Promise<void> {
  const raw: unknown = await fetchCatalogFromNeon();
  const ingestion: CatalogIngestion = CatalogIngestionSchema.parse(raw);
  fs.writeFileSync(CATALOG_OUT, JSON.stringify(ingestion.items, null, 2), 'utf-8');
}

if (require.main === module) {
  syncPullCatalog()
    .then(() => {
      // eslint-disable-next-line no-console
      console.log(`Catálogo escrito en ${CATALOG_OUT}`);
    })
    .catch((err: unknown) => {
      // eslint-disable-next-line no-console
      console.error(err);
      process.exit(1);
    });
}
