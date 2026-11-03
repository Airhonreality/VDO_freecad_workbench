# Procedencia de los goldens de M0

**Commit de origen:** `b78de04` (último estado con creación correcta, según el plan).
**Fecha de generación:** 2026-11-02.
**Generado con:** `freecadcmd` con `HOME=/tmp/vdo_home_noche`, donde
`~/.local/share/FreeCAD/Mod/VDO` apunta a un worktree en `b78de04`.
El enlace del usuario (`~/.local/share/FreeCAD/Mod/VDO`) no se tocó.

Verificado en cada generación: la línea `CODIGO_CARGADO` muestra la ruta del worktree
(`/tmp/vdo_home_noche/.local/share/FreeCAD/Mod/VDO/...`).

## Comandos

Dominio (8 módulos ya con entradas en `golden.py`, más 4 nuevos):

```
GOLD_MODS=<lista> HOME=/tmp/vdo_home_noche freecadcmd /tmp/vdo_m0/scripts/gold_drv.py
```

`gold_drv.py` carga `tools/auditoria/golden.py` y llama a `regenerar(modulo)` por
módulo. Es un driver de una línea, fuera del repo.

Creación:

```
HOME=/tmp/vdo_home_noche GOLDEN_MODO=regenerar freecadcmd tools/auditoria/golden_creacion.py
```

Verificación contra el código actual (sin escribir):

```
PYTHONPATH=$PWD python3 tools/auditoria/golden.py --verificar <modulo>
freecadcmd tools/auditoria/golden_creacion.py
```

## Cambios de interfaz encontrados (no son diferencias de comportamiento)

1. **Creación con documento explícito.** En `b78de04`, `crear_pieza`, `make_coco`,
   `make_zocalo`, `make_cajon` y `make_puerta` reciben `(configuracion)` y escriben en
   `App.ActiveDocument`. En el código actual reciben `(doc, configuracion)`. El golden de
   creación llama a cada versión según su firma (`_invocar`). Las salidas son iguales.
2. **`crear_panel` no existe en `b78de04`.** Está en `app/casos_uso/crear_panel.py`, que se
   añadió después. No hay golden de referencia para ese flujo. El flujo de panel se
   cubre con `crear_pieza`.
3. **Serialización.** `golden.py` ahora serializa objetos de dominio por sus atributos
   públicos (`_serializar`). Antes fallaba con `ResolvedLayout`. Afecta a
   `coco_spaces` y no cambia ningún golden que ya era serializable.

## Goldens generados

| Golden | Entradas | Errores registrados | Origen |
|---|---|---|---|
| `facade_contract.json` | 23 | 0 | sin cambio respecto a lo commiteado |
| `frames.json` | 18 | 1 (`interpretar_lados`: JSON inválido, comportamiento esperado) | sin cambio |
| `finish.json` | 6 | 0 | sin cambio |
| `reengrose.json` | 18 | 0 | sin cambio |
| `cajon_despiece.json` | 3 | 0 | sin cambio |
| `hardware_hub.json` | 9 | 0 | sin cambio |
| `puerta_despiece.json` | 9 | 0 | **cambiado**: el anterior tenía 8 de 8 entradas en error |
| `coco_spaces.json` | 3 | 0 | **cambiado**: el anterior tenía 3 de 3 entradas en error (firma incorrecta) |
| `creacion_modulos.json` | 15 (5 flujos × 3) | 0 | **sustituido**: el anterior tenía otro esquema y no tenía generador en el repo |
| `zocalo_core.json` | 3 | 0 | nuevo |
| `layout.json` | 3 | 0 | nuevo |
| `spaces.json` | 3 | 0 | nuevo |
| `optimizer_core.json` | 6 | 0 | nuevo |

Total: 119 entradas en 13 ficheros.

## Verificación contra el código actual

| Golden | Resultado con el código actual |
|---|---|
| los 12 de dominio (`golden.py --verificar <modulo>`) | OK, 0 diferencias |
| creación (`golden_creacion.py`) | 0 diferencias en 15 entradas |

## Módulos sin golden y motivo

| Módulo | Motivo |
|---|---|
| `panel_core`, `cajon_core`, `puerta_core`, `coco_core` | Son flujos de creación. Cubiertos por `creacion_modulos.json`. |
| `guardian` | Sin función de cálculo: solo asegura parámetros en el documento. |
| `nesting_presets` | Sin funciones públicas (solo datos). |
| `module_props` | Su única función pura, `rotacion_z`, devuelve `App.Rotation`. El serializador no la representa todavía. Ver `DEUDA_TECNICA.md`. |

## Lo que no está verificado

- Los goldens de creación y de geometría se generaron con FreeCAD 1.1.4 en esta
  máquina. No hay verificación en otra versión.
- Las entradas son representativas, no exhaustivas.
