from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Главное окно DualDoc Translator (этап 1, п. 6.1)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DualDoc Translator")
        self.resize(1100, 700)

        #центральная часть: вкладки проектов
        self.project_tabs = QTabWidget()
        self.project_tabs.setTabsClosable(True)
        self.project_tabs.tabCloseRequested.connect(self._on_tab_close)
        self.setCentralWidget(self.project_tabs)

        #статус-бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        #меню и тулбар
        self._create_menu()
        self.create_toolbar()

        #стартовая вкладка
        self._add_welcome_tab()
        self.update_status("Готово")

    #меню
    def _create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(self._make_action("Создать документ", self._stub))
        file_menu.addAction(self._make_action("Открыть…", self._stub))
        file_menu.addAction(
            self._make_action("Сохранить", self._stub, QKeySequence.Save)
        )
        file_menu.addSeparator()
        file_menu.addAction(self._make_action("Выход", self.close))

        for title in ("Правка", "Вид", "Перевод", "Версии", "ИИ", "Команда"):
            menu = menubar.addMenu(title)
            menu.addAction(self._make_action("Скоро…", self._stub))

    #тулбар
    def create_toolbar(self):
        self.toolbar = QToolBar("Main")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(self._make_action("Создать", self._stub))
        self.toolbar.addAction(self._make_action("Открыть", self._stub))
        self.toolbar.addAction(self._make_action("Сохранить", self._stub))
        self.toolbar.addSeparator()
        self.toolbar.addAction(self._make_action("Перевести", self._stub))
        self.toolbar.addAction(self._make_action("Коммит", self._stub))
        self.toolbar.addAction(self._make_action("ИИ", self._stub))

    #методы
    def open_project(self, project_id: str):
        page = QWidget()
        label = QLabel(f"Проект: {project_id}\n(редактор появится позже)")
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(page)
        layout.addWidget(label)

        index = self.project_tabs.addTab(page, str(project_id))
        self.project_tabs.setCurrentIndex(index)
        self.update_status(f"Открыт проект: {project_id}")

    def close_project(self, project_id: str):
        for i in range(self.project_tabs.count()):
            if self.project_tabs.tabText(i) == str(project_id):
                self.project_tabs.removeTab(i)
                self.update_status(f"Закрыт проект: {project_id}")
                return
        self.update_status(f"Проект не найден: {project_id}")

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

    #вспомогательное
    def _add_welcome_tab(self):
        welcome = QLabel("DualDoc Translator\nСоздайте или откройте документ")
        welcome.setAlignment(Qt.AlignCenter)
        self.project_tabs.addTab(welcome, "Старт")

    def _on_tab_close(self, index: int):
        title = self.project_tabs.tabText(index)
        self.project_tabs.removeTab(index)
        self.update_status(f"Вкладка закрыта: {title}")

    def _stub(self):
        self.update_status("Действие пока не реализовано")

    def _make_action(self, text, slot, shortcut=None):
        action = QAction(text, self)
        action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
        return action