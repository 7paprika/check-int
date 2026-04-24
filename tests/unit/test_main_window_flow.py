from pathlib import Path

from check_int.app.controller import MainWindowController
from check_int.ui.main_window import MainWindow


class _FakeUseCase:
    def run(self, *, eq_list_path, pid_path, datasheet_path):
        return [
            {
                "tag_no": "P-1401",
                "field_name": "material",
                "status": "mismatch",
                "master_value": "SS316",
                "pid_value": "CS",
                "datasheet_value": "SS316",
            }
        ]


class _FailingUseCase:
    def run(self, *, eq_list_path, pid_path, datasheet_path):
        raise RuntimeError("OCR engine is not installed")


class _FakeExporter:
    def __init__(self):
        self.called_with = None

    def __call__(self, rows, output_path):
        self.called_with = (rows, output_path)
        Path(output_path).write_text("ok", encoding="utf-8")
        return Path(output_path)


def test_main_window_accepts_use_case_and_runs_comparison(qtbot, tmp_path) -> None:
    fake_use_case = _FakeUseCase()
    fake_exporter = _FakeExporter()
    window = MainWindow(use_case=fake_use_case, report_exporter=fake_exporter)
    qtbot.addWidget(window)

    controller = window.controller

    window.file_panel.eq_list_path.setText(str(tmp_path / "eq.xlsx"))
    window.file_panel.pid_path.setText(str(tmp_path / "pid.pdf"))
    window.file_panel.datasheet_path.setText(str(tmp_path / "datasheet.pdf"))
    window.file_panel.report_path.setText(str(tmp_path / "report.xlsx"))

    controller.run_comparison()

    assert window.result_table.rowCount() == 1
    assert "비교 결과 1건을 로드했습니다." in window.status_log.toPlainText()

    controller.save_report()

    assert fake_exporter.called_with is not None
    assert Path(fake_exporter.called_with[1]).exists()
    assert "리포트 저장 완료" in window.status_log.toPlainText()


def test_main_window_controller_reports_use_case_errors(qtbot, tmp_path) -> None:
    window = MainWindow(use_case=_FailingUseCase())
    qtbot.addWidget(window)
    window.file_panel.eq_list_path.setText(str(tmp_path / "eq.xlsx"))
    window.file_panel.pid_path.setText(str(tmp_path / "pid.pdf"))
    window.file_panel.datasheet_path.setText(str(tmp_path / "datasheet.pdf"))

    window.controller.run_comparison()

    assert window.result_table.rowCount() == 0
    assert "비교 실행 실패" in window.status_log.toPlainText()
    assert "OCR engine is not installed" in window.status_log.toPlainText()


def test_main_window_controller_requires_paths_before_run_or_save(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    controller = MainWindowController(window, use_case=_FakeUseCase(), report_exporter=_FakeExporter())

    controller.run_comparison()
    controller.save_report()

    log = window.status_log.toPlainText()
    assert "세 문서 경로를 모두 선택해야 합니다." in log
    assert "저장 경로와 결과 데이터가 필요합니다." in log
