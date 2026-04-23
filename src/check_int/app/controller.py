from PySide6.QtCore import QObject


class MainWindowController(QObject):
    def __init__(self, window, use_case=None) -> None:
        super().__init__(window)
        self.window = window
        self.use_case = use_case
        self.window.result_table.row_selected.connect(self.window.evidence_panel.set_payload)
        self.window.file_panel.run_requested.connect(self.run_comparison)

    def run_comparison(self) -> None:
        if self.use_case is None:
            self.window.append_status("비교 실행 준비 완료: use case가 아직 연결되지 않았습니다.")
            return

        eq_list_path = self.window.file_panel.eq_list_path.text()
        pid_path = self.window.file_panel.pid_path.text()
        datasheet_path = self.window.file_panel.datasheet_path.text()

        if not all([eq_list_path, pid_path, datasheet_path]):
            self.window.append_status("세 문서 경로를 모두 선택해야 합니다.")
            return

        rows = self.use_case.run(
            eq_list_path=eq_list_path,
            pid_path=pid_path,
            datasheet_path=datasheet_path,
        )
        self.load_rows(rows)

    def load_rows(self, rows: list[dict[str, str | None]]) -> None:
        self.window.result_table.set_rows(rows)
        self.window.append_status(f"비교 결과 {len(rows)}건을 로드했습니다.")