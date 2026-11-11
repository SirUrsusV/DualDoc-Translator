from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from dualdoc_client.controllers.document_controller import DocumentController
from dualdoc_client.controllers.project_controller import ProjectController
from dualdoc_client.controllers.version_controller import VersionController


class MainWindow(QMainWindow):
    'Главное окно: UI → Project / Document / Version controllers.'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DualDoc Translator")
        self.resize(1100, 700)

        self.project_tabs = QTabWidget()
        self.project_tabs.setTabsClosable(True)
        self.project_tabs.tabCloseRequested.connect(self._on_tab_close)
        self.setCentralWidget(self.project_tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.project_controller = ProjectController(self)
        self.document_controller = DocumentController(user_id="local-user")
        self.version_controller = VersionController()

        self.project_controller.status_message.connect(self.update_status)
        self.document_controller.status_message.connect(self.update_status)
        self.document_controller.error_occurred.connect(self.update_status)
        self.version_controller.status_message.connect(self.update_status)
        self.version_controller.error_occurred.connect(self.update_status)

        #Document → Version: после load/create подвязать документ
        self.document_controller.document_loaded.connect(self._on_document_loaded)
        #после коммита — snapshot для rollback/merge
        self.document_controller.commit_created.connect(self._on_commit_created)

        self._create_menu()
        self.create_toolbar()

        self._add_welcome_tab()
        self.update_status("Готово")

    def _create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(
            self._make_action("Создать документ", self._on_new_document)
        )
        file_menu.addAction(
            self._make_action("Открыть…", self._on_open_document)
        )
        file_menu.addAction(
            self._make_action(
                "Сохранить", self._on_save_current, QKeySequence.Save
            )
        )
        file_menu.addAction(
            self._make_action(
                "Сохранить как…", self._on_save_as, QKeySequence.SaveAs
            )
        )
        file_menu.addSeparator()
        file_menu.addAction(self._make_action("Выход", self.close))

        versions_menu = menubar.addMenu("Версии")
        versions_menu.addAction(
            self._make_action("Коммит", self._on_commit)
        )
        versions_menu.addAction(
            self._make_action("Список коммитов", self._on_fetch_commits)
        )

        for title in ("Правка", "Вид", "Перевод", "ИИ", "Команда"):
            menu = menubar.addMenu(title)
            menu.addAction(self._make_action("Скоро…", self._stub))

    def create_toolbar(self):
        self.toolbar = QToolBar("Main")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(
            self._make_action("Создать", self._on_new_document)
        )
        self.toolbar.addAction(
            self._make_action("Открыть", self._on_open_document)
        )
        self.toolbar.addAction(
            self._make_action("Сохранить", self._on_save_current)
        )
        self.toolbar.addSeparator()
        self.toolbar.addAction(self._make_action("Перевести", self._stub))
        self.toolbar.addAction(
            self._make_action("Коммит", self._on_commit)
        )
        self.toolbar.addAction(self._make_action("ИИ", self._stub))

    def open_project(self, project_id: str):
        'Вкладка (вызывает ProjectController).'
        page = QWidget()
        label = QLabel(f"Проект: {project_id}\n(редактор появится позже)")
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(page)
        layout.addWidget(label)
        index = self.project_tabs.addTab(page, str(project_id))
        self.project_tabs.setCurrentIndex(index)

    def close_project(self, project_id: str):
        for i in range(self.project_tabs.count()):
            if self.project_tabs.tabText(i) == str(project_id):
                self.project_tabs.removeTab(i)
                return

    def update_status(self, message: str):
        self.status_bar.showMessage(message, 8000)

    def switch_theme(self, theme: str):
        if theme == "dark":
            self.setStyleSheet(
                "QMainWindow { background: #2b2b2b; color: #eee; }"
                "QMenuBar { background: #333; color: #eee; }"
                "QToolBar { background: #333; color: #eee; }"
                "QStatusBar { background: #333; color: #eee; }"
            )
        else:
            self.setStyleSheet("")
        self.update_status(f"Тема: {theme}")

    def _add_welcome_tab(self):
        welcome = QLabel("DualDoc Translator\nСоздайте или откройте документ")
        welcome.setAlignment(Qt.AlignCenter)
        self.project_tabs.addTab(welcome, "Старт")

    def _on_tab_close(self, index: int):
        title = self.project_tabs.tabText(index)
        if title == "Старт":
            self.project_tabs.removeTab(index)
            self.update_status("Вкладка закрыта: Старт")
            return
        self.project_controller.close_project(title)

    def _on_document_loaded(self, document):
        'Document → Version: один и тот же document в памяти.'
        self.version_controller.set_document(document)
        name = (document or {}).get("metadata", {}).get("name") or "document"
        #вкладка через ProjectController
        self.project_controller.open_project(str(name))

    def _on_commit_created(self, _message: str):
        'После коммита — snapshot для rollback/merge.'
        self.version_controller.set_document(self.document_controller.document)
        self.version_controller.attach_snapshot_to_last_commit()

    def _on_new_document(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Создать документ",
            "untitled.dualtrans",
            "Dualtrans (*.dualtrans);;All (*.*)",
        )
        if not path:
            return
        if not path.endswith(".dualtrans"):
            path += ".dualtrans"
        name = Path(path).stem
        self.document_controller.create_new_document(
            name, "en", "ru", file_path=path
        )
        #сразу сохранить пустой каркас на диск
        self.document_controller.save_document()

    def _on_open_document(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть документ",
            "",
            "Dualtrans (*.dualtrans);;All (*.*)",
        )
        if not path:
            return
        self.document_controller.load_document(path)

    def _on_save_current(self):
        if self.document_controller.document is None:
            self.update_status("Нет документа для сохранения")
            return
        self.document_controller.save_document()

    def _on_save_as(self):
        if self.document_controller.document is None:
            self.update_status("Нет документа для сохранения")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как",
            self.document_controller._file_path or "untitled.dualtrans",
            "Dualtrans (*.dualtrans);;All (*.*)",
        )
        if not path:
            return
        if not path.endswith(".dualtrans"):
            path += ".dualtrans"
        self.document_controller._file_path = path
        self.document_controller.save_document()

    def _on_commit(self):
        if self.document_controller.document is None:
            self.update_status("Нет документа для коммита")
            return
        self.document_controller.create_commit("manual commit")

    def _on_fetch_commits(self):
        commits = self.version_controller.fetch_commits()
        if not commits:
            self.update_status("Коммитов нет")
            return
        names = ", ".join(c.get("commit_hash", "?") for c in commits)
        self.update_status(f"Коммиты: {names}")

    def _stub(self):
        self.update_status("Действие пока не реализовано")

    def _make_action(self, text, slot, shortcut=None):
        action = QAction(text, self)
        action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
        return action
