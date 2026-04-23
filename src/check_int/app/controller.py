from PySide6.QtCore import QObject


class MainWindowController(QObject):
    def __init__(self, window) -> None:
        super().__init__(window)
        self.window = window
        self.window.result_table.row_selected.connect(self.window.evidence_panel.set_payload)
        self.window.file_panel.run_requested.connect(self.run_comparison)

    def run_comparison(self) -> None:
        self.window.append_status("비교 실행 준비 완료: Phase 6에서 실제 파이프라인을 연결합니다.")

    def load_rows(self, rows: list[dict[str, str | None]]) -> None:
        self.window.result_table.set_rows(rows)
        self.window.append_status(f"비교 결과 {len(rows)}건을 로드했습니다.")