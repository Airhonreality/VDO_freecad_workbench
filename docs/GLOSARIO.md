# Glosario VDO

Términos del dominio que aparecen en el código y en la interfaz. Cada definición sale del código o de sus docstrings. Cuando no hay base suficiente, la columna de estado dice **por confirmar**. Las rutas son relativas a `freecad/vdo/`.

Estado de la fuente: `docs/ARQUITECTURA.md` (capas) y `docs/PLAN_MINIMALISMO_VDO.md` (plan).

## Objetos del workbench

| Término | Definición | Dónde | Estado |
|---|---|---|---|
| Módulo | Pieza paramétrica VDO. Cada tipo (panel, cajón, puerta, zócalo, COCO) es un `FeaturePython`. | `cad/*.py` | confirmado |
| Panel | Tablero VDO (`PanelFeature`), con expresiones de `Params` según la orientación. | `cad/panel.py`, `core/panel_core.py` | confirmado |
| Zócalo | Pieza de base del mueble. Su cálculo produce tiras, amarres y despiece. | `cad/zocalo.py`, `core/zocalo_core.py` | confirmado |
| Cajón | Caja con corredera (`CajonFeature`). Corredera oculta, telescópica o metálica. | `cad/cajon.py`, `core/cajon_calculo.py` | confirmado |
| Puerta | Frente batiente, basculante o corredera (`PuertaFeature`). Familias en `datos/formularios.py`. | `cad/puerta.py`, `core/puerta_despiece.py` | confirmado |
| COCO | Cofre con divisiones internas (`CocoFeature`, "cofre COCO"). El significado de la sigla no está en el código. | `cad/coco.py`, `core/coco_core.py` | sigla por confirmar |
| Guardián | Escritura del entorno de parámetros en el documento: hoja de cálculo `Params` que leen las piezas. | `cad/guardian.py` | confirmado |
| Trinidad v2 | Nombre de versión que aparece en los docstrings de `make_cajon` y `CajonFeature`. Qué incluye exactamente, por confirmar. | `cad/cajon.py` | por confirmar |
| L1 | Nivel del motor de reengrose del panel ("panel L1"). Significado exacto por confirmar. | `cad/panel.py` (`add_reengrose_props`) | por confirmar |

## Geometría y cálculo

| Término | Definición | Dónde | Estado |
|---|---|---|---|
| Reengrose | Motor de bordes del panel: refuerzos de canto, encuentros entre piezas y despiece con cantos. Su tipo central es `ReengroseDTO`, con `BordeConfig`. | `core/reengrose_*.py` | confirmado (definición); origen del nombre por confirmar |
| Tiras | Franjas 2D de material. Las tiras perimetrales son la primitiva del reengrose; `resolver_tiras` aplica interrupciones y prioridades a las tiras de COCO. | `core/reengrose_tiras.py`, `core/coco_spaces.py` | confirmado |
| Espacios | Árbol de espacios libres dentro de un módulo. Nodo: `SpaceNode`; se serializa a JSON para una propiedad del documento. | `core/spaces.py`, `core/spaces_resumen.py` | confirmado |
| Vano | Hueco libre donde va una pieza, con su medida. COCO planifica una "matriz de vanos" sobre sus espacios. | `core/coco_spaces.py` (`planificar_divisiones_matriz`) | confirmado |
| Aperturas | Sistemas de apertura de frentes (tirador, gola, inglete 45, push open). Una sola tabla desde M3 (MN-06). | `core/aperturas.py`, `cad/cajon.py` (`SistemaApertura`) | confirmado |
| Montaje | Cómo se fija el frente al vano: `parche`, `semiparche` o `embebida`. | `core/facade_contract.py` (`MONTAJE_*`) | confirmado |
| Despiece | Lista de piezas físicas que sale de un cálculo, con sus cortes. Lo producen `cajon_calculo`, `puerta_despiece` y `reengrose_despiece`. | `core/*_despiece.py`, `core/cajon_calculo.py` | confirmado |
| Cantos | Bordes de la pieza que llevan acabado visible. La política de cantos está en `core/finish.py`. | `core/finish.py` | confirmado |
| Frame / marco | Marco local único del módulo y vocabulario de lados (`norte`, `sur`, `este`, `oeste` en las tablas). | `core/frames.py` | confirmado |
| Plan | Dataclass inmutable que devuelve un cálculo de `core/`; `cad/` lo escribe en el documento. | `core/dto.py`, `cad/*.py` | confirmado |
| Nesting | Colocación automática de piezas sobre el tablero. | `core/nesting.py`, `core/nesting_presets.py` | confirmado |
| Lista de corte | Piezas agrupadas para el optimizador de corte. | `core/optimizer_lista_corte.py`, `core/optimizar_corte.py` | confirmado |
| Catálogo de herrajes | Datos de bisagras, correderas y demás herrajes. Único origen: `core/vdo_hardware_catalog.json`. Consulta con `core/hardware_hub.py`. | `core/hardware_hub.py` | confirmado |
| Anclaje | Tipo de fijación de la pieza. Su tabla está en `datos/anclajes.json`. | `datos/anclajes.json`, `core/module_props.py` | confirmado |

## Interfaz y workbench

| Término | Definición | Dónde | Estado |
|---|---|---|---|
| Task panel | Panel de configuración de un módulo al editarlo. Un archivo por tipo (`*_task.py`). | `ui/*_task.py`, `ui/task_base.py` | confirmado |
| ViewProvider | Proxy de FreeCAD que muestra un objeto VDO en la vista 3D. | `ui/view_providers.py` | confirmado |
| Inspector | Árbol y páginas de propiedades del documento. | `ui/universal_inspector.py`, `ui/inspector_*.py` | confirmado |
| Especificación de formulario | Tabla de campos (etiqueta, tipo, rango, valor por defecto) que `FormBuilder` convierte en widgets. | `datos/formularios.py`, `ui/form_builder.py` | confirmado |
| Tema | Tabla única de estilos y colores de `ui/` (MN-07). Las excepciones están en `docs/ARQUITECTURA.md` §4. | `ui/tema.py` | confirmado |
| Accept | Función que lee los valores de un panel y los escribe en el módulo. | `ui/*_task.py` | confirmado |

## Verificación

| Término | Definición | Dónde | Estado |
|---|---|---|---|
| Golden | Captura de salida de `core/` o de un flujo de creación, comparada en cada prueba. Los de origen están en `tests/golden/`. | `tests/golden/*.json`, `docs/metricas/goldens_origen.md` | confirmado |
| Nivel 1 / 2 / 3 | Nivel 1: pruebas sin FreeCAD. Nivel 2: pruebas con `freecadcmd`. Nivel 3: verificación visual en la GUI, por una persona. | `tools/run_tests.py` | confirmado |
| Meta medida | Cifra que una fase debe cumplir para cerrarse, medida con `tools/auditoria/minimalismo.py`. | `docs/PLAN_MINIMALISMO_VDO.md` §5 y §6 | confirmado |
