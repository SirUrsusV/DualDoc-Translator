'Заглушка ИИ-панели.'

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class AIPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._out = QTextEdit()
        self._out.setReadOnly(True)
        self._out.setPlaceholderText("ИИ-подсказки появятся здесь")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ИИ"))
        layout.addWidget(self._out)
