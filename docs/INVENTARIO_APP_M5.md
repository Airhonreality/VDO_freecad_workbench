# Inventario de destino de `freecad/vdo/app/` (M5, paso 1)

Fecha: 2026-11-05. Rama: `minimalismo/noche-20261102`.
Base: 21 archivos `.py`, 923 líneas (`find freecad/vdo/app -name '*.py' | xargs wc -l`).

Reglas aplicadas (de `docs/PLAN_MINIMALISMO_VDO.md` §0 P4, P6 y §6 M5):
lógica de decisión → `core/`; escritura en FreeCAD → `cad/`; solo coordina → `commands.py`;
solo reexporta o no hace nada → eliminar.

"Escribe en FreeCAD" se mide sobre el propio archivo: llama a `addObject`, `setattr`,
`Placement`, transacciones o `recompute` directamente. Una función que solo delega en
`core/make_*` o en `cad/` figura como "no" y se explica en el motivo.

| Archivo de app/ | Función / clase principal | ¿Lógica de decisión? | ¿Escribe en FreeCAD? | Destino propuesto | Motivo |
|---|---|---|---|---|---|
| `__init__.py` | (vacío) | no | no | eliminar | Paquete vacío; desaparece con el último módulo. |
| `puertos.py` | `Documento` (Protocol), `crear_documento` | no | no (delega en `cad/vdo_guardian`) | eliminar | Fachada: el tipo se mueve a quien lo usa y `crear_documento` lo llama `commands.py` directamente desde `cad/`. |
| `registro.py` | `info`, `warning`, `error` | no | no (escribe en consola, no en el documento) | eliminar | Sin importadores; duplica `App.Console` y el logger ya existente. |
| `rutas.py` | `ruta_recursos` | no | no | eliminar | Sin importadores; devuelve rutas relativas a `app/`, que va a desaparecer. |
| `composicion.py` | `Contexto`, `contexto` | no | no | eliminar | Sin importadores; solo carga manifiesto y catálogo, y eso lo puede hacer `commands.py`. |
| `vdo_creacion.py` | `crear_modulo_interactivo`, `_nombre_unico`, `_sanitizar_nombre` | sí (nombre único, sanitizado) | sí (transacción, `add_common_props`, `ocultar_vista`, `removeObject`) | commands.py (coordina); la lógica de nombres pasa a core/ | Orquesta creación con callbacks de UI. Los nombres son decisión y van a core/. |
| `dto.py` | 26 dataclasses `*DTO` / `*Resultado` | no | no | eliminar | Contenedores sin comportamiento (P6). Su único importador es `casos_uso/`. |
| `casos_uso/__init__.py` | reexportación de `dto` y `casos_uso` | no | no | eliminar | Solo reexporta. |
| `casos_uso/crear_zocalo.py` | `crear_zocalo` | no | no directo (llama `make_zocalo`, que escribe) | commands.py | Mapea DTO a cfg y llama a core; solo coordina. |
| `casos_uso/crear_hoja.py` | `crear_hoja` | no | no directo (llama `vdo_guard`) | commands.py | Valida documento y delega en el guardián de `cad/`. |
| `casos_uso/crear_panel.py` | `crear_panel` | no | no directo (llama `crear_pieza`) | commands.py | Mapea DTO a cfg y llama a core; solo coordina. |
| `casos_uso/crear_puerta.py` | `crear_puerta` | no | no directo (llama `make_puerta`) | commands.py | Mapea DTO a cfg y llama a core; solo coordina. |
| `casos_uso/crear_cajon.py` | `crear_cajon` | no | no directo (llama `make_cajon`) | commands.py | Mapea DTO a cfg y llama a core; solo coordina. |
| `casos_uso/crear_coco.py` | `crear_coco` | no | no directo (llama `make_coco`) | commands.py | Mapea DTO a cfg y llama a core; solo coordina. |
| `casos_uso/editar_modulo.py` | `editar_modulo` | no | sí (`setattr`, `recompute`) | cad/ | Escribe propiedades de un objeto FreeCAD. |
| `casos_uso/colocar_modulo.py` | `colocar_modulo`, `preparar_colocacion`, `colocar_en_punto` | no | sí (`Placement`, `recompute`) en `colocar_modulo`; los otros dos delegan | cad/ | Escribe `Placement`. Los dos wrappers son fachadas hacia `cad/colocacion`. |
| `casos_uso/exportar_lista_corte.py` | `exportar_lista_corte` | no | no | eliminar | Stub: devuelve un nombre de archivo fijo y `piezas=0`. |
| `casos_uso/optimizar_corte.py` | `optimizar_corte` | sí (eficiencia de corte) | no | core/ | Cálculo de eficiencia puro. |
| `casos_uso/nesting.py` | `nesting` | sí (placas = 8 piezas por placa) | no | core/ | Heurística de reparto en placas. Es decisión, aunque sea provisional. |
| `casos_uso/consultar_herrajes.py` | `consultar_herrajes` | sí (filtro por tipo) | no | core/ | Filtra por tipo, pero tiene SKU fijos en código; deben venir del catálogo (MN-05). |
| `casos_uso/recargar_catalogo.py` | `recargar_catalogo` | no | no | eliminar | Stub: devuelve la versión fija `"1.0.0"`. |

## Resumen por destino

| Destino | Archivos | Cuáles |
|---|---|---|
| core/ | 3 | `optimizar_corte`, `nesting`, `consultar_herrajes` (más la lógica de nombres de `vdo_creacion`) |
| cad/ | 2 | `editar_modulo`, `colocar_modulo` |
| commands.py | 7 | `vdo_creacion`, `crear_zocalo`, `crear_hoja`, `crear_panel`, `crear_puerta`, `crear_cajon`, `crear_coco` |
| eliminar | 9 | `__init__` (app), `puertos`, `registro`, `rutas`, `composicion`, `dto`, `casos_uso/__init__`, `exportar_lista_corte`, `recargar_catalogo` |

Total: 3 + 2 + 7 + 9 = 21.

## Dependencias externas que bloquean la eliminación

- `freecad/vdo/commands.py:57` importa `app.vdo_creacion`; `:72` importa `app.puertos`.
- `freecad/vdo/ui/vdo_placement.py:15` importa `app.casos_uso.colocar_modulo`. La UI debe llamar a `cad/colocacion` directamente en la siguiente ola.
- `tests/test_creacion_colocacion.py:19` importa `app.vdo_creacion`.
- `tests/test_arquitectura.py` solo cita `app` en cadenas de texto de sus reglas (líneas 94, 118, 142). No importa ningún archivo de `app/`. Se deja intacto.
- `tools/auditoria/verificar.py:179-183` (R4, congelado) exige la existencia de `casos_uso/exportar_lista_corte.py` y `casos_uso/recargar_catalogo.py`. Eliminarlos hace que R4 falle. Por eso esta ola no los elimina.

## Siguiente ola (pendiente)

Mover `vdo_creacion` a commands.py con la lógica de nombres en core/. Mover los 7 casos de coordinación a commands.py, o eliminarlos al separar plan y aplicación de `make_*`. Mover `editar_modulo` y `colocar_modulo` a cad/. Pasar `optimizar_corte`, `nesting` y `consultar_herrajes` a core/. Eliminar `dto.py`, `puertos.py`, `exportar_lista_corte.py`, `recargar_catalogo.py` y `app/__init__.py` cuando ya no los use nadie. Decidir antes qué hacer con R4 de `verificar.py`.
