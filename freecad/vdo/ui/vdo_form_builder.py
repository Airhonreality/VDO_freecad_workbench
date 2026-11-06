# =====================================================================
# vdo_form_builder.py
# Constructor declarativo de formularios para los Task Panels VDO (D-15).
#
# Un formulario se define como una lista de campos (especificacion
# declarativa). El builder crea los widgets Qt correspondientes y expone
# metodos para leer/escribir valores por clave. El panel conserva la
# propiedad de las senales (valueChanged, toggled, etc.) y de la logica
# de negocio; el builder solo construye la UI de los campos.
#
# Campo:
#   {
#     "tipo": "double_spin" | "spin" | "checkbox" | "combo" | "label",
#     "etiqueta": str,           # etiqueta mostrada
#     "clave": str,              # clave para leer/escribir el valor
#     "valor_defecto": any,      # valor por defecto
#     "rango": (min, max) | None,# rango para spinners
#     "decimales": int | None,   # decimales (double_spin)
#     "sufijo": str | None,      # sufijo mostrado (p. ej. " mm")
#     "unidades": str | None,    # unidades (informativo)
#     "tooltip": str | None,
#     "items": [(label, data), ...] | None,  # para combo
#     "dependencias": [(clave, callable), ...],  # callbacks de dependencia
#     "estilo": str | None,      # clave de estilo (dict "estilos" del builder)
#     "ajustar_texto": bool,     # setWordWrap (labels)
#     "sin_etiqueta": bool,      # celda sin etiqueta propia
#     "colspan": int,            # columnas que ocupa el widget
#     "editable": bool,          # combo editable (combo)
#     "texto_especial": str|None,# texto del valor minimo (double_spin)
#   }
# =====================================================================

from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui.vdo_qt import VDO_DoubleSpinBox, VDO_ExpressionInput

# tipos cuyo widget es numerico (value(), interpretText())
_TIPOS_NUMERICOS = ("double_spin", "vdo_double_spin", "spin")


def _asignar_numero(widget, valor):
    widget.setValue(valor)


def _asignar_check(widget, valor):
    widget.setChecked(bool(valor))


def _asignar_combo(widget, valor):
    idx = widget.findData(valor)
    if idx >= 0:
        widget.setCurrentIndex(idx)


def _asignar_texto(widget, valor):
    widget.setText(str(valor))


# tipo de campo -> funcion que escribe el valor en el widget
_ASIGNADORES_VALOR = {
    "double_spin": _asignar_numero,
    "spin": _asignar_numero,
    "checkbox": _asignar_check,
    "combo": _asignar_combo,
    "label": _asignar_texto,
    "texto": _asignar_texto,
    "expresion": _asignar_texto,
    "vdo_double_spin": _asignar_numero,
}


def _crear_double_spin(campo, parent, clase=None):
    w = (clase or QtWidgets.QDoubleSpinBox)(parent)
    if campo.rango:
        w.setRange(*campo.rango)
    if campo.decimales is not None:
        w.setDecimals(campo.decimales)
    if campo.sufijo:
        w.setSuffix(campo.sufijo)
    if campo.texto_especial:
        w.setSpecialValueText(campo.texto_especial)
    w.setValue(float(campo.valor_defecto or 0.0))
    return w


def _crear_spin(campo, parent):
    w = QtWidgets.QSpinBox(parent)
    if campo.rango:
        w.setRange(*campo.rango)
    w.setValue(int(campo.valor_defecto or 0))
    if campo.sufijo:
        w.setSuffix(campo.sufijo)
    return w


def _crear_checkbox(campo, parent):
    w = QtWidgets.QCheckBox(campo.etiqueta or "", parent)
    w.setChecked(bool(campo.valor_defecto or False))
    return w


def _crear_combo(campo, parent):
    w = QtWidgets.QComboBox(parent)
    if campo.editable:
        w.setEditable(True)
    for label, data in (campo.items or []):
        w.addItem(label, data)
    w.setCurrentIndex(0)
    return w


def _crear_label(campo, parent):
    return QtWidgets.QLabel(str(campo.valor_defecto or ""), parent)


def _crear_texto(campo, parent):
    return QtWidgets.QLineEdit(parent)


def _crear_expresion(campo, parent):
    return VDO_ExpressionInput(parent, numeric_only=False)


def _crear_vdo_double_spin(campo, parent):
    return _crear_double_spin(campo, parent, VDO_DoubleSpinBox)


# tipo de campo -> funcion que crea el widget Qt (campo, parent)
_CONSTRUCTORES_WIDGET = {
    "double_spin": _crear_double_spin,
    "vdo_double_spin": _crear_vdo_double_spin,
    "spin": _crear_spin,
    "checkbox": _crear_checkbox,
    "combo": _crear_combo,
    "label": _crear_label,
    "texto": _crear_texto,
    "expresion": _crear_expresion,
}


class FormField:
    """Un campo de formulario con su widget y metadatos."""

    def __init__(self, espec):
        self.tipo = espec["tipo"]
        self.etiqueta = espec.get("etiqueta", "")
        self.clave = espec["clave"]
        self.valor_defecto = espec.get("valor_defecto")
        self.rango = espec.get("rango")
        self.decimales = espec.get("decimales")
        self.sufijo = espec.get("sufijo")
        self.tooltip = espec.get("tooltip")
        self.items = espec.get("items")
        self.editable = espec.get("editable", False)
        self.texto_especial = espec.get("texto_especial")
        self.widget = None

    def crear_widget(self, parent=None):
        """Crea el widget Qt del campo segun su tipo."""
        constructor = _CONSTRUCTORES_WIDGET.get(self.tipo)
        if constructor is None:
            raise ValueError(f"Tipo de campo no soportado: {self.tipo!r}")
        w = constructor(self, parent)

        if self.tooltip:
            w.setToolTip(self.tooltip)
        self.widget = w
        return w

    # -----------------------------------------------------------------
    # Lectura / escritura de valor
    # -----------------------------------------------------------------
    def valor(self):
        if self.widget is None:
            return self.valor_defecto
        if self.tipo in _TIPOS_NUMERICOS:
            return self.widget.value()
        if self.tipo == "checkbox":
            return self.widget.isChecked()
        if self.tipo == "combo":
            return self.widget.currentData()
        if self.tipo in ("label", "texto"):
            return self.widget.text()
        if self.tipo == "expresion":
            return self.widget.value()
        return self.valor_defecto

    def set_valor(self, valor):
        if self.widget is None:
            return
        asignar = _ASIGNADORES_VALOR.get(self.tipo)
        if asignar is not None:
            asignar(self.widget, valor)


class FormBuilder:
    """Construye un formulario a partir de una lista de especificaciones."""

    def __init__(self, parent=None):
        self.parent = parent
        self.campos = {}  # clave -> FormField
        self.orden = []   # claves en orden de declaracion

    def agregar(self, espec):
        """Agrega un campo a partir de su especificacion y devuelve el Field."""
        campo = FormField(espec)
        clave = campo.clave
        self.campos[clave] = campo
        self.orden.append(clave)
        return campo

    def widget(self, clave):
        """Devuelve el widget Qt de un campo."""
        return self.campos[clave].widget

    def valor(self, clave):
        return self.campos[clave].valor()

    def set_valor(self, clave, valor):
        self.campos[clave].set_valor(valor)

    def valores(self):
        return {clave: self.campos[clave].valor() for clave in self.orden}

    def set_valores(self, valores):
        for clave, valor in valores.items():
            if clave in self.campos:
                self.campos[clave].set_valor(valor)

    def campos_decl(self):
        """Devuelve la lista de claves declaradas (en orden)."""
        return list(self.orden)

    def _crear_campo_ui(self, espec, estilos):
        """Crea el campo y su widget. Aplica ajuste de texto y estilo si la especificacion los pide."""
        campo = self.agregar(espec)
        w = campo.crear_widget()
        if espec.get("wrapping"):
            w.setWrapping(True)
        if espec.get("ajustar_texto"):
            w.setWordWrap(True)
        if espec.get("estilo"):
            w.setStyleSheet(estilos[espec["estilo"]])
        return campo, w

    def construir_grupo(self, main_layout, titulo, filas, estilos=None, estilo_grupo=None):
        """Crea un QGroupBox con una fila de rejilla por campo (etiqueta + widget)."""
        grupo = QtWidgets.QGroupBox(titulo)
        if estilo_grupo:
            grupo.setStyleSheet(estilo_grupo)
        grid = QtWidgets.QGridLayout(grupo)
        for fila, espec in enumerate(filas):
            campo, w = self._crear_campo_ui(espec, estilos)
            if espec.get("sin_etiqueta"):
                grid.addWidget(w, fila, 0, 1, espec.get("colspan", 1))
                continue
            grid.addWidget(QtWidgets.QLabel(campo.etiqueta), fila, 0)
            grid.addWidget(w, fila, 1, 1, espec.get("colspan", 1))
        main_layout.addWidget(grupo)
        return grupo

    def construir_suelto(self, main_layout, espec, estilos=None):
        """Añade un campo sin grupo ni etiqueta propia (p. ej. una casilla suelta)."""
        _campo, w = self._crear_campo_ui(espec, estilos)
        main_layout.addWidget(w)
        return w

    def crear(self, espec, estilos=None):
        """Crea el campo y devuelve su widget sin colocarlo en ningun layout."""
        return self._crear_campo_ui(espec, estilos)[1]

    def construir_celda(self, grid, fila, col, espec, estilos=None):
        """Coloca etiqueta (columna col) y widget (columna col+1) en una rejilla existente."""
        campo, w = self._crear_campo_ui(espec, estilos)
        grid.addWidget(QtWidgets.QLabel(campo.etiqueta), fila, col)
        grid.addWidget(w, fila, col + 1)
        return campo

    def construir_bloques(self, main_layout, bloques, estilos=None, estilo_grupo=None):
        """Construye bloques en orden. (clave, titulo, filas) = grupo; (clave, None, filas) = campo suelto.

        Devuelve {clave: QGroupBox o widget}.
        """
        construidos = {}
        for clave, titulo, filas in bloques:
            if titulo is None:
                construidos[clave] = self.construir_suelto(main_layout, filas[0], estilos)
            else:
                construidos[clave] = self.construir_grupo(
                    main_layout, titulo, filas, estilos, estilo_grupo)
        return construidos

    def interpretar_texto(self):
        """Interpreta el texto escrito en los spinners antes de leer valores."""
        for clave in self.orden:
            campo = self.campos[clave]
            if campo.tipo in _TIPOS_NUMERICOS and campo.widget is not None:
                campo.widget.interpretText()


__all__ = ["FormBuilder", "FormField"]
