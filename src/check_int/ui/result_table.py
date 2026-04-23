from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem


class ResultTableWidget(QTableWidget):
    row_selected = Signal(dict)

    HEADERS = [
        "Tag No",
        "Field",
        "Status",
        "Master",
        "P&ID",
        "Datasheet",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(0, len(self.HEADERS), parent)
        self._rows: list[dict[str, str | None]] = []
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.itemSelectionChanged.connect(self._emit_selected_row)

    def set_rows(self, rows: list[dict[str, str | None]]) -> None:
        self._rows = rows
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                row.get("tag_no"),
                row.get("field_name"),
                row.get("status"),
                row.get("master_value"),
                row.get("pid_value"),
                row.get("datasheet_value"),
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value or "")
                if row.get("status") == "mismatch" and col_index >= 3:
                    item.setBackground(QColor("#fff1b3"))
                self.setItem(row_index, col_index, item)
        self.resizeColumnsToContents()

    def _emit_selected_row(self) -> None:
        row_index = self.currentRow()
        if 0 <= row_index < len(self._rows):
            self.row_selected.emit(self._rows[row_index])