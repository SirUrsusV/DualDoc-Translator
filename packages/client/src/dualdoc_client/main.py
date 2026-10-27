"""Точка входа desktop-приложения."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

def main() -> int:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("DualDoc Translator")
    window.resize(1200, 800)
    window.setCentralWidget(QLabel("Здесь будет редактор", alignment=0x0084))
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
