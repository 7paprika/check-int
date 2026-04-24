from PySide6.QtWidgets import QApplication

from check_int.app.use_cases import build_default_use_case
from check_int.config import AppConfig
from check_int.ui.main_window import MainWindow


def main() -> int:
    config = AppConfig.from_base_dir(".")
    app = QApplication([])
    window = MainWindow(use_case=build_default_use_case(config))
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
