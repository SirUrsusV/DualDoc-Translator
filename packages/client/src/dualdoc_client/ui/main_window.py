from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QTabWidget,
    QStatusBar,
    QWidget,
    QLabel,
    QVBoxLayout,
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt

from dualdoc_client.controllers.project_controller import ProjectController


class MainWindow(QMainWindow):
    'Главное окно DualDoc Translator (этап 1, п. 6.1).'

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
        self.project_controller.status_message.connect(self.update_status)

        self._create_menu()
        self.create_toolbar()

        self._add_welcome_tab()
        self.update_status("Готово")

    def _create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(
            self._make_action("Создать документ", self._on_open_demo)
        )
        file_menu.addAction(
            self._make_action("Открыть…", self._on_open_demo)
        )
        file_menu.addAction(
            self._make_action(
                "Сохранить", self._on_save_current, QKeySequence.Save
            )
        )
        file_menu.addSeparator()
        file_menu.addAction(self._make_action("Выход", self.close))

        for title in ("Правка", "Вид", "Перевод", "Версии", "ИИ", "Команда"):
            menu = menubar.addMenu(title)
            menu.addAction(self._make_action("Скоро…", self._stub))

    def create_toolbar(self):
        self.toolbar = QToolBar("Main")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(
            self._make_action("Создать", self._on_open_demo)
        )
        self.toolbar.addAction(
            self._make_action("Открыть", self._on_open_demo)
        )
        self.toolbar.addAction(
            self._make_action("Сохранить", self._on_save_current)
        )
        self.toolbar.addSeparator()
        self.toolbar.addAction(self._make_action("Перевести", self._stub))
        self.toolbar.addAction(self._make_action("Коммит", self._stub))
        self.toolbar.addAction(self._make_action("ИИ", self._stub))

    def open_project(self, project_id: str):
        'Добавить вкладку проекта (вызывается из ProjectController).'
        page = QWidget()
        label = QLabel(f"Проект: {project_id}\n(редактор появится позже)")
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(page)
        layout.addWidget(label)

        index = self.project_tabs.addTab(page, str(project_id))
        self.project_tabs.setCurrentIndex(index)

    def close_project(self, project_id: str):
        'Убрать вкладку проекта (вызывается из ProjectController).'
        for i in range(self.project_tabs.count()):
            if self.project_tabs.tabText(i) == str(project_id):
                self.project_tabs.removeTab(i)
                return

    def update_status(self, message: str):
        self.status_bar.showMessage(message, 5000)

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
        #закрытие через контроллер, чтобы open_projects был в синхроне
        self.project_controller.close_project(title)

    def _on_open_demo(self):
        'Пока без диалога файла — открываем demo-проект.'
        self.project_controller.open_project("demo-1")

    def _on_save_current(self):
        tabs = self.project_tabs
        if tabs.count() == 0:
            self.update_status("Нет открытых вкладок")
            return
        title = tabs.tabText(tabs.currentIndex())
        if title == "Старт":
            self.update_status("Нечего сохранять на стартовой вкладке")
            return
        self.project_controller.save_project(title)

    def _stub(self):
        self.update_status("Действие пока не реализовано")

    def _make_action(self, text, slot, shortcut=None):
        action = QAction(text, self)
        action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
        return action
