from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit, QSplitter, QVBoxLayout, QWidget

from check_int.app.controller import MainWindowController
from check_int.ui.evidence_panel import EvidencePanel
from check_int.ui.file_panel import FilePanel
from check_int.ui.result_table import ResultTableWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LEDIC - Check Int")
        self.resize(1280, 800)

        central = QWidget(self)
        layout = QVBoxLayout(central)

        self.file_panel = FilePanel(self)
        self.result_table = ResultTableWidget(self)
        self.evidence_panel = EvidencePanel(self)
        self.status_log = QPlainTextEdit(self)
        self.status_log.setReadOnly(True)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(self.result_table)
        splitter.addWidget(self.evidence_panel)
        splitter.setSizes([500, 220])

        layout.addWidget(self.file_panel)
        layout.addWidget(splitter)
        layout.addWidget(self.status_log)
        self.setCentralWidget(central)

        self.controller = MainWindowController(self)
        self.append_status("LEDIC UI 초기화 완료")

    def append_status(self, message: str) -> None:
        self.status_log.appendPlainText(message)
