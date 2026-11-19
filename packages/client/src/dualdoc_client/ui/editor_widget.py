"""EditorWidget: редактор с двумя панелями и поабзацным отображением (п. 6.3)."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

STATUS_LABELS = {
    "draft": "Черновик",
    "translated": "Переведено",
    "reviewed": "Проверено",
}


class ParagraphRow(QWidget):
    """Один абзац: исходник (слева) + поле перевода (справа) + кнопка и статус."""

    translate_clicked = Signal(str)      # para_id
    text_edited = Signal(str, str)       # para_id, новый текст

    def __init__(self, para_id, source_text, target_text="", status="draft",
                 parent=None):
        super().__init__(parent)
        self.para_id = para_id

        self.source_panel = QTextEdit()
        self.source_panel.setPlainText(source_text or "")
        self.source_panel.setReadOnly(True)
        self.source_panel.setFixedHeight(60)

        self.target_panel = QTextEdit()
        self.target_panel.setPlaceholderText("Translation")
        self.target_panel.setPlainText(target_text or "")
        self.target_panel.setFixedHeight(60)
        self.target_panel.textChanged.connect(self._on_edited)

        self.translate_button = QPushButton("Перевести")
        self.translate_button.clicked.connect(
            lambda: self.translate_clicked.emit(self.para_id)
        )

        self.status_label = QLabel(STATUS_LABELS.get(status, status))

        layout = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel(f"Source [{para_id}]"))
        left.addWidget(self.source_panel)
        left.addWidget(self.translate_button)
        right = QVBoxLayout()
        right.addWidget(QLabel(f"Target — {self.status_label.text()}"))
        right.addWidget(self.target_panel)
        layout.addLayout(left)
        layout.addLayout(right)

    def _on_edited(self):
        self.text_edited.emit(self.para_id, self.target_panel.toPlainText())

    def set_target_text(self, text):
        """Установить перевод без срабатывания text_edited."""
        self.target_panel.blockSignals(True)
        self.target_panel.setPlainText(text or "")
        self.target_panel.blockSignals(False)

    def set_status(self, status):
        self.status_label.setText(STATUS_LABELS.get(status, status))


class EditorWidget(QWidget):
    translate_requested = Signal(str)    # para_id
    paragraph_edited = Signal(str, str)  # para_id, текст
    def on_translate_clicked(self, para_id: str) -> None:
        """Обработчик кнопки «Перевести»: запрашивает перевод абзаца."""
        self.translate_requested.emit(para_id)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paragraph_widgets: list = []

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.paragraphs_layout = QVBoxLayout(self.container)
        self.paragraphs_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.scroll)
        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)

    def set_document(self, document: dict | None) -> None:
        """Разобрать документ на абзацы: source слева, перевод справа."""
        for row in self.paragraph_widgets:
            row.deleteLater()
        self.paragraph_widgets.clear()
        while self.paragraphs_layout.count():
            item = self.paragraphs_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not document:
            return

        content = document.get("content") or {}
        source_paras = content.get("source") or []
        meta = document.get("metadata") or {}
        lang = meta.get("target_lang") or "ru"
        translations = (content.get("translations") or {}).get(lang) or []

        for i, para in enumerate(source_paras):
            para_id = str(para.get("id") or f"para_{i + 1}")
            target = ""
            if i < len(translations):
                target = translations[i].get("text") or ""
            row = ParagraphRow(
                para_id,
                para.get("text") or "",
                target,
                (translations[i].get("status") if i < len(translations) else None)
                or "draft",
            )
            row.translate_clicked.connect(self.on_translate_clicked)
            row.text_edited.connect(self.paragraph_edited)
            self.paragraph_widgets.append(row)
            self.paragraphs_layout.addWidget(row)

    def update_paragraph_status(self, para_id, status):
        for row in self.paragraph_widgets:
            if row.para_id == str(para_id):
                row.set_status(status)

    def set_translation(self, para_id, text):
        for row in self.paragraph_widgets:
            if row.para_id == str(para_id):
                row.set_target_text(text)
