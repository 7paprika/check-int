from PySide6.QtWidgets import QGroupBox, QLabel, QHBoxLayout, QVBoxLayout, QWidget


class EvidencePanel(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("증빙 비교", parent)
        layout = QVBoxLayout(self)
        self.summary = QLabel("행을 선택하면 증빙 정보가 표시됩니다.", self)
        layout.addWidget(self.summary)

        body = QWidget(self)
        body_layout = QHBoxLayout(body)
        self.pid_label = QLabel("P&ID 증빙 대기 중", body)
        self.datasheet_label = QLabel("Datasheet 증빙 대기 중", body)
        body_layout.addWidget(self.pid_label)
        body_layout.addWidget(self.datasheet_label)
        layout.addWidget(body)

    def set_payload(self, payload: dict[str, str | None]) -> None:
        self.summary.setText(
            f"{payload.get('tag_no')} / {payload.get('field_name')} / 상태: {payload.get('status')}"
        )
        self.pid_label.setText(f"P&ID 값: {payload.get('pid_value') or '-'}")
        self.datasheet_label.setText(f"Datasheet 값: {payload.get('datasheet_value') or '-'}")