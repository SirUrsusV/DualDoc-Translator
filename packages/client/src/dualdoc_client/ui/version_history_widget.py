'Заглушка панели версий.'

from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget


class VersionHistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._list = QListWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Версии"))
        layout.addWidget(self._list)

    def set_commits(self, commits: list | None) -> None:
        self._list.clear()
        for c in commits or []:
            h = c.get("commit_hash", "?")
            m = c.get("message", "")
            self._list.addItem(f"{h}: {m}")
