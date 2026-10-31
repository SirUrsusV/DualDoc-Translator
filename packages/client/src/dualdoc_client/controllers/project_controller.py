'Управление открытыми проектами (вкладками).'

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from dualdoc_client.ui.main_window import MainWindow


class ProjectController(QObject):
    'Слой Controllers, п. 5.1 ТЗ.'

    project_opened = Signal(str)
    project_closed = Signal(str)
    project_saved = Signal(str)
    status_message = Signal(str)

    def __init__(self, main_window: MainWindow | None = None, parent=None):
        super().__init__(parent)
        self._main_window = main_window
        self.open_projects: dict[str, dict[str, Any]] = {}

    def set_main_window(self, main_window: MainWindow) -> None:
        self._main_window = main_window

    def open_project(self, project_id: str) -> None:
        project_id = str(project_id).strip()
        if not project_id:
            self.status_message.emit("Пустой id проекта")
            return

        if project_id in self.open_projects:
            self.status_message.emit(f"Уже открыт: {project_id}")
            if self._main_window is not None:
                tabs = getattr(self._main_window, "project_tabs", None)
                if tabs is not None:
                    for i in range(tabs.count()):
                        if tabs.tabText(i) == project_id:
                            tabs.setCurrentIndex(i)
                            break
            return

        self.open_projects[project_id] = {
            "id": project_id,
            "title": project_id,
            "dirty": False,
        }

        if self._main_window is not None and hasattr(
            self._main_window, "open_project"
        ):
            self._main_window.open_project(project_id)

        self.project_opened.emit(project_id)
        self.status_message.emit(f"Открыт проект: {project_id}")

    def close_project(self, project_id: str) -> None:
        project_id = str(project_id).strip()
        if project_id not in self.open_projects:
            self.status_message.emit(f"Проект не открыт: {project_id}")
            return

        del self.open_projects[project_id]

        if self._main_window is not None and hasattr(
            self._main_window, "close_project"
        ):
            self._main_window.close_project(project_id)

        self.project_closed.emit(project_id)
        self.status_message.emit(f"Закрыт проект: {project_id}")

    def save_project(self, project_id: str) -> None:
        project_id = str(project_id).strip()
        if project_id not in self.open_projects:
            self.status_message.emit(f"Нечего сохранять: {project_id}")
            return

        self.open_projects[project_id]["dirty"] = False
        self.project_saved.emit(project_id)
        self.status_message.emit(
            f"Сохранение проекта {project_id} (пока заглушка)"
        )
