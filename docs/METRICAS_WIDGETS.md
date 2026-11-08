# Métricas de construcción de widgets a mano en `freecad/vdo/ui/`

Medición de F9 (D-95). **Sin cambio de código.** Solo lectura del árbol y este documento.

## Método

- Inventario: AST sobre `freecad/vdo/ui/*.py` (124 funciones o métodos, incluidos anidados como `Clase.metodo`). Se cuenta cada función que contiene alguna de estas llamadas: `QLabel(`, `QDoubleSpinBox(`, `QSpinBox(`, `QComboBox(`, `QCheckBox(`, `QLineEdit(`, `addWidget(`, `addRow(`, `setRange(`, `setToolTip(`. Columna «Llamadas a constructores» = solo las seis primeras; columna «Llamadas a patrones» = las diez.
- Clasificación: lectura de cada función. **A** = crea campos (etiqueta + entrada) con valor, rango o tooltip y los añade a un layout. **B** = campos más lógica visual (botones con acción, listas o tablas). **C** = presentación: etiquetas de estado, botones sin campos, árboles, canvas, cabeceras y widgets propios. Las funciones de `form_builder.py` se cuentan en C como infraestructura.
- Ahorro: para A y B, `bruto = líneas actuales - (1 + campos)`, donde 1 es la llamada que queda en `ui/` y `campos` es una línea de especificación por campo (en `datos/`, contada como coste). Como criterio conservador, el **ahorro neto estimado = bruto / 2**. Las señales, las validaciones y los botones siguen en el panel y no se descuentan de forma explícita: la mitad cubre ese margen. Ahorro 0 cuando la función ya es genérica o ya está migrada.
- Medida: líneas del `def` a su último renglón (incluye comentarios y líneas en blanco). Es una estimación estática, no verificada en ejecución.

## Totales por clasificación

| Clase | Funciones | Líneas actuales | Ahorro bruto (líneas) | Ahorro neto estimado (bruto/2) |
|---|---:|---:|---:|---:|
| A. Patrón de formulario | 26 | 514 | 414 | 207.0 |
| B. Mixta | 7 | 240 | 199 | 99.5 |
| C. Presentación | 91 | 1633 | 0 | 0.0 |
| **Total** | **124** | **2387** | **613** | **306.5** |

Líneas totales de `freecad/vdo/ui/*.py`: **13461**. Las funciones medidas suman 2387 líneas (17.7 %).
Ahorro neto estimado: **306.5 líneas**, es decir **2.28 %** de `freecad/vdo/ui/` (ahorro bruto **613 líneas**, **4.55 %**). Las líneas de especificación ya están restadas.

## Tabla por función

| Archivo | Función | Clase | Líneas actuales | Llamadas a constructores | Llamadas a patrones | Campos (spec) | Ahorro neto estimado | Nota |
|---|---|:---:|---:|---:|---:|---:|---:|---|
| box_construccion.py | `BoxConstruccionMixin._spin` | C | 7 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| box_construccion.py | `BoxConstruccionMixin._construir_barra_superior` | B | 26 | 2 | 8 | 2 | 11.5 | dos casillas (activar, sincronizar); boton All fuera |
| box_construccion.py | `BoxConstruccionMixin._construir_esquinas` | C | 31 | 1 | 2 | - | 0.0 | botones de esquina con icono y combos legacy ocultos; no es un formulario; desclasificada en D-118, no se migra |
| box_construccion.py | `BoxConstruccionMixin._construir_bordes` | C | 46 | 0 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| box_construccion.py | `BoxConstruccionMixin._construir_centro` | C | 31 | 0 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| box_construccion.py | `BoxConstruccionMixin._construir_selector_margenes` | C | 17 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| box_construccion.py | `BoxConstruccionMixin._construir_panel_medidas` | A | 31 | 3 | 13 | 3 | 13.5 | ancho, offset, espesor; migrada en F-UI-2b: árbol de widgets idéntico (snapshot de box sin cambios entre commits, `git diff <commit1> -- tests/fixtures/box_panel_medidas_snapshot.json` vacío), `FormBuilder.construir_rejilla` con `BOX_PANEL_MEDIDES` y 3 campos en `datos/formularios.py` (incl. `texto_especial: "Auto"`); ahorro real 21 líneas en `box_construccion.py` (325 → 304; función 31 → 8), parcialmente compensado por +17 en `form_builder.py` por `construir_rejilla` (`ui/` 13 459 → 13 455, −4); el estimado era 13.5 |
| box_construccion.py | `BoxConstruccionMixin._construir_chips_offset` | C | 21 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| box_construccion.py | `BoxConstruccionMixin._construir_resumen` | C | 6 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| box_esquinas.py | `BoxEsquinasMixin._actualizar_iconos_esquinas` | C | 6 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cajon_task_cabecera.py | `PanelHeaderWidget.__init__` | C | 29 | 2 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cajon_task_construccion.py | `CajonTaskConstruccionMixin._crear_widget` | C | 20 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| chassis_construccion.py | `ChassisConstruccionMixin._init_ui` | C | 37 | 0 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| chassis_construccion.py | `ChassisConstruccionMixin._construir_barra_superior` | C | 36 | 2 | 6 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| chassis_construccion.py | `ChassisConstruccionMixin._construir_matriz_esquinas` | C | 18 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| chassis_construccion.py | `ChassisConstruccionMixin._construir_matriz_caras` | C | 45 | 0 | 5 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| chassis_construccion.py | `ChassisConstruccionMixin._construir_fondo` | A | 16 | 2 | 4 | 1 | 7.0 | fondo trasero (combo) + etiqueta |
| chassis_construccion.py | `ChassisConstruccionMixin._construir_selector_estrategias` | C | 25 | 0 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| chassis_construccion.py | `ChassisConstruccionMixin._crear_pagina_parametros` | A | 21 | 1 | 5 | 0 | 0.0 | ya generica: recibe filas (etiqueta, rango, valor) como datos; ahorro 0 |
| chassis_construccion.py | `ChassisConstruccionMixin._construir_pagina_suspendido` | A | 19 | 2 | 7 | 1 | 8.5 | despegue de piso; etiqueta de herrajes |
| chassis_estado.py | `ChassisEstadoMixin._actualizar_botones_esquinas` | C | 5 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_arbol_pintado.py | `ArbolPintadoMixin._pintar_filas_vanos` | C | 24 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_arbol_pintado.py | `ArbolPintadoMixin._crear_item_pieza` | C | 18 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_arbol_pintado.py | `ArbolPintadoMixin._crear_item_reengrose` | C | 13 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_construccion_widgets.py | `DivisionesEditor._construir_preview_y_modo` | C | 17 | 0 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_construccion_widgets.py | `DivisionesEditor._construir_arbol` | C | 22 | 0 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_construccion_widgets.py | `DivisionesEditor._construir_inspector_base` | B | 52 | 6 | 19 | 6 | 22.5 | tres pares casilla+spin (fijar ancho, alto, medida) y cabecera/etiquetas de estado |
| coco_construccion_widgets.py | `DivisionesEditor._construir_selector_contenido` | A | 15 | 2 | 5 | 1 | 6.5 | contenido del vano (combo) + etiqueta |
| coco_construccion_widgets.py | `DivisionesEditor._construir_panel_subdivision` | A | 20 | 2 | 8 | 2 | 8.5 | eje (combo), N partes (spin) |
| coco_construccion_widgets.py | `DivisionesEditor._construir_panel_puerta` | A | 32 | 5 | 15 | 4 | 13.5 | familia, montaje, apertura, herraje (combos) + etiqueta informativa |
| coco_construccion_widgets.py | `DivisionesEditor._construir_panel_cajon` | A | 28 | 4 | 13 | 3 | 12.0 | cantidad, corredera, apertura + etiqueta informativa |
| coco_construccion_widgets.py | `DivisionesEditor._construir_aviso_reengrose` | C | 8 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_construccion_widgets.py | `DivisionesEditor._construir_resumen` | C | 8 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_edicion_widgets.py | `EdicionDivisionesMixin._crear_item_celda` | C | 33 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_inspector_widgets.py | `PanelHeaderWidget.__init__` | C | 23 | 3 | 7 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_preview2d.py | `CocoPreview2D._dibujar_celdas` | C | 27 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_preview2d.py | `CocoPreview2D._dibujar_paneles` | C | 34 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_preview2d.py | `CocoPreview2D._dibujar_tiras` | C | 38 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_reengrose_widgets.py | `ReengroseDivisionesMixin._crear_grupo_reengrose` | C | 22 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_reengrose_widgets.py | `ReengroseDivisionesMixin._crear_combo_elemento` | A | 8 | 2 | 5 | 1 | 3.0 | elemento (combo) + etiqueta |
| coco_reengrose_widgets.py | `ReengroseDivisionesMixin._crear_combos_fabricacion` | A | 24 | 6 | 15 | 3 | 10.0 | fabricacion, choque, cara; mismo contenido que reengrose_ui_construccion._construir_fabricacion_choque_cara |
| coco_reengrose_widgets.py | `ReengroseDivisionesMixin._crear_controles_legacy` | A | 12 | 3 | 3 | 3 | 4.0 | combos legacy; no verificado si se llama |
| coco_reengrose_widgets.py | `ReengroseDivisionesMixin._spin_medida` | A | 6 | 1 | 2 | 1 | 2.0 | helper que crea un spin de rango 0-100000 |
| coco_reengrose_widgets.py | `ReengroseDivisionesMixin._fila_check_spin` | C | 7 | 0 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_widget` | C | 40 | 0 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_grupo_coloc` | B | 17 | 1 | 5 | 0 | 0.0 | ya migrado en D-74/D-75 (rotacion y anclaje); queda la etiqueta y botones +-90 fuera; ahorro 0 |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_boton_giro` | C | 11 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_grupo_exposicion` | C | 10 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_contenido_estructura` | C | 13 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_contenido_divisiones` | C | 5 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| coco_unified_construccion.py | `CocoUnifiedConstruccionMixin._crear_grupo_resumen` | C | 9 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cutting_list_menu.py | `_agregar_titulo` | C | 7 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cutting_list_menu.py | `_crear_opciones` | C | 19 | 0 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cutting_list_menu.py | `_agregar_info` | C | 12 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cutting_list_preview.py | `CuttingListPreviewPanel._crear_cabecera` | C | 11 | 2 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cutting_list_preview.py | `CuttingListPreviewPanel._crear_tabla` | C | 40 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| cutting_list_preview.py | `CuttingListPreviewPanel._crear_resumen` | C | 17 | 2 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `_crear_double_spin` | C | 12 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `_crear_spin` | C | 8 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `_crear_checkbox` | C | 4 | 1 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `_crear_combo` | C | 8 | 1 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `_crear_label` | C | 2 | 1 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `_crear_texto` | C | 2 | 1 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `FormField.crear_widget` | C | 11 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `FormBuilder.construir_grupo` | C | 15 | 1 | 5 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `FormBuilder.construir_suelto` | C | 5 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| form_builder.py | `FormBuilder.construir_celda` | C | 6 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| hardware_manager.py | `VDOHardwareManagerDialog._crear_selector_familia` | A | 12 | 2 | 4 | 1 | 5.0 | familia de herraje (combo) + etiqueta |
| hardware_manager.py | `VDOHardwareManagerDialog._crear_tabla_productos` | C | 19 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| hardware_manager.py | `VDOHardwareManagerDialog._crear_panel_detalle` | C | 22 | 1 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| hardware_manager.py | `VDOHardwareManagerDialog._crear_botones` | C | 13 | 0 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| hardware_manager.py | `VDOHardwareManagerDialog._mostrar_detalle` | C | 26 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| hardware_manager.py | `VDOHardwareManagerDialog._crear_editor` | A | 17 | 3 | 4 | 3 | 6.5 | editor dinamico segun tipo de valor (casilla, spin, texto); ahorro depende de tabla de tipos |
| inspector_cabecera.py | `_BreadcrumbBar.__init__` | C | 19 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_cabecera.py | `_BreadcrumbBar.set_ruta` | C | 24 | 2 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_cabecera.py | `_MicroHeaderWidget._crear_icono` | C | 4 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_cabecera.py | `_MicroHeaderWidget._crear_medidas` | A | 31 | 2 | 10 | 3 | 13.5 | W, H, D en fila con '×' intercalada; migrada en F-UI-2: ahorro real 23 líneas en inspector_cabecera.py y en el total (función 31 → 6; `inspector_cabecera.py` 200 → 177, `ui/` 13 475 → 13 452); árbol de widgets idéntico (snapshot sin cambios entre commits, `git diff 1561a5e -- tests/fixtures/inspector_cabecera_medidas_snapshot.json` vacío); `CABECERA_MEDIDES` en `datos/formularios.py`, `FormBuilder.construir_fila` con `ancho_fijo` 64 y `sin_etiqueta`; el estimado era 13.5 |
| inspector_cabecera.py | `_MicroHeaderWidget._crear_espesor` | A | 12 | 1 | 4 | 1 | 5.0 | espesor (spin, rango 3-100) + etiqueta |
| inspector_pagina_pieza.py | `PaginaPieza.__init__` | C | 44 | 8 | 12 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_pagina_pieza.py | `PaginaPieza.__init__._fila` | C | 7 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_pagina_vano.py | `PaginaVano._crear_banner_luz` | C | 13 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_pagina_vano.py | `PaginaVano._crear_dock_habitantes` | C | 31 | 1 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_pagina_vano.py | `PaginaVano._crear_stack_dock` | C | 13 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_pagina_vano.py | `PaginaVano._crear_panel_subdivision` | B | 34 | 6 | 15 | 3 | 15.0 | eje, partes, modo; boton Aplicar; migrada en F-UI-2e (D-117): árbol de widgets idéntico (snapshot sin cambios, `git diff 6ab3753 -- tests/fixtures/inspector_pagina_vano_subdivision_snapshot.json` vacío); ahorro real 17 líneas en `inspector_pagina_vano.py` (298 → 281) y 12 en `ui/` (13 472 → 13 460), función 34 → 15; el estimado era 15.0 |
| inspector_pagina_vano.py | `PaginaVano._crear_panel_insercion` | C | 25 | 2 | 7 | - | 0.0 | contenedor de presentacion: recibe widgets ya creados |
| inspector_pagina_vano.py | `PaginaVano._crear_panel_cajon` | A | 15 | 3 | 4 | 3 | 5.5 | cajones (spin), corredera, agarre (combos) |
| inspector_pagina_vano.py | `PaginaVano._crear_panel_puerta` | A | 14 | 3 | 3 | 3 | 5.0 | sistema, sentido, agarre (combos) |
| inspector_pagina_vano.py | `PaginaVano._crear_panel_vacio` | C | 13 | 1 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_paginas.py | `_PaginaBase.__init__` | C | 30 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_paginas.py | `_PaginaBase._add_dato` | C | 12 | 2 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_paginas.py | `PaginaChasis.__init__` | C | 17 | 5 | 6 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_paginas.py | `PaginaCierre.__init__` | C | 34 | 2 | 5 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| inspector_paginas.py | `PaginaCierre.__init__._fila_h` | C | 11 | 2 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| nesting_workflow.py | `NestingDialog._construir_modo` | C | 16 | 0 | 4 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| nesting_workflow.py | `NestingDialog._construir_tablero` | A | 38 | 8 | 17 | 4 | 16.5 | preset, ancho, alto, espaciado; migrada en F-UI-2a: ahorro real 23 líneas en ui/ y en el total (función 38 → 13); el estimado era 16.5 |
| nesting_workflow.py | `NestingDialog._construir_algoritmo` | A | 19 | 4 | 9 | 2 | 8.0 | algoritmo (combo), generaciones (spin); migrada en F-UI-2c: árbol de widgets idéntico (snapshot sin cambios, `git diff 0adddb0 -- tests/fixtures/nesting_algoritmo_snapshot.json` vacío); ahorro real 11 líneas en ui/ y en el total (función 19 → 8; `nesting_workflow.py` 306 → 295, `ui/` 13 455 → 13 444); el estimado era 8.0 |
| optimizer_dialog.py | `OptimizerDialog._build_ui` | C | 14 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| optimizer_dialog.py | `OptimizerDialog._construir_panel_config` | B | 55 | 10 | 25 | 5 | 24.5 | CSV, tablero, medidas, rotar; botones Examinar/Optimizar y etiquetas de estado fuera del formulario |
| optimizer_dialog.py | `OptimizerDialog._construir_bloque_corte` | A | 15 | 5 | 12 | 2 | 6.0 | kerf y margen (double) |
| optimizer_dialog.py | `OptimizerDialog._construir_panel_preview` | C | 9 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| optimizer_dialog.py | `OptimizerDialog._construir_barra` | C | 10 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| panel_task.py | `PanelTaskPanel._crear_widget` | C | 21 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| panel_task.py | `PanelTaskPanel._crear_grupo_reengrose` | C | 39 | 3 | 3 | - | 0.0 | delega en ReengroseBorderEditor y crea combos legacy sin layout; desclasificada en D-111, no se migra |
| puerta_task_cabecera.py | `PanelHeaderWidget.__init__` | C | 21 | 3 | 7 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| puerta_task_construccion.py | `PuertaTaskConstruccionMixin._crear_widget` | C | 21 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| qt.py | `crear_botonera_cancelar_aceptar` | C | 14 | 0 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| qt.py | `VDO_ExpressionInput.__init__` | C | 23 | 1 | 5 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._spin` | C | 7 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_activo_y_bordes` | B | 25 | 1 | 7 | 1 | 11.5 | casilla de activo; botones All y de borde (toggles) fuera del formulario |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_medidas` | A | 29 | 4 | 15 | 4 | 12.0 | uniforme (casilla), ancho, distancia, espesor en una fila horizontal con etiquetas inline |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_largo` | A | 13 | 2 | 5 | 1 | 5.5 | largo de tira (combo) + etiqueta |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_preview` | C | 18 | 1 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_sync_y_tabla` | A | 11 | 1 | 4 | 1 | 4.5 | casilla sincronizar esquinas con tooltip |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_fabricacion_choque_cara` | A | 29 | 6 | 15 | 3 | 12.5 | fabricacion, choque, cara |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_etiqueta_resumen` | C | 5 | 1 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_rejilla_esquinas` | A | 33 | 3 | 7 | 4 | 14.0 | cuatro combos de esquina en rejilla 2x2 con etiquetas |
| reengrose_ui_construccion.py | `ReengroseConstruccionMixin._construir_tabla_bordes` | A | 25 | 4 | 10 | 8 | 8.0 | matriz 4 bordes x (ancho, distancia): requiere tabla fila/columna, no soportada |
| task_base.py | `VDOTransactionMixin._crear_botonera_vdo` | C | 15 | 0 | 3 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| universal_inspector.py | `VDOUniversalInspectorWidget._construir_ui` | C | 13 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| universal_inspector.py | `VDOUniversalInspectorWidget._crear_cabecera` | C | 10 | 0 | 2 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| universal_inspector.py | `VDOUniversalInspectorWidget._crear_preview` | C | 11 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| universal_inspector.py | `VDOUniversalInspectorWidget._crear_arbol_maestro` | C | 10 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| universal_inspector.py | `VDOUniversalInspectorWidget._crear_stack` | C | 18 | 0 | 5 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |
| zocalo_task.py | `ZocaloTaskPanel._crear_widget` | C | 20 | 0 | 1 | - | 0.0 | presentacion, botones, etiquetas o widgets propios |

## Tipos de campo que faltan en FormBuilder

Soportados hoy: texto (`texto`), numérico (`double_spin`, `vdo_double_spin`, `spin`), combo (con `items` y `editable`), casilla (`checkbox`), etiqueta (`label`), expresión (`expresion`), rango, tooltip, sufijo, decimales, texto especial, estilo, ajuste de texto, `colspan` y `sin_etiqueta`. Filas: sí, una por campo en `construir_grupo`.

Faltan:
1. **Fila horizontal con varios campos y etiquetas intercaladas** (p. ej. `reengrose_ui_construccion._construir_medidas`, `inspector_cabecera._MicroHeaderWidget._crear_medidas` con «×»). `construir_grupo` solo hace una fila por campo.
2. **Tabla de campos filas × columnas** (p. ej. `_construir_tabla_bordes`, cuatro bordes por dos spins).
3. **Botón de acción dentro del formulario** (Examinar, Aplicar subdivisión, Optimizar). Ya señalado en D-74.
4. **Ancho fijo o máximo de widget** (`setFixedWidth`, `setMaximumWidth`), usado en medidas de cabecera y tabla de bordes.
5. **Campo de tipo dinámico** según el valor (`hardware_manager._crear_editor`). Requiere un despachador, no solo una tabla.
6. **Conexión de señales en la especificación** (`valueChanged`, `currentTextChanged`). Hoy cada panel conecta a mano; sin esto el ahorro real es menor que el estimado.
7. **Botón de opción (`QRadioButton`)**, no soportado. Solo aparece en C (`nesting_workflow._construir_modo`, `cutting_list_menu._crear_opciones`).
8. **Texto de sugerencia (`setPlaceholderText`)** en campos de texto. Hoy está fijo dentro de `VDO_ExpressionInput`.

## Orden de migración recomendado (mayor a menor ahorro neto)

| # | Función | Clase | Ahorro neto estimado | Requiere nuevo tipo |
|---:|---|:---:|---:|---|
| 1 | `optimizer_dialog.py::OptimizerDialog._construir_panel_config` | B | 24.5 | botón de acción |
| 2 | `coco_construccion_widgets.py::DivisionesEditor._construir_inspector_base` | B | 22.5 | señales; fila cabecera |
| 3 | `panel_task.py::PanelTaskPanel._crear_grupo_reengrose` | C | 0.0 | desclasificada (D-111); no se migra |
| 4 | `nesting_workflow.py::NestingDialog._construir_tablero` | A | 23.0 (real) | migrada (F-UI-2a, D-111); sin tipo nuevo |
| 5 | `inspector_pagina_vano.py::PaginaVano._crear_panel_subdivision` | B | 15.0 | migrada en F-UI-2e (D-117); árbol de widgets idéntico (snapshot sin cambios); ahorro real 12 líneas en `ui/` y 17 en `inspector_pagina_vano.py`, función 34 → 15; el estimado era 15.0 |
| 6 | `box_construccion.py::BoxConstruccionMixin._construir_esquinas` | C | 0.0 | desclasificada en D-118; no es formulario, no se migra |
| 7 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_rejilla_esquinas` | A | 14.0 | ninguno |
| 8 | `box_construccion.py::BoxConstruccionMixin._construir_panel_medidas` | A | 13.5 | ninguno |
| 9 | `coco_construccion_widgets.py::DivisionesEditor._construir_panel_puerta` | A | 13.5 | ninguno |
| 10 | `inspector_cabecera.py::_MicroHeaderWidget._crear_medidas` | A | 13.5 | fila horizontal; ancho fijo |
| 11 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_fabricacion_choque_cara` | A | 12.5 | ninguno |
| 12 | `coco_construccion_widgets.py::DivisionesEditor._construir_panel_cajon` | A | 12.0 | ninguno |
| 13 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_medidas` | A | 12.0 | fila horizontal |
| 14 | `box_construccion.py::BoxConstruccionMixin._construir_barra_superior` | B | 11.5 | botón de acción |
| 15 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_activo_y_bordes` | B | 11.5 | botones de acción |
| 16 | `coco_reengrose_widgets.py::ReengroseDivisionesMixin._crear_combos_fabricacion` | A | 10.0 | ninguno |
| 17 | `chassis_construccion.py::ChassisConstruccionMixin._construir_pagina_suspendido` | A | 8.5 | ninguno |
| 18 | `coco_construccion_widgets.py::DivisionesEditor._construir_panel_subdivision` | A | 8.5 | ninguno |
| 19 | `nesting_workflow.py::NestingDialog._construir_algoritmo` | A | 8.0 | ninguno (migrada en F-UI-2c; árbol idéntico, real −11 líneas) |
| 20 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_tabla_bordes` | A | 8.0 | tabla filas×columnas |
| 21 | `chassis_construccion.py::ChassisConstruccionMixin._construir_fondo` | A | 7.0 | ninguno |
| 22 | `coco_construccion_widgets.py::DivisionesEditor._construir_selector_contenido` | A | 6.5 | ninguno |
| 23 | `hardware_manager.py::VDOHardwareManagerDialog._crear_editor` | A | 6.5 | campo de tipo dinámico |
| 24 | `optimizer_dialog.py::OptimizerDialog._construir_bloque_corte` | A | 6.0 | ninguno |
| 25 | `inspector_pagina_vano.py::PaginaVano._crear_panel_cajon` | A | 5.5 | ninguno |
| 26 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_largo` | A | 5.5 | ninguno |
| 27 | `hardware_manager.py::VDOHardwareManagerDialog._crear_selector_familia` | A | 5.0 | ninguno |
| 28 | `inspector_cabecera.py::_MicroHeaderWidget._crear_espesor` | A | 5.0 | ninguno |
| 29 | `inspector_pagina_vano.py::PaginaVano._crear_panel_puerta` | A | 5.0 | ninguno |
| 30 | `reengrose_ui_construccion.py::ReengroseConstruccionMixin._construir_sync_y_tabla` | A | 4.5 | ninguno |
| 31 | `coco_reengrose_widgets.py::ReengroseDivisionesMixin._crear_controles_legacy` | A | 4.0 | ninguno |
| 32 | `coco_reengrose_widgets.py::ReengroseDivisionesMixin._crear_combo_elemento` | A | 3.0 | ninguno |
| 33 | `coco_reengrose_widgets.py::ReengroseDivisionesMixin._spin_medida` | A | 2.0 | ninguno |

Recomendación: empezar por las A que no requieren tipo nuevo (combos y spins en rejilla; la columna «Requiere nuevo tipo» indica las demás), porque su ahorro se obtiene solo con datos. Después, añadir a FormBuilder la fila horizontal y el botón de acción, y migrar las B y las medidas en fila. La tabla de bordes y el editor dinámico dejarlos al final, ya que requieren los tipos más costosos.

## Limitaciones

- La clasificación es juicio sobre lectura de código, no regla automática. Las funciones C se clasificaron por sus líneas con llamadas a widgets (etiquetas, botones, canvas, árboles), no línea a línea.
- `_crear_pagina_parametros` recibe sus filas de fuera, así que su conteo de campos no está fijado en la función; se le asignó ahorro 0. `_crear_editor` depende del tipo de valor, y su conteo (3) es una referencia.
- Los combos de fabricación, choque y cara están duplicados en `reengrose_ui_construccion.py` y `coco_reengrose_widgets.py`. El ahorro se cuenta en ambas funciones, así que el total queda algo sobrestimado en esa parte.
- No se ejecutaron pruebas ni verificación visual: la medición es estática.
- **Corrección por lectura real (F-UI-2a, D-111):** `panel_task.py::PanelTaskPanel._crear_grupo_reengrose` estaba clasificada como A por sus llamadas, pero delega en `ReengroseBorderEditor` y sus tres combos son legacy, sin layout. Pasa a C con ahorro 0 y no se migra. En `nesting_workflow.py::NestingDialog._construir_tablero` el ahorro real medido fue de 23 líneas de `ui/` (13 562 → 13 539) y del total (24 470 → 24 447), frente a las 16.5 estimadas; la función pasó de 38 a 13 líneas.
- **Corrección por lectura real (F-UI-2, D-118):** `box_construccion.py::BoxConstruccionMixin._construir_esquinas` estaba clasificada como B por sus llamadas a widgets, pero crea 4 botones cuadrados con icono (`QPushButton`, `setFixedSize`, `setIconSize`, cursor) en un bucle sobre un `QGridLayout` más 4 `QComboBox` ocultos (`setVisible(False)`) de retrocompatibilidad: no crea pares etiqueta+campo ni layout de formulario. Pasa a C con ahorro 0 y no se migra.
