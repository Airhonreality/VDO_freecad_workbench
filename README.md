# VDO — Muebles paramétricos para FreeCAD

Workbench de FreeCAD para diseñar muebles paramétricos (paneles, cajones, puertas,
zócalos y lista de corte).

## Requisitos

- FreeCAD 1.1 o superior (con interfaz gráfica para usar los paneles).

## Instalación

1. Descomprime el archivo `VDO-<versión>.zip`. Obtendrás una carpeta llamada `VDO`.
2. Copia la carpeta `VDO` dentro de la carpeta de módulos (`Mod`) de FreeCAD:
   - Linux (nativo): `~/.local/share/FreeCAD/Mod/`
   - Linux (Flatpak): `~/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/Mod/`
   - Windows: `%APPDATA%\FreeCAD\Mod\`
   - macOS: `~/Library/Preferences/FreeCAD/Mod/`
3. Reinicia FreeCAD y selecciona el workbench **VDO** en el selector de workbenches.

## Uso

- **Crear hoja**: crea `Params_Melamina` y `Params` (parámetros globales).
- **Creación**: paneles estándar y de fachada, división, zócalo, COCO 4C, puerta y cajón.
  Cada módulo se crea oculto, abre su panel de configuración y se coloca con un clic.
- **Herramientas**: Inspector Universal lateral, propiedades del módulo seleccionado,
  lista de corte (CSV), optimizador de corte, nesting (requiere el addon Nesting
  Workbench) y catálogo de herrajes.

## Soporte

Uso privado. Contacta con el titular para cualquier incidencia.
