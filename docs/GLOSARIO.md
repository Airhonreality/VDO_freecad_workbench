# Glosario VDO

Términos de dominio VDO y su correspondencia con el código.

| Término | Código | Descripción |
|---------|--------|-------------|
| Módulo | `freecad.vdo.core` | Pieza paramétrica VDO (panel, cajón, puerta, zócalo, COCO) |
| Core | `freecad/vdo/core/` | Dominio puro: cálculos sin FreeCAD ni Qt |
| CAD | `freecad/vdo/cad/` | Adaptador FreeCAD: Part.Shape, App.Vector |
| App | `freecad/vdo/app/` | Casos de uso y composición |
| UI | `freecad/vdo/ui/` | Interfaz Qt/PySide |
| Puerto | `app/puertos.py` | Protocolo `Documento` para abstraer FreeCAD |
| Caso de uso | `app/casos_uso/` | Una operación de usuario (crear zócalo, crear puerta, etc.) |
| Plan | `dataclass` inmutable | Salida de un módulo de core; se aplica al documento vía cad/ |
| Golden master | `tests/golden/*.json` | Captura de salida de dominio para detección de regresiones |
| Manifiesto | `core/vdo_manifest.json` | Fuente única de datos de materiales, herrajes, procesos |
| Catálogo de herrajes | `core/vdo_hardware_catalog.json` | SKUs de herrajes (bisagras, correderas, etc.) |
| Sistema de apertura | `core/vdo_facade_contract.py` | tirador, gola_aluminio, inglete_45, push_open |
| Montaje | `core/vdo_facade_contract.py` | parche, semiparche, embebida |
| Reengrose | `core/vdo_reengrose.py` | Refuerzos perimetrales en paneles |
| COCO | `core/vdo_coco_core.py` | Contenedor Cohesivo: mueble con divisiones internas |
| Task Panel | `ui/vdo_*_task.py` | Panel de configuración de un módulo VDO |
| ViewProvider | `ui/vdo_view_providers.py` | Proxy de FreeCAD para objetos VDO en la vista 3D |

## Términos de usuario

Estos términos aparecen en la UI pero no son identificadores de código:

| Término de usuario | Descripción |
|-------------------|-------------|
| Zócalo | Pieza de base del mueble |
| Corredera oculta | Guía de cajón invisible |
| Bisagra de cazoleta | Bisagra de 35mm para puertas |
| Gola | Perfil de aluminio en el canto superior |
| Inglete 45° | Corte a 45° para agarre de puerta |
| Push open | Apertura por presión (empujar para abrir) |
