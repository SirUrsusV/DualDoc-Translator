'Виджет одной вкладки проекта (п. 6.2 ТЗ).'

from __future__ import annotations  #анастейшн (ну типа анастасия)

from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QSplitter, QVBoxLayout, QWidget

from dualdoc_client.ui.ai_panel_widget import AIPanelWidget
from dualdoc_client.ui.editor_widget import EditorWidget
from dualdoc_client.ui.version_history_widget import VersionHistoryWidget


class ProjectTab(QWidget):
    'Вкладка: редактор + панель версий + ИИ.'

    def __init__(self, project_id: str, parent=None):
        super().__init__(parent)
        self.project_id = str(project_id)
        self._document: dict[str, Any] | None = None

        self.editor = EditorWidget()
        self.version_panel = VersionHistoryWidget()
        self.ai_panel = AIPanelWidget()

        side = QWidget()
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.addWidget(self.version_panel, stretch=2)
        side_layout.addWidget(self.ai_panel, stretch=1)

        splitter = QSplitter()
        splitter.addWidget(self.editor)
        splitter.addWidget(side)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root = QHBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.addWidget(splitter)

    def load_document(self, document: dict[str, Any] | None) -> None:
        self._document = document
        self.editor.set_document(document)
        history = (document or {}).get("version_history") or []
        self.version_panel.set_commits(history)

    def get_current_document(self) -> dict[str, Any] | None:
        return self._document
