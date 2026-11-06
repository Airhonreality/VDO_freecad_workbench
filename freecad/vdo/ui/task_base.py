# =====================================================================
# task_base.py
# Utilidades comunes para Task Panels VDO.
# - Gestión de transacciones con propiedad explícita.
# - Callbacks on_accept / on_cancel para el flujo de creación.
# - Cierre seguro del diálogo.
# =====================================================================

import FreeCAD as App

from freecad.vdo.qt_compat import QtCore, QtWidgets


def cerrar_dialogo():
    """Cierra el Task Panel activo sin asumir que estamos en modo edición."""
    try:
        import FreeCADGui as Gui
        Gui.Control.closeDialog()
    except Exception:
        App.Console.PrintWarning("[VDO] No se pudo cerrar el diálogo activo")


# Acción de cierre -> (método de Document, verbo del aviso de error).
_CIERRE_TRANSACCION = {
    "commit": ("commitTransaction", "confirmar"),
    "abort": ("abortTransaction", "abortar"),
}


class VDOTransactionMixin:
    """Mixin para Task Panels VDO.

    Reglas:
    - `auto_transaction=True`: el panel abre y confirma su propia
      transacción (edición normal).
    - `auto_transaction=False`: la transacción la gestiona un flujo
      externo (creación de módulo). El panel nunca confirma ni aborta.
    """

    def _init_vdo_task(self, on_accept=None, on_cancel=None,
                       auto_transaction=True,
                       transaction_name="Editar módulo VDO"):
        self._vdo_on_accept = on_accept
        self._vdo_on_cancel = on_cancel
        self.auto_transaction = auto_transaction
        self.transaction_name = transaction_name
        self._vdo_tx_open = False

    def _init_panel_vdo(self, obj, on_accept, on_cancel, auto_transaction,
                        transaction_name, propiedades=()):
        """Secuencia común de arranque de los task panels de módulo."""
        self.obj = obj
        self._vdo_aceptado = False
        self._init_vdo_task(
            on_accept=on_accept,
            on_cancel=on_cancel,
            auto_transaction=auto_transaction,
            transaction_name=transaction_name,
        )
        self.form = self._crear_widget()
        if obj:
            for anadir_propiedades in propiedades:
                anadir_propiedades(obj)
            self._cargar_valores(obj)

    def _crear_botonera_vdo(self, main_layout, tip_aceptar=None, tip_cancelar=None):
        """Botonera Aceptar/Cancelar de los task panels; tooltips opcionales."""
        botones = QtWidgets.QDialogButtonBox()
        btn_ok = botones.addButton(
            "Crear y colocar" if not self.auto_transaction else "Aplicar",
            QtWidgets.QDialogButtonBox.AcceptRole)
        btn_cancelar = botones.addButton(
            "Cancelar", QtWidgets.QDialogButtonBox.RejectRole)
        botones.accepted.connect(self._on_ok)
        botones.rejected.connect(self._on_cancel)
        if tip_aceptar is not None:
            btn_ok.setToolTip(tip_aceptar)
        if tip_cancelar is not None:
            btn_cancelar.setToolTip(tip_cancelar)
        main_layout.addWidget(botones)

    # -----------------------------------------------------------------
    # Transacciones
    # -----------------------------------------------------------------
    def _vdo_begin(self):
        if not self.auto_transaction:
            return False
        doc = App.ActiveDocument
        if doc is None:
            return False
        if doc.HasPendingTransaction:
            # No abrimos una transacción si ya hay una ajena en curso.
            self._vdo_tx_open = False
            return False
        try:
            doc.openTransaction(self.transaction_name)
            self._vdo_tx_open = True
            return True
        except Exception as exc:
            App.Console.PrintWarning(
                f"[VDO] No se pudo abrir transacción: {exc}\n")
            self._vdo_tx_open = False
            return False

    def _vdo_cerrar(self, accion):
        """Confirma ("commit") o aborta ("abort") la transacción abierta."""
        if not self.auto_transaction or not self._vdo_tx_open:
            return
        metodo, verbo = _CIERRE_TRANSACCION[accion]
        doc = App.ActiveDocument
        try:
            if doc is not None:
                getattr(doc, metodo)()
        except Exception as exc:
            App.Console.PrintWarning(
                f"[VDO] No se pudo {verbo} transacción: {exc}\n")
        finally:
            self._vdo_tx_open = False

    # -----------------------------------------------------------------
    # Callbacks de flujo
    # -----------------------------------------------------------------
    def _vdo_call_accept(self):
        if self._vdo_on_accept:
            QtCore.QTimer.singleShot(0, self._vdo_on_accept)

    def _vdo_call_cancel(self):
        if self._vdo_on_cancel:
            QtCore.QTimer.singleShot(0, self._vdo_on_cancel)

    # Botones OK / Cancelar comunes a todos los Task Panels VDO.
    def _on_ok(self):
        if self.accept():
            cerrar_dialogo()

    def _on_cancel(self):
        self.reject()
        cerrar_dialogo()

    # -----------------------------------------------------------------
    # API estándar de Task Panel (compartida por todos los paneles)
    # -----------------------------------------------------------------
    def reject(self):
        """Rechaza cambios: aborta transacción, avisa al flujo y cierra."""
        if getattr(self, "_vdo_aceptado", False):
            return True
        self._vdo_cerrar("abort")
        self._vdo_call_cancel()
        return True

    def clicked(self, button):
        """Slot genérico de clic en botones del panel (sin acción por defecto)."""
        pass

    def getStandardButtons(self):
        """Botones estándar del cuadro de diálogo del Task Panel."""
        return QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

    def helpRequested(self):
        """Solicitud de ayuda (sin acción por defecto)."""
        pass
