from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class FilePanel(QGroupBox):
    run_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("입력 문서", parent)
        self.eq_list_path = QLineEdit(self)
        self.pid_path = QLineEdit(self)
        self.datasheet_path = QLineEdit(self)

        layout = QGridLayout(self)
        self._add_row(layout, 0, self.eq_list_path, "EQ List")
        self._add_row(layout, 1, self.pid_path, "P&ID")
        self._add_row(layout, 2, self.datasheet_path, "Datasheet")

        run_button = QPushButton("비교 실행", self)
        run_button.clicked.connect(self.run_requested.emit)
        layout.addWidget(run_button, 3, 2)

    def _add_row(self, layout: QGridLayout, row: int, line_edit: QLineEdit, title: str) -> None:
        browse_button = QPushButton(f"{title} 선택", self)
        browse_button.clicked.connect(lambda: self._pick_file(line_edit))
        line_edit.setPlaceholderText(f"{title} 파일 경로")
        line_edit.setReadOnly(True)
        row_container = QWidget(self)
        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(line_edit)
        layout.addWidget(browse_button, row, 0)
        layout.addWidget(row_container, row, 1, 1, 2)

    def _pick_file(self, target: QLineEdit) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if file_path:
            target.setText(file_path)