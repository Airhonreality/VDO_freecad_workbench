# Changelog VDO

## [2.0.0] — Pendiente de aprobación (M-23)

### Cambios en la API interna
- Eliminación de `core/vdo_ui_registry.py`: core ya no conoce vistas (M-07).
- Nueva capa `cad/` con `geometria.py`, `propiedades.py`, `vdo_guardian.py`.
- Nueva capa `app/` con `puertos.py`, `composicion.py`, `registro.py`, `casos_uso/`, `vdo_api.py`.
- Nuevo módulo `core/errores.py` con jerarquía tipada: `VDOError`, `ParametroInvalido`, `ReglaDeDominio`, `CatalogoError`, `GeometriaError`.
- Nuevo módulo `core/vdo_helpers.py` con importadores perezosos `_get_app` / `_get_part`.
- Eliminación de estado mutable de módulo: `_MANIFEST`, `_CATALOGO`, `VDO_MANIFEST` eliminados.

### Cambios de comportamiento
- Cero `except … pass` en todo el paquete.
- Cero `except Exception` en `core/`, `cad/`, `app/`.
- Los tests de nivel 1 no instalan mocks en `sys.modules` (M-18).
- El acento de tema se unifica en `#007acc` (M-12).

### Cambios externos
- `tools/vdo_erp_sync/` movido a `tools/erp_sync/`, excluido del ZIP.
- `tools/matriz_mapeo.py` eliminado.
- `package.xml`: versión 2.0.0.

## [1.0.0] — Versión previa

Versión inicial del workbench VDO.
