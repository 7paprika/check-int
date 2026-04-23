from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGroupBox, QLabel, QHBoxLayout, QVBoxLayout, QWidget


class EvidencePanel(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("증빙 비교", parent)
        layout = QVBoxLayout(self)
        self.summary = QLabel("행을 선택하면 증빙 정보가 표시됩니다.", self)
        layout.addWidget(self.summary)

        body = QWidget(self)
        body_layout = QHBoxLayout(body)
        self.pid_image_label = QLabel(body)
        self.datasheet_image_label = QLabel(body)
        self.pid_caption = QLabel("P&ID 값: -", body)
        self.datasheet_caption = QLabel("Datasheet 값: -", body)
        self._set_placeholder(self.pid_image_label, "P&ID 증빙 대기 중")
        self._set_placeholder(self.datasheet_image_label, "Datasheet 증빙 대기 중")

        pid_box = QWidget(body)
        pid_layout = QVBoxLayout(pid_box)
        pid_layout.addWidget(self.pid_image_label)
        pid_layout.addWidget(self.pid_caption)

        datasheet_box = QWidget(body)
        datasheet_layout = QVBoxLayout(datasheet_box)
        datasheet_layout.addWidget(self.datasheet_image_label)
        datasheet_layout.addWidget(self.datasheet_caption)

        body_layout.addWidget(pid_box)
        body_layout.addWidget(datasheet_box)
        layout.addWidget(body)

    def set_payload(self, payload: dict[str, str | None]) -> None:
        self.summary.setText(
            f"{payload.get('tag_no')} / {payload.get('field_name')} / 상태: {payload.get('status')}"
        )
        self.pid_caption.setText(f"P&ID 값: {payload.get('pid_value') or '-'}")
        self.datasheet_caption.setText(f"Datasheet 값: {payload.get('datasheet_value') or '-'}")
        self._set_image(self.pid_image_label, payload.get("pid_image_path"), "P&ID 증빙 대기 중")
        self._set_image(
            self.datasheet_image_label,
            payload.get("datasheet_image_path"),
            "Datasheet 증빙 대기 중",
        )

    def _set_image(self, label: QLabel, image_path: str | None, placeholder: str) -> None:
        if image_path and Path(image_path).exists():
            pixmap = QPixmap(image_path)
            label.setPixmap(pixmap)
            label.setText("")
            return
        label.clear()
        label.setText(placeholder)

    def _set_placeholder(self, label: QLabel, text: str) -> None:
        label.clear()
        label.setText(text)
