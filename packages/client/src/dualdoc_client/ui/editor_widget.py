'Заглушка редактора (полный EditorWidget — п. 6.3).'

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget


class EditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_panel = QTextEdit()
        self.source_panel.setPlaceholderText("Source")
        self.source_panel.setReadOnly(True)
        self.target_panel = QTextEdit()
        self.target_panel.setPlaceholderText("Translation")
        self.paragraph_widgets: list = []

        layout = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel("Source"))
        left.addWidget(self.source_panel)
        right = QVBoxLayout()
        right.addWidget(QLabel("Target"))
        right.addWidget(self.target_panel)
        layout.addLayout(left)
        layout.addLayout(right)

    def set_document(self, document: dict | None) -> None:
        self.source_panel.clear()
        self.target_panel.clear()
        if not document:
            return
        content = document.get("content") or {}
        for p in content.get("source") or []:
            self.source_panel.append(p.get("text") or "")
        meta = document.get("metadata") or {}
        lang = meta.get("target_lang") or "ru"
        for p in (content.get("translations") or {}).get(lang) or []:
            self.target_panel.append(p.get("text") or "")
