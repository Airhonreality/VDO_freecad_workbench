# Arquitectura VDO

**Estado:** documento vigente tras la fase M11 del plan de minimalismo (2026-11-06).
**Fuente de reglas:** `docs/PLAN_MINIMALISMO_VDO.md` §2 (MN-01 a MN-13) y §3 (plantilla de archivo).
**Cifras:** de `docs/metricas/minimalismo_final.json` (salida de `tools/auditoria/minimalismo.py`) y de `docs/PROGRESO_MINIMALISMO.md`, sección M10. Ninguna cifra es estimada.
**Versión anterior:** `docs/archivo/ARQUITECTURA_anterior.md` (describía `app/` y puertos que ya no existen).

---

## 1. Capas

| Capa | Ruta | Archivos (`minimalismo.py resumen`) | Líneas | Responsabilidad | Puede importar |
|---|---|---:|---:|---|---|
| `core` | `freecad/vdo/core/` | 47 | 7.943 | Datos y cálculo puro. Sin FreeCAD ni Qt (P4). | Nada del paquete de capas (MN-03). |
| `cad` | `freecad/vdo/cad/` | 19 | 2.854 | Escritura en el documento FreeCAD: `FeaturePython`, propiedades, geometría. | `core` (MN-03). |
| `ui` | `freecad/vdo/ui/` | 79 | 14.374 | Qt y presentación: paneles de tarea, inspector, vistas, estilos (`ui/tema.py`). | `core` y `cad` (MN-03; decisión D-31). No escribe en FreeCAD. |
| `datos` | `freecad/vdo/datos/` | 2 `.py` + 3 JSON | (no medido) | Tablas de datos: `formularios.py` (especificación de formularios, MN-08), `valores.py` (valores de dominio, D-16). | No importa capas. |
| Entrada | `freecad/vdo/commands.py`, `creacion.py`, `qt_compat.py`; `Init.py` e `InitGui.py` en la raíz del repo | 3 `.py` en el paquete | (no medido) | Registro de comandos del workbench y arranque. | Todo (MN-03). |

Las 3 cifras de líneas y archivos de la tabla son las de la herramienta, que mide `core`, `ui`, `cad` y `app`. `app/` ya no existe (MN-01): `app` aparece en la medición con 0 archivos.

Cambio de estructura respecto a la base: `app/` (518 líneas de casos de uso y DTO) se eliminó. Su lógica pasó a `core/` (decisión) o a `cad/` (escritura). Ver `docs/adr/ADR-MN01-eliminar-app.md`.

---

## 2. Reglas de dependencia (MN-02, MN-03)

- **MN-02:** tres capas (`core`, `cad`, `ui`) más la entrada (`commands.py`, `Init.py`, `InitGui.py`).
- **MN-03:** `core` no importa `cad`, `ui` ni `app`. `cad` importa `core`. `ui` importa `core` y `cad`. La entrada importa todo.

**Verificación:**

| Comprobación | Dónde | Qué comprueba |
|---|---|---|
| Pruebas de capas | `tests/test_arquitectura.py` (clase `CapasTests`, 5 pruebas) | `ui` no importa `core`/`cad`/`app` de la API prohibida (D-31); `ui` no escribe en FreeCAD; `core` no importa `app`, `ui` ni `cad`; `app` no importa `ui`; `cad` no importa `ui` ni `app`. |
| Pruebas de capas (segundo conjunto) | `tests/test_capas_arquitectura.py` (2 pruebas) | `core` no importa interfaz ni Qt; el registro de `ui` no está en `core`. |
| Ciclos entre módulos | `python3 -I tools/auditoria/ciclos.py` | Componentes cíclicos y aristas `core->cad`. Salida actual: `ARISTAS core->cad: 0` y 3 componentes en `ui/` (ver §4). |

Nota: la lista de la primera fila es la que describe `tests/test_arquitectura.py`. No se ha revisado línea a línea el contenido de cada prueba en esta fase.

---

## 3. Plantilla de archivo (P5) y cómo se aplicó

Plantilla de `core/` y `cad/` (plan §3):

```
"""Una frase: qué concepto de dominio resuelve este archivo."""
# 1. DATOS     tablas constantes (dict, tuple, o carga de datos/*.json)
# 2. TIPOS     dataclasses inmutables de entrada y salida (plan)
# 3. CÁLCULO   funciones puras que devuelven planes; sin efectos
# 4. APLICACIÓN (solo cad/) funciones que escriben un plan en el documento
```

Plantilla de `ui/`: especificación de campos (desde `datos/`), construcción genérica (`ui/form_builder.py`) y `accept` de pocas líneas.

**Aplicación medida:**

| Regla | Resultado | Fuente |
|---|---|---|
| Archivo > 400 líneas | 0 (antes: 17) | `minimalismo.py tamano` (M10) |
| Función > 60 líneas | 0 (antes: 68) | `minimalismo.py tamano` (M10) |
| Módulo > 600 líneas | 0 | `find` + `wc -l` (M10) |
| Marca de sección DATOS/TIPOS/CÁLCULO en `core/` | 30 de 47 módulos | `grep` (M11); no hay verificador automático de la estructura por secciones |
| Marca de sección en `cad/` | 11 de 19 módulos | `grep` (M11), misma salvedad |
| Formularios desde especificación (MN-08) | Migrados completos: zócalo (D-70), panel (D-71), puerta (D-72) y cajón (D-73). Coco solo en campos simples, rotación y pestañas (D-74, D-75); el resto del panel de coco sigue a mano. `ui/form_builder.py` se usa en 21 archivos de `ui/` | `docs/DECISIONES_DELEGADAS.md` |

Lo no cumplido de la plantilla está en `docs/DEUDA_TECNICA.md`.

---

## 4. Excepciones declaradas

Estas excepciones están documentadas. Ninguna se ha dado por aprobada por el humano; ver `docs/PENDIENTES_HUMANO.md`.

1. **Tres funciones de `ui/` con 4 o más ramas, sin dividir** (medido por `minimalismo.py ramas`, M10):
   - `ui/inspector_arbol.py`: `_on_tree_item_clicked` (5 ramas) y `_on_selection_changed` (4).
   - `ui/view_providers.py`: `abrir_panel_objeto` (4).
   - No están ligadas a D-21 (que trata `generar_tiras_perimetrales` en `core`, y su gate de "ramas baja en 1" no se cumplió; ver DECISIONES_DELEGADAS). D-40 trata la división de `ui/coco_*` y no incluye estas tres. Quedan como deuda; no hay decisión registrada que las excluya.
2. **Una excepción tragada en `ui/`:** `ui/coco_unified_task.py` (`minimalismo.py excepciones` la cuenta en la línea 302, a nivel de módulo). La función que registra el error es `_fallar_accept` (línea 333), que llama a `App.Console.PrintError`. Decisión D-79.
3. **Ciclos en `ui/`** (no cubiertos por el plan, medidos con `tools/auditoria/ciclos.py`):
   - U-01: `ui/cutting_list_preview.py` y `ui/export_cutting_list.py`.
   - U-02: `ui/inspector_dock.py` y `ui/universal_inspector.py`.
   - U-03: `ui/coco_unified_task.py`, `ui/drag_handles.py` y `ui/view_providers.py`.
   - Requieren mover lógica entre módulos de UI. Pendientes en `docs/DEUDA_TECNICA.md`.
4. **Cuatro hojas de estilo locales fuera de `ui/tema.py`** (D-76): `ESTILO_WIDGET` en `ui/box_hoja_estilos.py`, `_ESTILO_CHASSIS` en `ui/chassis_estilos.py`, la hoja `estilo` en `ui/hardware_manager.py` y en `ui/reengrose_ui_construccion.py`. Son hojas de ventana completa; meterlas en `tema.py` lo llevaría por encima de 400 líneas (P5). Se aplican con `tema.aplicar_estilo`.
5. **Colores hex fuera de `tema.py`** en SVG, HTML y `QColor` de `ui/`: fuera del alcance de D-76 y sin resolver (MN-07). Ver `docs/DEUDA_TECNICA.md`.

---

## 5. Mapa de archivos

Generado con `find freecad/vdo -name "*.py" | sort` (agrupado por directorio, sin `__pycache__`).

| Directorio | .py (sin `__init__`) | Archivos |
|---|---:|---|
| `freecad/vdo//` | 3 | `commands.py`, `creacion.py`, `qt_compat.py` |
| `freecad/vdo/cad/` | 18 | `cajon.py`, `cajon_geometria.py`, `coco.py`, `coco_carcasa.py`, `coco_cortes.py`, `coco_divisiones.py`, `coco_espacios.py`, `coco_propiedades.py`, `coco_shell.py`, `colocacion.py`, `documento.py`, `edicion.py`, `geometria.py`, `guardian.py`, `panel.py`, `propiedades.py`, `puerta.py`, `zocalo.py` |
| `freecad/vdo/core/` | 46 | `aperturas.py`, `cajon_autotest.py`, `cajon_calculo.py`, `cajon_calculo_bloques.py`, `cajon_correderas.py`, `coco_core.py`, `coco_spaces.py`, `coco_spaces_bloques.py`, `consultar_herrajes.py`, `defaults.py`, `dto.py`, `errores.py`, `espacios_cajas.py`, `facade_contract.py`, `finish.py`, `frames.py`, `hardware_hub.py`, `helpers.py`, `layout_matriz.py`, `layout_modelo.py`, `layout_resolucion.py`, `layout_resuelto.py`, `manifest.py`, `module_props.py`, `module_specs.py`, `nesting.py`, `nesting_presets.py`, `optimizar_corte.py`, `optimizer_core.py`, `optimizer_core_resumen.py`, `optimizer_lista_corte.py`, `panel_core.py`, `paths.py`, `puerta_despiece.py`, `reengrose_despiece.py`, `reengrose_encuentros.py`, `reengrose_geometria.py`, `reengrose_interferencias.py`, `reengrose_modelo.py`, `reengrose_modificador.py`, `reengrose_modificador_normalizacion.py`, `reengrose_tiras.py`, `spaces.py`, `spaces_resumen.py`, `view_base.py`, `zocalo_core.py` |
| `freecad/vdo/datos/` | 2 | `formularios.py`, `valores.py` |
| `freecad/vdo/ui/` | 78 | `bim_bridge.py`, `box_canvas.py`, `box_config.py`, `box_constantes.py`, `box_construccion.py`, `box_controller.py`, `box_esquinas.py`, `box_estado.py`, `box_hoja_estilos.py`, `box_margen.py`, `cajon_task.py`, `cajon_task_cabecera.py`, `cajon_task_construccion.py`, `chassis_canvas.py`, `chassis_config.py`, `chassis_constantes.py`, `chassis_construccion.py`, `chassis_estado.py`, `chassis_estilos.py`, `chassis_eventos.py`, `chassis_widget.py`, `coco_arbol_pintado.py`, `coco_arbol_widgets.py`, `coco_construccion_widgets.py`, `coco_edicion_widgets.py`, `coco_inspector_widgets.py`, `coco_preview2d.py`, `coco_reengrose_widgets.py`, `coco_unified_celdas.py`, `coco_unified_construccion.py`, `coco_unified_escritura.py`, `coco_unified_espacios.py`, `coco_unified_pestanas.py`, `coco_unified_tabla.py`, `coco_unified_task.py`, `coco_unified_valores.py`, `cutting_list_menu.py`, `cutting_list_preview.py`, `drag_handles.py`, `export_cutting_list.py`, `form_builder.py`, `hardware_constantes.py`, `hardware_manager.py`, `hardware_resumen.py`, `inspector_acciones.py`, `inspector_arbol.py`, `inspector_cabecera.py`, `inspector_dock.py`, `inspector_pagina_pieza.py`, `inspector_pagina_vano.py`, `inspector_paginas.py`, `interfaz.py`, `nesting_workflow.py`, `optimizer_dialog.py`, `optimizer_preview.py`, `optimizer_view.py`, `panel_task.py`, `placement.py`, `plano_cero.py`, `puerta_task.py`, `puerta_task_cabecera.py`, `puerta_task_constantes.py`, `puerta_task_construccion.py`, `qt.py`, `reengrose_ui.py`, `reengrose_ui_config.py`, `reengrose_ui_constantes.py`, `reengrose_ui_construccion.py`, `reengrose_ui_estado.py`, `reengrose_ui_eventos.py`, `reengrose_ui_preview.py`, `registro.py`, `selection_bridge.py`, `task_base.py`, `tema.py`, `universal_inspector.py`, `view_providers.py`, `zocalo_task.py` |

Total: 147 archivos `.py` sin `__init__.py`, incluidos `datos/` y la raíz. La cifra de `minimalismo.py resumen` (145) equivale a core 47 + ui 79 + cad 19: no cuenta `datos/` ni los archivos de la raíz.

---

## 6. Cómo verificar

| Comprobación | Comando | Resultado esperado |
|---|---|---|
| Nivel 1 (sin FreeCAD) | `python3 -I tools/run_tests.py` | `RESUMEN ... fallos=0` |
| Nivel 2 (FreeCAD headless) | `freecadcmd tools/run_tests.py` | Ver `docs/PROGRESO_MINIMALISMO.md` (M10) |
| Ciclos | `python3 -I tools/auditoria/ciclos.py` | `ARISTAS core->cad: 0` |
| Métricas de la fase | `python3 -I tools/auditoria/minimalismo.py resumen` (y los demás subcomandos) | Ver `docs/metricas/minimalismo_final.json` |
| Instalación limpia | `tools/build_zip.py` (salida en `dist/`) | Ver `docs/PENDIENTES_HUMANO.md` (build) |

El nivel 3 (verificación visual en la GUI de FreeCAD) lo hace una persona; no está automatizado.

---

## 7. Decisiones de referencia

Las decisiones estructurales están en `docs/adr/` (un ADR por decisión MN-01 a MN-06 y MN-09; índice en `docs/adr/README.md`). El detalle de cada decisión delegada (D-xx) está en `docs/DECISIONES_DELEGADAS.md`.
