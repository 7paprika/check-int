from PIL import Image

from check_int.ui.evidence_panel import EvidencePanel


def test_evidence_panel_loads_side_by_side_images_when_paths_exist(qtbot, tmp_path) -> None:
    pid_image = tmp_path / "pid.png"
    datasheet_image = tmp_path / "datasheet.png"
    Image.new("RGB", (40, 20), color="red").save(pid_image)
    Image.new("RGB", (40, 20), color="blue").save(datasheet_image)

    panel = EvidencePanel()
    qtbot.addWidget(panel)

    panel.set_payload(
        {
            "tag_no": "P-1501",
            "field_name": "material",
            "status": "mismatch",
            "pid_value": "CS",
            "datasheet_value": "SS316",
            "pid_image_path": str(pid_image),
            "datasheet_image_path": str(datasheet_image),
        }
    )

    assert panel.pid_image_label.pixmap() is not None
    assert panel.datasheet_image_label.pixmap() is not None
    assert "P-1501" in panel.summary.text()


def test_evidence_panel_uses_placeholder_when_image_missing(qtbot) -> None:
    panel = EvidencePanel()
    qtbot.addWidget(panel)

    panel.set_payload(
        {
            "tag_no": "P-1502",
            "field_name": "service",
            "status": "matched",
            "pid_value": "Cooling Water",
            "datasheet_value": "Cooling Water",
        }
    )

    pid_pixmap = panel.pid_image_label.pixmap()
    datasheet_pixmap = panel.datasheet_image_label.pixmap()
    assert pid_pixmap is None or pid_pixmap.isNull()
    assert datasheet_pixmap is None or datasheet_pixmap.isNull()
    assert panel.pid_caption.text() == "P&ID 값: Cooling Water"
    assert panel.datasheet_caption.text() == "Datasheet 값: Cooling Water"
