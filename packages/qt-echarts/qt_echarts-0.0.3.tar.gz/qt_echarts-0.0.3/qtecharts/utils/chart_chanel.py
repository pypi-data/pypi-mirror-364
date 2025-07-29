from PyQt5.QtCore import QObject, pyqtSlot


class ChartChanel(QObject):
    def __init__(self, parent=None, func=None):
        super().__init__(parent)
        self.func = func

    @pyqtSlot(str)
    def js_to_qt(self, msg):
        self.func(msg)

    @pyqtSlot()
    def py_to_hs(self):
        pass