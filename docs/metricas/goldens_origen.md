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
| `guardian.json` | 9 (3 funciones × 3 escenarios) | 0 | nuevo, desde `b78de04` (ver sección "Guardián") |
| `puerta_despiece.json` | 9 | 0 | **cambiado**: el anterior tenía 8 de 8 entradas en error |
| `coco_spaces.json` | 3 | 0 | **cambiado**: el anterior tenía 3 de 3 entradas en error (firma incorrecta) |
| `creacion_modulos.json` | 15 (5 flujos × 3) | 0 | **sustituido**: el anterior tenía otro esquema y no tenía generador en el repo |
| `zocalo_core.json` | 3 | 0 | nuevo |
| `module_props.json` | 3 | 0 | nuevo (`rotacion_z`, serializado como eje y ángulo) |
| `layout.json` | 3 | 0 | nuevo |
| `spaces.json` | 3 | 0 | nuevo |
| `optimizer_core.json` | 6 | 0 | nuevo |

Total: 131 entradas en 15 ficheros (medido con un script sobre `tests/golden/*.json`, 1 entrada en error: `frames.interpretar_lados`).

## Verificación contra el código actual

| Golden | Resultado con el código actual |
|---|---|
| los 12 de dominio sin FreeCAD (`golden.py --verificar <modulo>`) | OK, 0 diferencias |
| `module_props` (con FreeCAD, `GOLD_MODS=module_props freecadcmd ...`) | OK, 0 diferencias, con reubicación de `rotacion_z` (ver abajo) |
| creación (`golden_creacion.py`) | 0 diferencias en 15 entradas |

## Módulos sin golden y motivo

| Módulo | Motivo |
|---|---|
| `panel_core`, `cajon_core`, `puerta_core`, `coco_core` | Son flujos de creación. Cubiertos por `creacion_modulos.json`. |
| `nesting_presets` | **No cubierto. Decisión humana pendiente (P-10).** En `b78de04` el módulo no se puede importar dentro de FreeCAD: `initialize_defaults()` se ejecuta al cargar y llama a `FreeCAD.ParamGet` sin tener `FreeCAD` en el ámbito (`NameError`, medido con `freecadcmd`). No hay comportamiento de origen que capturar. Tiene 9 métodos estáticos (`get_preset`, `save_preset`, etc.); no es "solo datos", como decía la versión anterior de este documento. |
| — | `module_props` ya tiene golden (ver tabla). |

## Guardián (`guardian.json`)

- **Origen:** `freecad/vdo/core/vdo_guardian.py` en `b78de04`. En el código actual está en
  `freecad/vdo/cad/vdo_guardian.py`. `golden.py` lo importa desde la primera ubicación que
  exista (`UBICACIONES`). La lógica es la misma: las diferencias son docstrings y formato de
  mensajes.
- **Funciones:** `asegurar_hoja_global`, `asegurar_params_local`, `vdo_guard`.
  `asegurar_documento` no se cubre: usa `App.ActiveDocument` y no recibe documento.
- **Escenarios** (3 por función): estado del documento antes de la llamada. Se crea un
  documento nuevo por entrada y se vuelcan las celdas A1:D60 de cada hoja, con contenido y
  alias. Los estados "editada" fijan un valor propio (`B2=1234` en `Params_Melamina`,
  `A1=999` en `Params`) con alias, para comprobar que el guardián no lo sobrescribe.
- **Procedencia:** generado desde `b78de04` con `gold_drv.py` (fuera del repo, en
  `/tmp/vdo_m0/scripts/`) y `HOME=/tmp/vdo_home_noche`.
- **Verificación contra el código actual:** `freecadcmd` con el `HOME` real del usuario,
  `OK golden: guardian`, 0 diferencias.
- **Limitación:** el golden solo cubre estos escenarios. No hay entradas con error.

## Reubicación de funciones

| Función | Módulo en `b78de04` | Módulo actual | Efecto |
|---|---|---|---|
| `rotacion_z` | `core/vdo_module_props.py` | `core/vdo_helpers.py` **y** `cad/propiedades.py` (dos copias) | El golden se verifica contra `vdo_helpers`. Cuando el módulo original no tiene la función, `golden.py` usa `RELOCALIZADAS`. Comportamiento igual: 0 diferencias. Duplicado registrado en `DEUDA_TECNICA.md` (D-09). |

## Lo que no está verificado

- Los goldens de creación y de geometría se generaron con FreeCAD 1.1.4 en esta
  máquina. No hay verificación en otra versión.
- Las entradas son representativas, no exhaustivas.
