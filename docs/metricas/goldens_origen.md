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
| `frames.json` | 18 | 0 | **corregido** (ver "Cambios de esta sesión"): la entrada en error `interpretar_lados` pasa a ser una entrada válida |
| `finish.json` | 6 | 0 | sin cambio |
| `reengrose.json` | 24 | 0 | 18 en M0; **+6** en esta sesión (una entrada más para las 6 funciones que tenían 2) |
| `cajon_despiece.json` | 3 | 0 | sin cambio |
| `hardware_hub.json` | 12 | 0 | 9 en M0; **+3** en esta sesión (una entrada más para las 3 funciones que tenían 2) |
| `guardian.json` | 9 (3 funciones × 3 escenarios) | 0 | nuevo, desde `b78de04` (ver sección "Guardián") |
| `puerta_despiece.json` | 9 | 0 | **cambiado**: el anterior tenía 8 de 8 entradas en error |
| `coco_spaces.json` | 3 | 0 | **cambiado**: el anterior tenía 3 de 3 entradas en error (firma incorrecta) |
| `creacion_modulos.json` | 15 (5 flujos × 3) | 0 | **sustituido**: el anterior tenía otro esquema y no tenía generador en el repo |
| `zocalo_core.json` | 3 | 0 | nuevo |
| `module_props.json` | 3 | 0 | nuevo (`rotacion_z`, serializado como eje y ángulo) |
| `layout.json` | 3 | 0 | nuevo |
| `spaces.json` | 3 | 0 | nuevo |
| `optimizer_core.json` | 6 | 0 | nuevo |

Total: **140 entradas en 15 ficheros, 0 entradas en error** (medido con un script sobre `tests/golden/*.json`, al cierre de esta sesión).

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
| `nesting_presets` | **N/A con motivo (P-10, decisión delegada, ver `DECISIONES_DELEGADAS.md`).** En `b78de04` el módulo no se puede importar dentro de FreeCAD: `initialize_defaults()` se ejecuta al cargar y llama a `FreeCAD.ParamGet` sin tener `FreeCAD` en el ámbito (`NameError`, medido con `freecadcmd`). No hay comportamiento de origen que capturar, y generar un golden contra el código actual no probaría nada de origen. Tiene 9 métodos estáticos. **Deuda:** responsable `ejecutor`, plazo antes de M5, porque toca escritura de preferencias. Hay que arreglar la carga en el código actual y generar un golden de ese comportamiento, marcado como "nuevo, no de origen". |
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

## Revisión de goldens sustituidos (P-05)

Anterior = `692b76a^` (lo que había commiteado). Ahora = `692b76a`. Pendiente de aprobación humana (`PENDIENTES_HUMANO.md`, P-05).

### `creacion_modulos.json`

- **Antes:** 4 flujos (`crear_pieza`, `make_coco`, `make_zocalo`, `make_cajon`), 1 entrada plana por flujo (nombre, props y volumen). Sin `make_puerta`. No había script que lo generara en el repo.
- **Por qué estaba mal:** no se podía regenerar ni auditar (sin generador), no cubría `make_puerta` y tenía 1 entrada por flujo, por debajo del mínimo de 3 del plan.
- **Ahora:** 5 flujos × 3 entradas, con `caja`, `label`, `n_solidos`, `props`, `volumen`. Lo genera `tools/auditoria/golden_creacion.py` (con `GOLDEN_MODO=regenerar`).
- **¿Altera una salida esperada?** Parcialmente. Los volúmenes de los 4 flujos antiguos son iguales: `crear_pieza` 4320000, `make_coco` 28639296, `make_zocalo` 3866400. `make_cajon` pasa de `7417634.707993` a `7417634.708`: el nuevo golden redondea a 3 decimales; el valor no cambia. **El esquema cambia**, así que el golden no es comparable campo a campo con el anterior.

### `coco_spaces.json`

- **Antes:** 3 entradas, **3 de 3 en error** (`generar_divisiones_matriz() missing 5 required positional arguments`). La llamada usaba la firma equivocada.
- **Por qué estaba mal:** no probaba nada: todas las entradas eran errores de llamada.
- **Ahora:** 3 entradas con salida, con la firma de `b78de04` (`divisiones_json`, `ancho_cavidad`, `alto_cavidad`, `fondo`, `espesor`, …). 0 errores.
- **¿Altera una salida esperada?** **Sí.** Una salida esperada pasa de error a valor. Por eso va a P-05.

### `puerta_despiece.json`

- **Antes:** 8 entradas en 3 funciones, **8 de 8 en error** (argumentos mal nombrados: `ancho`/`alto`/`montaje` en vez de `W_neto`/`H_neto`/`tipo_montaje`).
- **Por qué estaba mal:** igual que el anterior: no probaba nada.
- **Ahora:** 9 entradas (3 por función) con las firmas de `b78de04`. 0 errores.
- **¿Altera una salida esperada?** **Sí.** De error a valor. Va a P-05.

Sin cambios en salidas: los 12 goldens de dominio restantes (incluido `module_props`, con la reubicación de `rotacion_z`) y `guardian`, que es nuevo.

## Cambios de esta sesión (2026-11-03)

Todos generados desde `b78de04` con `gold_drv.py` y `HOME=/tmp/vdo_home_noche`. Ninguno regenerado contra el código actual.

1. **`frames.interpretar_lados`: entrada en error sustituida por una válida.** Antes: `valor = "[frente, fondo]"`, que no es JSON válido (los nombres no van entre comillas). `interpretar_lados` la trata como JSON, así que el error viene de la entrada del golden, no del código; `b78de04` hace lo mismo. Ahora: `valor = '["frente", "fondo"]'`, salida `["frente", "fondo"]`. El golden queda con 0 entradas en error.
2. **`frames`, forma de guardar floats.** En `rotar_z` y `normal_global`, las salidas se guardan redondeadas a 6 decimales (`6.123e-17` pasa a `0.0`). `_serializar` ya redondeaba al comparar, así que no cambia el comportamiento. Comprobado: tras normalizar, las salidas antiguas y nuevas son idénticas (`golden.py --verificar frames: OK`).
3. **`hardware_hub`: +3 entradas** (una por función que tenía 2): `resolve_sliding` (`alacena`), `resolve_drawer_slide` (`HAFELE-OCULTA`), `calculate_sliding_doors` (`DUC-AL-1535-VID`). Las entradas previas no cambian.
4. **`reengrose`: +6 entradas** (una por función que tenía 2): `calcular_geometria_reengrose`, `calcular_geometria_caja`, `despiece_panel`, `despiece_caja`, `resolver_politica_cantos` (`modo_fabricacion = pacha`), `detectar_colision` (caja que toca sin solapar). Las entradas previas no cambian.

Motivo de (3) y (4): el plan exige **mínimo 3 entradas por función**. El registro anterior decía que lo cumplía, y no era cierto: 7 funciones tenían 2.

**P-05 aprobado** (decisión delegada en `DECISIONES_DELEGADAS.md`): `creacion_modulos`, `coco_spaces` y `puerta_despiece`, con el detalle de arriba.

## Defecto de locale (abierto, no es del golden)

`guardian.json` falla en el nivel 2 cuando el test corre después de otros tests de la misma sesión. Causa medida:

- Crear una `QApplication` (lo hacen los tests de UI) pone `LC_NUMERIC` a `es_CO`, porque Qt lee `LANG=es_CO.UTF-8` (medido: `('None','None')` antes, `('es_CO','UTF-8')` después).
- Con ese locale, FreeCAD lee el texto `"0.4"` como `0`. El guardián escribe `str(info["valor"])` en la hoja, así que `canto_fino` queda en `0` (medido: el manifiesto sigue en `0.4`; la hoja nueva guarda `'0'`).
- Ejecutado de forma aislada, el golden pasa.

**Riesgo para el usuario:** es un defecto de producto. Una sesión de FreeCAD con GUI y locale de coma decimal escribiría `canto_fino = 0` en el documento. No he verificado el comportamiento de la GUI real.

**Por qué no se corrige ahora:** la solución de fondo (escribir los números sin depender del locale, p. ej. con `=0.4`) cambia el contenido guardado en las celdas. Es un cambio de salida esperada: necesita aprobación humana. Tampoco se oculta: el test se queda en rojo en el nivel 2, como fallo documentado.

**Responsable:** usuario, para aprobar el cambio. Ejecutor, para implementarlo tras la aprobación.

**Actualización (2026-11-03, D-11, `169135b`):** la causa está corregida en código. `cad/vdo_guardian.py` escribe los números como `=N/D` (`Fraction(repr(valor))`), y `tests/test_guardian_locale.py` prueba la lectura en `es_CO.UTF-8` y en `C`. El golden `guardian.json` **se regeneró en D-14** (ver abajo). Antes la única diferencia era la celda `B5` (`canto_fino`), que pasa de `"0.4"` a `"=2 / 5"` en las 6 entradas, con el mismo valor leído. Los documentos ya guardados con `0` no se corrigen por código.

**Regeneración D-14 (2026-11-03):** `tests/golden/guardian.json` regenerado con `tools/auditoria/golden.py` (`regenerar("guardian")`) desde el código de D-13 (commit `1984d9e`). Diff comparado campo a campo: 6 cambios, todos en `Params_Melamina!B5` (`canto_fino`), `"0.4"` → `"=2 / 5"`. Ningún otro campo cambia. `verificar(guardian)` = True; `test_guardian` pasa. Procedencia del diseño de escenarios: la de la sección anterior, sin cambios. Esta regeneración es contra el código actual, aprobada por D-14 en `DECISIONES_DELEGADAS.md`.

## Lo que no está verificado

- Los goldens de creación y de geometría se generaron con FreeCAD 1.1.4 en esta
  máquina. No hay verificación en otra versión.
- Las entradas son representativas, no exhaustivas.
