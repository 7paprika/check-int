from PySide6.QtGui import QColor

from check_int.ui.main_window import MainWindow
from check_int.ui.result_table import ResultTableWidget


ROWS = [
    {
        "tag_no": "P-101",
        "field_name": "service",
        "status": "matched",
        "master_value": "Cooling Water",
        "pid_value": "Cooling Water",
        "datasheet_value": "Cooling Water",
    },
    {
        "tag_no": "P-101",
        "field_name": "design_pressure",
        "status": "mismatch",
        "master_value": "10 bar",
        "pid_value": "10 bar",
        "datasheet_value": "12 bar",
    },
]


def test_main_window_builds_phase_one_ui(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.file_panel.title() == "입력 문서"
    assert window.result_table.columnCount() == 6
    assert window.evidence_panel.title() == "증빙 비교"
    assert "LEDIC UI 초기화 완료" in window.status_log.toPlainText()


def test_result_table_populates_rows_and_highlights_mismatch(qtbot) -> None:
    widget = ResultTableWidget()
    qtbot.addWidget(widget)

    widget.set_rows(ROWS)

    assert widget.rowCount() == 2
    assert widget.item(0, 0).text() == "P-101"
    assert widget.item(1, 1).text() == "design_pressure"
    assert widget.item(1, 5).text() == "12 bar"

    mismatch_color = widget.item(1, 5).background().color()
    assert mismatch_color == QColor("#fff1b3")


def test_result_table_emits_selected_row_payload(qtbot) -> None:
    widget = ResultTableWidget()
    qtbot.addWidget(widget)
    widget.set_rows(ROWS)

    captured: list[dict[str, str | None]] = []
    widget.row_selected.connect(captured.append)

    widget.selectRow(1)
    widget._emit_selected_row()  # noqa: SLF001

    assert captured[0]["field_name"] == "design_pressure"
    assert captured[0]["status"] == "mismatch"
