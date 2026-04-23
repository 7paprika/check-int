from PySide6.QtWidgets import QApplication

from check_int.config import AppConfig
from check_int.ui.main_window import MainWindow


def main() -> int:
    AppConfig.from_base_dir(".")
    app = QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
