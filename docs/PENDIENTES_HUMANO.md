# Pendientes humanos — plan de minimalismo

**Actualizado: 2026-11-06 (cierre de M11).** Lo que el usuario debe decidir o revisar, por orden de urgencia. Después, el historial de la sesión anterior con su estado comprobado.

Ninguna decisión de esta lista está tomada. El merge de la rama no se ha hecho.

---

## Decisiones y revisiones para el usuario

### 1. Objetivo de líneas: +6,6 % frente a −30 %

- **Hecho:** 23.608 líneas en la base (`docs/metricas/minimalismo_base.json`) y 25.171 en el final (`docs/metricas/minimalismo_final.json`): **+6,6 %**. La meta del plan era −30 %. Detalle en `docs/DEUDA_TECNICA.md`, A1.
- **Opciones:**
  1. Aceptar el resultado y documentarlo como tal.
  2. Abrir una fase de reducción con alcance concreto.
- **Recomendación del ejecutor:** opción 1 para cerrar M11, y una fase aparte si quieres reducción. La división por conceptos (P5) añadió archivos: la base tenía 85 (incluido `app/`) y el final 145 en `core`, `ui` y `cad`. Ese aumento de archivos acompaña al aumento de líneas. Una reducción real exigiría cambios de comportamiento que hoy no tienen golden.
- **Bloquea:** el cierre formal de la meta de §1 del plan.

### 2. `dist/VDO-1.1.0.zip` sobrescrito

- **Hecho:** el zip de 2 de noviembre se sustituyó el día de M10. Hoy `dist/` no tiene zip. El build de M10 está en `/tmp/ola79_build/VDO-1.1.0.zip`, fuera del repo.
- **Opciones:** regenerar con `tools/build_zip.py` en `dist/`, o no conservar el zip en el repo.
- **Bloquea:** la entrega del zip.

### 3. Revisión visual en FreeCAD

- **Qué revisar:** paneles de M6 y M7 (zócalo, panel, puerta, cajón y coco), y el icono de M4. Son los cambios sin verificación gráfica (D-70 a D-75, D-40).
- **Por qué:** el nivel 3 de M10 no está automatizado y ninguna persona lo ha hecho.
- **Bloquea:** el cierre de M10 y de M6 y M7 en el sentido del plan §9.

### 4. Revisar los 168 `noqa`

- **Hecho:** 168 códigos medidos: E402 (108), RUF001 (47), C901 (13). El encargo decía 166 (E402 106). Ver `docs/DEUDA_TECNICA.md`, C1.
- **Qué decidir:** si cada `noqa` tiene motivo aceptable. Los RUF001 cambian texto visible si se corrigen, así que no se tocan sin revisión.

### 5. Fase de depuración

- **Qué decidir:** si empieza con la lista de `docs/DEUDA_TECNICA.md` (sección B: defectos a depurar), y en qué orden. Hay defectos de comportamiento (B1 a B5), incluido el `TipoMontaje` del cajón (B1), que se verificó por lectura y no en ejecución.
- **Recomendación del ejecutor:** empezar por B1 y B2, que afectan a datos guardados por el usuario, y después B4 con su golden.

### 6. Merge de `minimalismo/noche-20261102`

- **Hecho:** la rama contiene los commits de M0 a M11. No hay push, merge, tag ni cambio en `main`.
- **Qué decidir:** si se mergea, y cuándo. Conviene decidirlo después de los puntos 1 y 3.

### 7 (nuevo). Planes y ADR anteriores que siguen en `docs/`

- **Hecho:** MN-13 pedía archivar los planes anteriores. Se archivaron `PLAN_MAESTRO_VDO.md` y `PLAN_CORRECCIONES_F19.md`. **Siguen en `docs/`:** `PLAN_REFACTOR_VDO.md`, `PROGRESO_REFACTOR.md`, `PROGRESO_VDO.md`, `PROGRESO_VDO.yaml`, `REVISION_ARQUITECTURA_CAPAS.md`, `CONTEXTO_TECNICO_VDO.md`, `INVENTARIO_APP_M5.md`, `MANIFIESTO_DISENO_INTERFAZ_VDO.md` y los ADR `ADR-000`, `ADR-001`, `ADR-004` y `ADR-005`.
- **Qué decidir:** si se archivan también (MN-13 lo pide para los planes), y si los ADR anteriores se archivan o se borran. MN-11 los descarta.

---

## Historial de la sesión anterior (estado comprobado en M11)

| Entrada | Estado | Nota |
|---|---|---|
| P-01 (¿N/A `guardian` y `nesting_presets`?) | **Resuelto** en parte | `guardian` tiene golden de 9 entradas. `nesting_presets` pasa a P-10. |
| P-02 (serializador de `rotacion_z`) | **Resuelto** | Golden de 3 entradas desde `b78de04`. |
| P-03 (flujos de creación sin módulo propio) | **Decidido** por el ejecutor | Cubiertos por `creacion_modulos.json`. |
| P-04 (tests de otra sesión con `os._exit`) | **Por confirmar** | `os._exit` ya no aparece en el código: hay `sys.exit` en su lugar. Falta confirmar si quedó commiteado o descartado. Ver `docs/DEUDA_TECNICA.md`, J2. |
| P-05 (aprobar goldens sustituidos) | **Pendiente de aprobación humana** | `creacion_modulos.json`, `coco_spaces.json` y `puerta_despiece.json` cambian de esquema o de error a valor. Ver `docs/metricas/goldens_origen.md`. El código actual los reproduce según el registro. |
| P-06 (dónde vive `rotacion_z`) | **Pendiente** | Siguen dos definiciones: `core/helpers.py` y `cad/propiedades.py`. Ver `docs/DEUDA_TECNICA.md`, B7. |
| P-07 (¿`ESQUINAS` y `TIPOS_ENCUENTRO` son el mismo concepto?) | **Por confirmar** | Ya no aparecen como tabla idéntica en la medición final. No consta qué se decidió sobre su significado. |
| P-08 (ciclo `core` ↔ `cad`) | **Resuelto** | `ARISTAS core->cad: 0` en el estado actual. |
| P-09 (sin definir) | **Sin definir** | El encargo de otra sesión cita P-09 y ningún documento lo define. Hace falta definirlo o retirarlo del encargo. |
| P-10 (golden de `nesting_presets`) | **Pendiente** | No carga en `b78de04`. No hay `tests/golden/nesting_presets.json`. Ver `docs/DEUDA_TECNICA.md`, B4. |

El texto original de cada entrada está en el historial de git de este archivo (commits anteriores a M11).
