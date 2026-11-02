# Plan de conversión de VDO a Workbench de FreeCAD (versión 4)

> Versión 4 (y sesión 5, ver sección 6 Fase 6 y `docs/REVISION_ARQUITECTURA_CAPAS.md`): refleja la ejecución de la sesión 4 (2026-11-01/02). Las versiones 1–3 se
> resumen en la sección 11. **Fuente única de decisiones: sección 7.**
>
> **Estado:** Fases 0–5 ejecutadas. Fases 6 y 7 no ejecutadas (motivo en la sección 6, Fases 6 y 7).
> Verificación en GUI **pendiente** (el entorno no permite comprobarla; ver sección 8).

---

## 1. Resumen ejecutivo

VDO es un workbench de FreeCAD **propietario**, de código no público. Se distribuye como
**ZIP versionado** por un canal privado (`dist/VDO-<versión>.zip`). No se usa el Addon Manager.

Hechos verificados que condicionan el diseño:

1. **La raíz del repositorio es la raíz del módulo.** `Init.py` e `InitGui.py` van en la raíz.
2. **Qt es PySide6** en FreeCAD 1.1.3 (PySide6 6.11.1 presente, PySide2 ausente).
3. **Durante `Init.py` no existen `__file__` ni `GuiUp`.** Se localiza la carpeta del módulo
   desde `sys.path`. `GuiUp` existe tras el arranque (vale `0` en consola).
4. **En FreeCADCmd, `import FreeCADGui` tiene éxito.** Un `try/except ImportError` no separa
   consola de GUI: hay que importar la GUI de forma perezosa.
5. **El paquete `freecad` es un espacio de nombres compartido** (FreeCAD y addons). El repo
   no añade `freecad/__init__.py`.

Estado del código: `freecad/vdo/` contiene el motor (`core/`), la interfaz (`ui/`), los
comandos (`commands.py`) y la capa Qt (`qt_compat.py`). `Macro/` se ha retirado.

---

## 2. Hipótesis validadas

Estado: **Confirmada** = comprobada ejecutando o leyendo código real; **Refutada** = la evidencia
la contradice; **Parcial** = cierta con matices; **No verificada** = abierta.

| ID | Hipótesis (plan o investigación) | Estado | Evidencia |
|---|---|---|---|
| H1 | FreeCAD ejecuta `Init.py` de una carpeta en `Mod/` en modo consola | **Confirmada** | `freecadcmd` ejecuta `Init.py` del módulo; imprime `[VDO] Módulo cargado desde: …` |
| H2 | Un `Init.py` anidado en `Mod/<x>/Mod/VDO/` se carga | **Refutada** | Prueba con `Mod/ZZ_T_nested/Mod/VDO/Init.py`: sin salida |
| H3 | Comprobar `App.GuiUp` durante la carga de `Init.py` | **Refutada** (C1) | Durante `Init.py` no existe; tras el arranque vale `0` |
| H4 | Ruta Linux `~/.local/share/FreeCAD/Mod/` | **Refutada para Flatpak** | Flatpak usa `~/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/` |
| H5 | Qt de FreeCAD 1.1 es PySide2 | **Refutada** | PySide6 6.11.1 presente; PySide2 ausente |
| H6 | El Addon Manager instala el repo completo en `Mod/<nombre>/` | **Confirmada** (código) | No aplica: distribución por ZIP (D5) |
| H7 | `<subdirectory>` indica dónde está el workbench | **Parcial** | No aplica: distribución por ZIP |
| H8 | API: `appendToolbar`, `appendMenu`, `addCommand`, `"Gui::PythonWorkbench"` | **Confirmada** (uso) | `Initialize()` registra comandos y barras; no se ha visto en GUI (sección 8) |
| H9 | Métodos de TaskPanel `getStandardButtons`, `isAllowedAlter*` | **Confirmada** (presencia) | Cadenas presentes en la instalación |
| H10 | Los `.FCMacro` usan `exec()` | **Refutada** | Los `.FCMacro` eran bootstrap + `import` + una llamada; los comandos nuevos no usan `exec()` |
| H11 | El motor del núcleo no importa GUI | **Confirmada** (C5, C6) | `test_headless_core`: importar `freecad/vdo/core/` no carga `FreeCADGui` ni PySide |
| H12 | Dependencias PyPI a declarar | **Confirmada: ninguna** | `jsonschema` es opcional (`try`). Nesting Workbench es un addon externo, no PyPI |
| H13 | La suite de tests sirve como compuerta | **Confirmada** | Runner único `tools/run_tests.py`; línea base registrada (sección 6, Fase 2) |
| H14 | `node_modules` no debe estar versionado | **Confirmada y resuelta** | Retirado del índice (841 ficheros) y en `.gitignore` |
| H15 | El inventario del plan es completo | **Refutada** | `Macro/` tenía 62 `.py`, 13 `.FCMacro` y módulos no listados (sección 3, histórico) |
| H16 | BIM absorbió Arch en FreeCAD 1.0 | **Confirmada** | En FreeCAD 1.1.3 no existe `Mod/Arch`; los `Arch*.py` están en `Mod/BIM/` (sesión 5) |
| H17 | `package.xml` `format="1"` con namespace `https://wiki.freecad.org/Package_Metadata` | **Confirmada** (uso) | Igual que el `package.xml` del Addon Manager; la especificación oficial no se ha leído |

---

## 3. Estado del repositorio

**Actual (tras la Fase 3):**

```
VDO_freecad_workbench/
├── package.xml            manifiesto (versión 1.1.0, licencia propietaria)
├── Init.py                fase de consola (sin GUI)
├── InitGui.py             fase GUI: VDOWorkbench, barras y menú
├── LICENSE                placeholder pendiente de revisión legal (D10)
├── README.md              instrucciones de instalación para el usuario final
├── freecad/               paquete (espacio de nombres; sin __init__.py en freecad/)
│   └── vdo/
│       ├── __init__.py
│       ├── commands.py    14 comandos + BARRAS + register_all()
│       ├── qt_compat.py   PySide6 → PySide2 → PySide
│       ├── core/          motor (28 módulos + vdo_manifest.json + vdo_hardware_catalog.json)
│       └── ui/            interfaz (25 módulos)
├── Resources/icons/       10 SVG
├── tests/                 18 suites + test_headless_core + test_comandos_workbench
├── docs/                  este plan, matriz, línea base, resultados y documentación previa
├── tools/                 run_tests.py, matriz_mapeo.py, build_zip.py, vdo_erp_sync/
└── dist/                  ZIP generados (no versionado)
```

**Histórico (antes de la Fase 3):** el código vivía en `Macro/` (62 `.py`, 13 `.FCMacro`,
18 suites de test). Se retiró en la sesión 4; los cambios todavía no están commiteados.

---

## 4. Comparación con la investigación (`workbench investigation.txt`)

### 4.1 Coincidencias

- Separación App/Gui; `Init.py` sin `FreeCADGui` ni PySide; `InitGui.py` solo con GUI.
- Carga diferida en `Initialize()`; `GetClassName() → "Gui::PythonWorkbench"`.
- Patrón `Command` (`GetResources`, `IsActive`, `Activated`) y `Gui.addCommand`.
- TaskPanel preferido sobre QDialog.
- `package.xml` en la raíz, con `<python-depend>` vacía (D8).
- Opción C (workbench autónomo, inyección opcional en BIM con fallback) como recomendación.

### 4.2 Contradicciones internas de la investigación

- **Layout**: la sección 2 pone el módulo en `Mod/VDO/`, pero su ejemplo usa `<subdirectory>./`.
  La prueba H2 da la razón al ejemplo: la raíz del repo es la raíz del módulo.
- **Namespace**: `vdo/` frente a `freecad/MiWorkbench/`. Resuelto con D2.

### 4.3 Errores o afirmaciones desactualizadas

| # | Afirmación | Corrección aplicada |
|---|---|---|
| E1 | Ruta Linux `~/.local/share/FreeCAD/Mod/` | No se escriben rutas: el módulo se localiza desde `sys.path` (D4) |
| E2 | `FreeCAD.getHomePath()` para localizar el módulo | Prefijo de instalación, no sirve. Se localiza desde `sys.path` en `Init.py`/`InitGui.py`; en el resto del código, `__file__` |
| E3 | `from PySide2 import …` | `freecad/vdo/qt_compat.py` (D17) |
| E4 | `App.GuiUp` "devuelve True" en `InitGui` | En `InitGui.py` no hace falta; en `Init.py`, `getattr(App, "GuiUp", False)` |
| E5 | `Init.py` registra importadores con `addImportType` | No aplica: VDO no define tipos de archivo propios |
| E6 | "Estructura estándar 100% validada" | No validada. No aplica a la distribución ZIP |
| E7 | `accept()` llama a `Gui.Control.closeDialog()` | Sin verificar en GUI (sección 8) |
| E8 | "A partir de FreeCAD 1.0, Arch → BIM" | Sin fuente (H16) |
| E9 | Atribuciones "Estándar Addon Academy" | Sin enlace; no se citan |
| E10 | `deleteLater` obligatorio | Tratado como recomendación |

---

## 5. Estructura objetivo

Ya implementada (ver 3). Reglas:

- El paquete `freecad/vdo/` no contiene scripts de consola ni `exec()`.
- Fuera del paquete (no se empaqueta): `tests/`, `tools/`, `docs/`, `dist/`, `.git/`, `.claude/`.
- `freecad/` **no** tiene `__init__.py` (espacio de nombres compartido; comprobado por
  `test_headless_core.test_freecad_no_tiene_init_en_el_repo`).

---

## 6. Plan por fases (con compuertas)

Cada fase termina con una compuerta. Estado: **Hecho** / **Parcial** / **No ejecutado**.

### Fase 0 — Inventario y limpieza — **Hecho**

| Tarea | Estado |
|---|---|
| Retirar `node_modules/` del índice y añadirlo a `.gitignore` | **Hecho** (sin commit) |
| Runner único `tools/run_tests.py` (modo puro y modo FreeCAD) | **Hecho** |
| Matriz de mapeo con `ast` (`tools/matriz_mapeo.py` → `docs/MATRIZ_MAPEO.md`) | **Hecho** (histórica: lee `Macro/`, ya retirado) |
| Línea base de tests (`docs/BASELINE_TESTS_*.txt`, generada desde `HEAD` antes de migrar) | **Hecho** |
| Investigar avisos de iconos | **Hecho**: causa en `user.cfg` (ver 8.6, D13) |

**Compuerta:** cumplida. `node_modules` fuera del índice; matriz; línea base; icono investigado.

### Fase 1 — Esqueleto en la raíz — **Hecho** (GUI pendiente)

| Tarea | Estado |
|---|---|
| `package.xml` (versión 1.1.0, licencia `LicenseRef-VDO-Proprietary`, `<subdirectory>./`) | **Hecho** |
| `Init.py`: sin GUI; localiza el módulo desde `sys.path` | **Hecho** (probado) |
| `InitGui.py`: clase `VDOWorkbench`; icono en la instancia (C3) | **Hecho** |
| Icono `Resources/icons/vdo_workbench.svg` | **Hecho** |

**Compuerta:**
- `Init.py` se ejecuta sin errores en consola: **cumplida**.
- El workbench aparece en el selector de la GUI: **no verificada** (sección 8.2).

### Fase 2 — Motor y UI dentro del paquete — **Hecho**

Desviación respecto al plan original, decidida en esta sesión (D16): **también se movió la UI a
`freecad/vdo/ui/`** en esta fase. Motivo: varios módulos del motor importan módulos de UI de forma
diferida (`from … import` dentro de funciones). Con el motor en el paquete y la UI en `Macro/`,
el paquete dependería de `Macro/` en `sys.path`, que es justo lo que D3/D4 prohíben.

| Tarea | Estado |
|---|---|
| Motor en `freecad/vdo/core/` (27 módulos del motor + `vdo_view_base`) con nombres conservados (D18) | **Hecho** |
| UI en `freecad/vdo/ui/` (25 módulos) | **Hecho** |
| Imports reescritos a rutas de paquete (`from freecad.vdo.core import …`); sin `sys.path` | **Hecho** |
| Cadenas de `importlib` de `vdo_module_specs.py` a rutas completas | **Hecho** |
| `vdo_manifest.json` y `vdo_hardware_catalog.json` junto al código que los lee | **Hecho** |
| Prueba headless (`tests/test_headless_core.py`) | **Hecho** (C5, D19) |
| Comprobación de colisión del paquete `freecad` (D2) | **Hecho** (C6) |
| Registro de línea base (`docs/BASELINE_TESTS_*.txt`) | **Hecho** |

Excluidos del paquete en esta fase, retirados en la Fase 3: `vdo_clone`, `vdo_install`,
`vdo_toolbar_inject`, `vdo_toolbar_test`, `vdo_publish`, `vdo_sync`, `vdo_sync_config` (D14).

**Compuerta:** prueba headless en verde; ningún test que pasa en la línea base deja de pasar.
**Resultado:** cumplida en ambos modos. Ver sección 10.

### Fase 3 — Comandos y TaskPanels — **Hecho** (GUI pendiente)

| Tarea | Estado |
|---|---|
| `freecad/vdo/commands.py`: una clase `Command` por acción (14) + `register_all()` | **Hecho** |
| `Activated()` con import diferido; sin lógica de negocio | **Hecho** |
| Todos los `.FCMacro` migrados (D15): creación (7), herramientas (6), Inspector | **Hecho** |
| Diálogos embebidos en macros trasladados a `ui/` (`vdo_optimizer_dialog.py`, `vdo_cutting_list_menu.py`) | **Hecho** |
| PySide directo eliminado: todo pasa por `qt_compat` | **Hecho** (D17) |
| `exec()` eliminado del código | **Hecho** (verificado por `SinExecTests`) |
| Retirada de `Macro/` | **Hecho** (confirmación previa del supervisor) |

**Compuerta:**
- Cada comando crea su efecto sin errores **en consola** (probado: los 14 se construyen, sus
  iconos existen, y los de creación crean objetos reales).
- Cada comando funciona **en GUI**: **no verificada** (sección 8.2).
- No hay `exec()`: **cumplida**.

### Fase 4 — Registro y menús — **Hecho** (GUI pendiente)

- `Initialize()`: `register_all()`, dos barras (`VDO · Creación`, `VDO · Herramientas`) y menú `VDO`.
- `Activated()`: muestra el Inspector Universal lateral (comportamiento del legacy).
- Sin preferencias: no hay opciones reales que exponer (la regla del plan se cumple).

**Compuerta:** toolbar y menú visibles al activar el workbench: **no verificada** (sección 8.2).

### Fase 5 — Empaquetado y distribución (ZIP) — **Hecho** (instalación en GUI pendiente)

- `tools/build_zip.py` genera `dist/VDO-<versión>.zip` (77 ficheros). La versión sale de `package.xml`.
- Incluye: `package.xml`, `Init.py`, `InitGui.py`, `LICENSE`, `README.md`, `freecad/`, `Resources/`.
- Excluye: `tests/`, `tools/`, `docs/`, `dist/`, `.git/`, `.claude/`, cachés de Python.
- `README.md` con instalación manual en `Mod/` (rutas de Linux nativo, Flatpak, Windows, macOS).
- **Prueba**: el ZIP descomprimido en `Mod/VDO` carga el paquete, registra 14 comandos y sus
  iconos existen (arranque de FreeCAD con `--disable-addon VDO` para aislarlo del enlace de
  desarrollo). Limitación del arnés: el espacio de nombres `freecad` se añade a mano porque
  lo calcula el arranque (sección 8.4).

**Compuerta:** el ZIP carga en consola desde una carpeta `Mod/` limpia: **cumplida**. En GUI: **no verificada**.

### Fase 6 — Integración con BIM — **Parcial** (sesión 5)

H16 verificada. Se implementa la Opción C: VDO sigue siendo autónomo y añade «Nuevo proyecto VDO»
al menú Archivo cuando BIM está activo (`freecad/vdo/ui/vdo_bim_bridge.py`, API
`Gui.addWorkbenchManipulator`, la misma que usa BIM). Sin dependencia en `package.xml` (D21).
**Verificación en GUI pendiente** (ver `docs/REVISION_ARQUITECTURA_CAPAS.md`, sección 7.4).

### Fase 7 — Renombrar símbolos al namespace limpio — **No ejecutada**

Solo si hace falta (plan original). Riesgo alto: `importlib` dinámico y más de 60 módulos.
No hay necesidad funcional hoy; se deja como trabajo futuro con su propia compuerta de tests.

---

## 7. Decisiones (fuente única)

Estado: **Cerrada** = decidida y aplicada. **Requiere tu acción** = no la puede cerrar el asistente.

| ID | Decisión | Estado | Motivo |
|---|---|---|---|
| D1 | Raíz del repo = raíz del módulo | **Cerrada** | H2 |
| D2 | Paquete Python `freecad/vdo/`, sin `__init__.py` en `freecad/` | **Cerrada** | Comprobado: `freecad` es espacio de nombres en FreeCAD y addons (C6) |
| D3 | **Sin shims.** `Macro/` retirado en la Fase 3 | **Cerrada** | No hay usuarios externos. Confirmación previa del supervisor (sesión 4) |
| D4 | El código no depende de la instalación: no escribe rutas fijas; localiza su carpeta desde `sys.path` (en `Init`/`InitGui`) o desde `__file__` (en el resto) | **Cerrada** | Requisito del usuario. `vdo_paths.py` reducido a rutas del repo |
| D5 | Distribución: ZIP versionado por canal privado. Sin Addon Manager | **Cerrada** | Código propietario |
| D6 | BIM: post-MVP; no ejecutada en esta sesión | **Cerrada** | No bloquea; H16 sin verificar |
| D7 | MVP: crear hoja, panel estándar, panel fachada, COCO 4C, panel división, zócalo, Inspector Universal | **Cerrada** (ampliada por D15) | El inspector es la dirección de UI actual |
| D8 | Sin `<python-depend>` | **Cerrada** | H12. Nesting Workbench es un addon externo, no una dependencia PyPI |
| D9 | Runner: `tools/run_tests.py` en modo puro (`python3`) y modo FreeCAD (`freecadcmd`) | **Cerrada** | Un único runner; resultados por test en `docs/*_TESTS_*.txt` |
| D10 | **Licencia propietaria.** `LICENSE` contiene un aviso de derechos reservados marcado como **pendiente de revisión legal**. Antes de distribuir, revisar la política de propiedad intelectual de la universidad | **Requiere tu acción** (texto legal) | Decisión legal del titular |
| D11 | Versión `1.1.0` | **Cerrada** | `package.xml` es la única fuente |
| D12 | Visibilidad del repo en GitHub (público o privado) | **Requiere tu acción** si el repo es público | Si es público, el código es visible aunque se distribuya por ZIP |
| D13 | Limpieza de `user.cfg`: eliminar `Std_Macro_*`, sus accesos rápidos y la barra `CARPINTERIA - VDO` que referencian `.FCMacro` **ya borrados** | **Requiere tu acción** | El sistema de permisos bloqueó la edición en la sesión anterior. Ahora la entrada apunta a ficheros que ya no existen |
| D14 | **Se retiran las herramientas de sincronización** (`vdo_sync`, `vdo_sync_config`, `vdo_publish`) y los auxiliares del modelo de carpeta de macros (`vdo_clone`, `vdo_install`, `vdo_toolbar_inject`, `vdo_toolbar_test`) | **Cerrada** | Copiaban `Macro/` ↔ carpeta de macros de FreeCAD: ese modelo ya no existe con el ZIP. Recuperables desde `HEAD` |
| D15 | **Se migran todos los `.FCMacro`, no solo el MVP** | **Cerrada** | Borrar `Macro/` sin migrarlos perdía funciones (optimizador, lista de corte, nesting, herrajes, puerta, cajón, editar). Supersede "el resto, después" del plan original |
| D16 | **La UI se mueve en la Fase 2, no en la 3** | **Cerrada** | El motor importa UI de forma diferida; mover solo el motor obligaba a depender de `Macro/` en `sys.path` |
| D17 | `freecad/vdo/qt_compat.py` es la única puerta a Qt (PySide6 → PySide2 → PySide). `ui/vdo_qt.py` conserva solo los widgets | **Cerrada** | FreeCAD 1.1 trae PySide6; PySide6 no expone widgets en `QtGui` (verificado: `QtGui.QLabel` no existe) |
| D18 | **Nombres de módulo conservados** en la Fase 2 (sin `panel_core`, etc.) | **Cerrada** | El plan original se contradecía (decía conservar nombres y daba un ejemplo que los cambia). Renombrar = Fase 7 |
| D19 | La prueba headless se ejecuta en un **proceso FreeCAD hijo** | **Cerrada** | `test_cajon_core` sustituye `sys.modules["FreeCAD"]` por un mock al importarse: contaminaría el proceso |
| D20 | Nesting Workbench ausente: el comando muestra un mensaje; no cierra FreeCAD | **Cerrada** | `sys.exit` al importar cerraba FreeCAD (C7) |
| D21 | Integración BIM por manipulador (Opción C), sin `<depend>BIM</depend>` | **Cerrada** | VDO debe funcionar sin BIM; el manipulador se degrada en silencio (sesión 5) |
| D22 | Tarjeta literal en la página de inicio: **no** se implementa | **Cerrada** | Las tarjetas de inicio de FreeCAD están codificadas en C++ (`StartGui.so`); se sustituye por la entrada del menú Archivo de BIM y `VDO_AbrirVDO` |
| D23 | Registro de comandos al cargar la GUI, no en `Initialize()` | **Cerrada** | BIM monta sus menús al activarse; los comandos deben existir antes |
| D24 | El motor no importa `ui/`: las piezas de interfaz se piden por clave al registro (`core/vdo_ui_registry.py`); los ViewProviders pasan a `ui/vdo_view_providers.py` | **Cerrada** | Dependencia circular core↔ui (`docs/REVISION_ARQUITECTURA_CAPAS.md`, 3.1) |
| D25 | Canónico del Inspector: `ui/vdo_inspector_dock.obtener_o_crear_dock_inspector`; eliminada la copia legacy | **Cerrada** | C11 |
| D26 | No renombrar símbolos ni módulos (Fase 7 no ejecutada) | **Cerrada** | Los `.FCStd` guardan rutas de proxies Python; renombrar rompe documentos existentes |
| D27 | Pruebas: aislamiento estático de GUI; mocks de FreeCAD solo en modo puro; `FreeCAD.__spec__` lo define el runner | **Cerrada** | Causa de los 19 fallos preexistentes (contaminación del proceso) |

---

## 8. Verificaciones pendientes

1. Especificación oficial de `package.xml` (wiki `Package_Metadata`). No consultada.
2. **Prueba en GUI** (Fases 1, 3, 4). **No verificada.** Hallazgos de intentos anteriores:
   - Los overrides de Flatpak fijan `QT_QPA_PLATFORM=xcb`; `offscreen` debe pasarse con `--env`.
   - Pasar un `.py` como argumento de la GUI no ejecuta el script.
   - Una sonda temporal en `Mod/` no produjo salida en varios minutos.
   - Un `FreeCAD --help` previo provocó un SIGSEGV dentro de Qt.
   - **Prueba manual pendiente:** abrir FreeCAD, seleccionar el workbench VDO, comprobar barras
     y menú, y pulsar cada comando. Anotar cualquier error de la consola de FreeCAD.
3. Probar `accept()` / `closeDialog()` en un TaskPanel real (E7). Pendiente de la prueba en GUI.
4. Instalación del ZIP en un FreeCAD con GUI. La prueba de consola está hecha (Fase 5); la de GUI no.
5. Verificar la afirmación de BIM/Arch (E8, H16). Bloquea la Fase 6.
6. **Avisos de iconos** `Cannot find icon: vdo_panel / vdo_coco_2 / vdo_workbench / vdo_cajon`.
   **Causa:** `user.cfg` (`~/.var/app/org.freecad.FreeCAD/config/FreeCAD/v1-1/user.cfg`) contiene
   definiciones `Std_Macro_0`–`5` que apuntan a `.FCMacro` que ya no existen, más accesos rápidos
   y la barra `CARPINTERIA - VDO`. **Acción:** D13.
7. ~~Comprobar si `vdo_publish.py` / `vdo_sync.py` copian algo sensible~~ **Resuelto por D14:** se retiraron.

---

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Estado / mitigación |
|---|---|---|
| Comandos sin probar en GUI | Alto | Abierto: prueba manual (8.2) |
| `user.cfg` apunta a macros borradas | Medio | Abierto: D13 |
| Módulo anidado en `Mod/VDO/` no se carga | Alto | Mitigado: raíz = módulo (D1; H2) |
| Espacio de nombres `freecad` calculado antes de añadir el módulo | Medio | Riesgo real en arranques atípicos. En arranque normal FreeCAD añade `Mod/*` a `sys.path` antes de ejecutar `Init.py`. Verificado solo en consola (8.4) |
| Dependencia de Nesting Workbench (addon externo) | Bajo | Mitigado: `ImportError` capturado; mensaje al usuario (D20) |
| Acoplamiento motor → UI (`vdo_view_base` y módulos con importaciones diferidas de `ui/`) | Medio | Deuda: el motor depende de la UI de forma diferida. Desacoplar en una fase posterior |
| Tests que dependen de `_MockApp` | Medio | Deuda: 19 tests fallan igual que en la línea base (sección 10) |
| Renombrado masivo de símbolos | Alto | Fase 7 separada, no ejecutada |
| Borrado irreversible fuera de git | Alto | Mitigado: todo está en `HEAD` y el borrado de `Macro/` fue confirmado |

---

## 10. Evidencia

### 10.1 Tests (`tools/run_tests.py`; ficheros en `docs/`)

| Modo | Línea base (`HEAD`, antes de migrar) | Final | Regresiones |
|---|---|---|---|
| Puro (`python3`) | 100 ejecutados · 0 fallos · 12 errores | 101 ejecutados · 0 fallos · 12 errores (89 OK; 8 no ejecutados porque necesitan FreeCAD) | **Ninguna** |
| FreeCAD (`freecadcmd`) | 106 ejecutados · 5 fallos · 14 errores · 22 no ejecutados | 115 ejecutados · 5 fallos · 14 errores · 22 no ejecutados (99 OK) | **Ninguna** |

- Los 12 errores puros son importaciones que requieren FreeCAD (`ModuleNotFoundError`).
- Los 22 no ejecutados en FreeCAD son los mismos que en la línea base: tests que `setUpClass` no deja correr (ver 10.2).
- Los 5 fallos y 14 errores de FreeCAD son **los mismos ids** que en la línea base (ver 10.2).
- Nuevas: `test_headless_core` (3), `test_comandos_workbench` (6, incluida la prueba estática de `exec()`).
- Los 3 headless no se ejecutan en modo puro: se saltan con motivo, y se registran como `NO_EJECUTADO`.

### 10.2 Fallos preexistentes (no introducidos por la migración)

| Causa | Tests afectados | Nota |
|---|---|---|
| `test_cajon_core` sustituye `sys.modules["FreeCAD"]` por `_MockApp` al importarse | 9 tests (`test_gui_wiring`, `test_vdo_zocalo`, `setUpClass` de 3 suites) y 4 de `test_vdo_agnosticism` / `test_hardware_hub` (`FreeCADGui` cargado por otros tests) | Deuda de tests. Arreglo: no mockear si FreeCAD existe, o aislar por proceso |
| `SystemExit: 1` al importar (`test_coco_reengrose`, `test_coco_reengrose_avanzado`, `test_reengrose_l1`) | 3 | Módulos de prueba que llaman `sys.exit` al importar |
| `FreeCAD.__spec__ is not set` (`importlib.util.find_spec` dentro de FreeCADCmd) | 3 (`test_puerta_core`, `test_selection_bridge`, `test_universal_inspector`) | Corregido en `test_headless_core` y `test_comandos_workbench`; pendiente en los demás |
| `test_smoke_l3_desk_assembly` con ruta fija `/home/javi/.local/share/FreeCAD/Macro` | 0 ejecutados | Ruta de otra máquina |

### 10.3 Correcciones de la sesión 4 (verificadas)

- **C5.** `vdo_view_base` hacía `import FreeCADGui` en un `try`. En FreeCADCmd ese import **sí** tiene
  éxito. Corregido con `_gui()` perezoso (mismo contrato: `None` sin GUI).
- **C6.** `freecad/` no tiene `__init__.py` en FreeCAD ni en `Mod/freecad.gears` (espacio de nombres). D2 cerrada.
- **C7.** `vdo_nesting_workflow`, `vdo_export_cutting_list` y `vdo_cutting_list_preview` llamaban
  `sys.exit(1)` al importarse. Sustituido por `ImportError`.
- **C8.** `vdo_coco_spaces_task` usaba `QtGui.QSeparate(QtGui.QSeparator(...))`, que no existe en
  ninguna versión de Qt. Sustituido por un separador `QFrame` vertical. Además, 290 referencias a
  clases de widget estaban bajo `QtGui` (válido con PySide antiguo, no con PySide6).
- **C9.** `vdo_cajon_task` usaba `QtWidgets` sin importarlo. Ya fallaba en `HEAD`. Corregido con `qt_compat`.
- **C10.** El runner colapsaba errores repetidos (`_ErrorHolder`) y marcaba como `OK` los tests que
  no llegaban a ejecutarse. Corregido; la línea base se regeneró con el mismo runner.
- **C11.** Existen dos `obtener_o_crear_dock_inspector` (en `vdo_universal_inspector` y `vdo_inspector_dock`).
  El de `universal` delega en el consolidado de `dock`. Se mantiene la API de `universal`.

---

## 11. Histórico de versiones y correcciones previas

**Versión 1–2 (sesiones 1–2):** plan original; decisiones D1–D9; hipótesis H1–H17; correcciones C1–C4
(`GuiUp` y `__file__` no existen durante `Init.py`; `InitGui` no ve variables de módulo en el cuerpo de
la clase; `PySide2` obsoleto).

**Versión 3 (sesión 3):** auditoría; D3 contradictoria (shims) eliminada; sección 7 unificada; línea base
con dos modos de ejecución; número de suites corregido (18); distribución por ZIP.

**Versión 4 (sesión 4):** ejecución completa de las fases 0–5 (6 y 7 no ejecutadas, con motivo).
Decisiones D14–D20. Correcciones C5–C11. Retirada de `Macro/`.

**Pendiente de la sesión 4 (acciones del usuario):**
1. Prueba manual en GUI (8.2).
2. Texto legal de `LICENSE` (D10).
3. Decidir sobre D12 (visibilidad del repo) y D13 (limpieza de `user.cfg`).
4. Revisar `git status`: hay cambios en el índice (renombrados, borrados y nuevos) **sin commit**.
