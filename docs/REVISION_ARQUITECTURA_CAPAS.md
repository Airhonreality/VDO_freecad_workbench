# Revisión de arquitectura por capas (VDO)

> Fecha: 2026-11-02. Alcance: capas estructurales (no la lógica de funcionamiento del workbench).
> Se revisa antes de entrar en el detalle del Inspector y de la lógica de COCO, según lo acordado.

## 1. Capas axiomáticas (contrato)

| Capa | Ruta | Puede importar | No puede importar |
|---|---|---|---|
| Arranque sin GUI | `Init.py` | `FreeCAD` | `FreeCADGui`, Qt |
| Arranque con GUI | `InitGui.py` | `FreeCADGui`, `freecad.vdo.commands`, `freecad.vdo.ui.vdo_bim_bridge` | motor (`core`) en el cuerpo de módulo |
| Comandos | `freecad/vdo/commands.py` | `core` y `ui` solo dentro de `Activated()` | lógica de negocio |
| Motor | `freecad/vdo/core/` | `FreeCAD`, librerías puras | **`ui/` y `FreeCADGui` (objetivo; hoy incumplido, ver 3.1)** |
| Interfaz | `freecad/vdo/ui/` | `core`, `qt_compat`, `FreeCADGui` | — |
| Compatibilidad Qt | `freecad/vdo/qt_compat.py` | PySide6 / PySide2 / PySide | — |
| Integración externa | `freecad/vdo/ui/vdo_bim_bridge.py` | `FreeCADGui` (API de manipuladores) | lógica de VDO |
| Pruebas | `tests/` (fuera del paquete) | todo | — (no se empaquetan) |
| Herramientas | `tools/` (fuera del paquete) | — | — |

Reglas que ya se cumplen y se comprueban por test:
- Sin `exec()` (`test_comandos_workbench.SinExecTests`).
- `freecad/` sin `__init__.py` (`test_headless_core`).
- `core` carga sin GUI (`test_headless_core`).

## 2. Lo que se cambió en esta sesión (capa de workbench)

1. **Registro de comandos al cargar la GUI.** Antes se hacía en `Initialize()` (primera activación).
   Ahora `InitGui.py` llama a `register_all()` y al puente con BIM al cargar. Motivo: BIM monta sus
   menús al activarse; los comandos de VDO deben existir antes.
2. **Documento y vista 3D al activar.** `VDOWorkbench.Activated()` y el comando `VDO_AbrirVDO`
   llaman a `asegurar_documento_activo()`. Sin documento, FreeCAD muestra la página de inicio y no
   el canvas 3D. Esto corrige «seleccionar VDO en el desplegable no activa el canvas».
3. **Puente con BIM (Opción C de la investigación).** `freecad/vdo/ui/vdo_bim_bridge.py` registra un
   manipulador de workbench. Cuando el workbench activo es BIM, añade «Nuevo proyecto VDO» en el menú
   Archivo. Si la API no existe, no añade nada y avisa en consola.
4. **Comando nuevo `VDO_AbrirVDO`** (15 comandos en total).

## 3. Hallazgos de arquitectura

### 3.1 Dependencia circular core ↔ ui — **RESUELTO (D24)**

- `core` importa `ui` de forma diferida en ~20 sitios (`vdo_coco_core`, `vdo_creation_flow`,
  `vdo_zocalo_core`, `vdo_optimizer_core`, `vdo_cajon_core`, `vdo_puerta_core`, `vdo_panel_core`,
  `vdo_view_base`) y `vdo_module_specs.py` guarda rutas `freecad.vdo.ui.*` como cadenas.
- `ui` importa `core` (19 de sus módulos).
- `vdo_view_base` y `vdo_creation_flow` usan `FreeCADGui` directamente.

**Por qué importa:** el motor no puede probarse ni cargarse sin la interfaz; el ciclo se oculta
en importaciones diferidas, así que los errores aparecen en tiempo de ejecución, no en los tests.

**Propuesta (no ejecutada aquí, requiere GUI para verificar):** inversión de dependencias.
- `core` define un registro vacío: `registrar_fabrica_panel(module_key, fabrica)` y
  `registrar_fabrica_vista(...)`.
- `ui` (al cargar la GUI, desde `InitGui.py`) registra sus paneles en ese registro.
- `core` consulta el registro; si no hay GUI, devuelve `None` y el flujo sigue sin panel.
- `vdo_module_specs` pasa de cadenas `importlib` a claves de registro.
- Verificación: `test_headless_core` debe seguir pasando y se añade un test que importe `core`
  y compruebe que ningún módulo de `core` contiene `freecad.vdo.ui`.

### 3.2 `vdo_view_base` mezcla motor y GUI — **RESUELTO (D24)**

Nombre de módulo en `core/`, pero contiene la vista (`ViewProvider`), selección y paneles. Debe
moverse a `ui/` cuando se haga 3.1. Se mantiene en `core/` ahora para no romper importaciones.

### 3.3 Duplicidad del Inspector (C11) — **RESUELTO (D25)**

Existen dos `obtener_o_crear_dock_inspector` (`vdo_universal_inspector` y `vdo_inspector_dock`).
`universal` delega en `dock`. Antes de tocar la lógica del Inspector, decidir cuál es la API
canónica y eliminar la otra. Esto es la discusión de «legacy vs vigente» que pediste revisar después.

### 3.4 Nomenclatura — **NO SE RENOMBRA (D26)**

- Prefijo `vdo_` repetido en el paquete `freecad.vdo.*`. Es redundante pero no daña; renombrar es la
  Fase 7 del plan y se deja para después (riesgo alto: `importlib` dinámico).
- Decisión: **no renombrar ahora**. Se renombra cuando 3.1 esté cerrado, en el mismo cambio.

### 3.5 Pruebas contaminadas — **RESUELTO (D27)**

19 fallos preexistentes por mocks de FreeCAD que se instalan en `sys.modules` al importar
(`test_cajon_core`). Afecta a la confianza en la compuerta. Arreglo propuesto: no mockear si
FreeCAD real está disponible, o aislar por proceso (D19).

## 4. Verificación de H16 (BIM absorbió Arch)

**Confirmada.** En FreeCAD 1.1.3 (Flatpak) no existe `Mod/Arch`; los módulos `Arch*.py` están dentro de
`Mod/BIM/` (p. ej. `Mod/BIM/Arch.py`, `Mod/BIM/ArchWall.py`). Ruta de referencia:
`/var/lib/flatpak/app/org.freecad.FreeCAD/.../files/freecad/Mod/BIM/`.

## 5. Pantalla de inicio: no es extensible por terceros

Las tarjetas de la página de inicio están codificadas en C++ (`StartGui.so`): `Std_New`,
`PartDesign_Body`, `Assembly_CreateAssembly`, `Std_Open` y la tarjeta de proyecto arquitectónico
(BIM). No hay API de Python para añadir tarjetas. Lo único dinámico son los ejemplos (`.FCStd`
de carpetas de ejemplos) y los archivos recientes, que no abren el workbench.

**Decisión:** no se añade una tarjeta propia (requeriría parchear FreeCAD). La entrada equivalente es
«Nuevo proyecto VDO» en el menú Archivo de BIM (y el comando `VDO_AbrirVDO`, usable desde cualquier
barra o atajo). Si quieres tarjeta literal en el inicio, hay que proponerlo a FreeCAD upstream o
aceptar un parche local de la instalación; no lo recomiendo.

## 6. Pendiente de verificación en GUI

- Que «Nuevo proyecto VDO» aparezca en Archivo cuando BIM está activo. El manipulador usa el
  workbench activo; si FreeCAD monta los menús antes de cambiar el activo, la entrada no aparecerá
  al activar BIM. Síntoma: entrada visible solo tras cambiar de workbench dos veces. Causa probable
  si ocurre: orden de activación; solución: comprobar la entrada en `modifyMenuBar` con otro criterio.
- Que el canvas aparezca al elegir VDO en el desplegable sin documento abierto.

## 7. Cierre de la capa de workbench (sesión 5b)

### 7.1 Qué se hizo

- **Registro de piezas de UI (D24).** `core/vdo_ui_registry.py` (cargadores perezosos) y
  `ui/vdo_registro.py` (`registrar_piezas()`, llamado desde `InitGui.py`). El motor pide por clave:
  `panel.<tipo>`, `vista.<tipo>`, `colocacion.iniciar`, `dialogo.cerrar_activo`, `dialogo.mostrar`.
  Sin GUI el registro está vacío y el motor sigue funcionando.
- **ViewProviders movidos a `ui/vdo_view_providers.py`** (`VDOViewProviderBase`, `ViewProviderCoco`,
  `ViewProviderCajon`, `ViewProviderZocalo`, `ViewProviderPanel`, `ViewProviderPuerta`), junto con
  `reparar_viewprovider`, `enfocar_inspector_universal` y `abrir_panel_objeto`. `core/vdo_view_base.py`
  queda solo con clasificación (`_es_*`) y diagnóstico.
- **CLI del optimizador** movido de `core/` a `tools/vdo_optimizador_cli.py`.
- **Malla del plano 0** (`ui/vdo_plano_cero.py`): activa el Snapper de Draft con `show_always`, el mismo
  camino que `Draft_ToggleGrid`. Se llama desde `Activated()` y desde «Nuevo proyecto VDO».
- **Puente con BIM corregido** (`ui/vdo_bim_bridge.py`): el estado se actualiza con la señal
  `workbenchActivated` y, si cambia, se recarga el workbench activo. Así no depende del orden entre
  activación y montaje de menús.
- **Regla de capas comprobada** por `tests/test_capas_arquitectura.py` (AST: ni imports de `ui`,
  `FreeCADGui` ni Qt en `core/`, tampoco diferidos).

### 7.2 Decisiones

| ID | Decisión |
|---|---|
| D24 | El motor no importa `ui/`. Las piezas de interfaz se piden por clave al registro. |
| D25 | Canónico: `ui/vdo_inspector_dock.obtener_o_crear_dock_inspector`. Eliminada la copia legacy de `vdo_universal_inspector`. |
| D26 | **No renombrar símbolos ni módulos (Fase 7 cerrada sin ejecutar).** Motivo: los documentos `.FCStd` guardan la ruta de sus proxies Python; renombrar rompe documentos existentes. Sin necesidad funcional. Reversible si se decide lo contrario. |
| D27 | Pruebas: la comprobación de «sin GUI» es estática (AST), no `sys.modules` (global al proceso). `FreeCAD.__spec__` lo define el runner. Los mocks de `test_cajon_core` solo se instalan en modo puro. |

### 7.3 Resultados (solo consola; la GUI no se ha podido ejecutar aquí)

| Modo | Antes de esta fase | Ahora |
|---|---|---|
| Puro | 101 OK · 0 fallos · 12 errores (todos requieren FreeCAD) | 103 OK · 0 fallos · 11 errores (todos requieren FreeCAD) · 3 omitidos |
| FreeCAD | 115 · 5 fallos · 14 errores | **205 OK · 0 fallos · 0 errores · 5 omitidos** |

Comprobado además: las 13 claves del registro resuelven a piezas reales en `freecadcmd`; el ZIP
se regenera con los cambios.

### 7.4 Pendiente de verificación en GUI (no se puede hacer desde aquí)

1. Al elegir VDO en el desplegable sin documento: aparece el canvas **y la malla del plano 0**.
2. Con BIM activo: aparece «Nuevo proyecto VDO» en Archivo. Al salir de BIM, desaparece.
3. Las barras y comandos siguen funcionando tras mover los ViewProviders (sobre todo doble clic
   en un COCO, un cajón y un panel: deben abrir el Inspector).
4. Si algo falla en 3, el primer sospechoso es el registro (`registrar_piezas()` debe ejecutarse antes
   de `register_all()` en `InitGui.py`).
