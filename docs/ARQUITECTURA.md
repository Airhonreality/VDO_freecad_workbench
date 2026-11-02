# Arquitectura VDO — Workbench de muebles paramétricos

## Visión general

VDO es un workbench de FreeCAD para diseño de muebles paramétricos (cajones, puertas, paneles, zócalos, COCO). El código sigue una arquitectura en capas con estricta separación de responsabilidades.

## Capas

El paquete `freecad/vdo/` se divide en cinco capas con dependencias unidireccionales:

```
ui/  →  app/  →  cad/  →  core/
```

- **`core/`**: Dominio puro. Solo importa biblioteca estándar y otros módulos de `core/`. No importa FreeCAD, Qt, ni UI. Cálculos con números y tuplas inmutables.
- **`cad/`**: Adaptador FreeCAD. Único lugar con `import FreeCAD`, `import Part`. Convierte planos de dominio a `App.Vector`/`Part.Shape`.
- **`app/`**: Casos de uso y composición. Orquesta `core/` y `cad/`. Recibe el manifiesto y catálogo inyectados.
- **`ui/`**: Qt (PySide). Solo habla con `app/` (vía `app/vdo_api.py`) y `qt_compat`.
- **Entrada**: `Init.py`, `InitGui.py`, `commands.py`. Punto de entrada de FreeCAD.

### Dependencias permitidas

| Desde | Puede importar |
|-------|---------------|
| `ui/` | `app/`, `qt_compat` |
| `app/` | `core/`, `cad/` |
| `cad/` | `core/` |
| `core/` | solo stdlib y `core/` |

Ninguna otra dependencia está permitida.

## Puerto: Documento

`app/puertos.py` define el protocolo `Documento` (crear/leer/escribir objetos, transacción, recompute). `cad/` lo implementa. Los tests usan una implementación en memoria.

## Flujo de un comando (ejemplo: crear zócalo)

1. Usuario activa un comando en `commands.py`.
2. `commands.py` construye el contexto (`app/composicion.py`) y llama al caso de uso (`app/casos_uso/`).
3. El caso de uso recibe `Parametros` (dataclass) y `Documento` (puerto), llama a `core/` para calcular, y a `cad/` para escribir en el documento.
4. `ui/` muestra paneles y diálogos, pero solo recibe datos de `app/`.

## Niveles de prueba

| Nivel | Qué prueba | Requiere | Comando |
|-------|-----------|----------|---------|
| 1 — pura | `core/`, `app/`, golden de cálculo, arquitectura, docs | Python 3 | `VDO_TEST_DIR=tests VDO_TEST_OUT=out.txt python3 tools/run_tests.py` |
| 2 — FreeCAD | `cad/`, golden de geometría, integración | `freecadcmd` | `VDO_TEST_DIR=tests VDO_TEST_OUT=out.txt freecadcmd tools/run_tests.py` |
| 3 — GUI | Paneles, comandos, inspector, capturas | FreeCAD GUI con display | FreeCAD GUI |

## Cómo ejecutar la verificación

```bash
# Métricas de la rúbrica (código ≠ 0 si falla)
python3 -I tools/auditoria/verificar.py

# Lint
.venv/bin/ruff check freecad/ tests/ tools/

# Tipado
.venv/bin/mypy --strict freecad/vdo/core freecad/vdo/app freecad/vdo/cad

# Golden masters
python3 -I tools/auditoria/golden.py --verificar
```

## Decisiones de arquitectura (ADR)

Véase `docs/adr/ADR-000-indice.md` para el listado completo de M-01…M-24.
