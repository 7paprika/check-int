from math import isnan
from typing import Any

from check_int.domain.enums import DocumentType
from check_int.domain.models import DocumentEvidence, EquipmentRecord


def map_structured_row_to_equipment_record(
    row: dict[str, Any],
    *,
    document_type: DocumentType,
    source_file: str,
) -> EquipmentRecord:
    return EquipmentRecord(
        document_type=document_type,
        tag_no=_clean_value(row.get("tag_no")) or "",
        equipment_name=_clean_value(row.get("equipment_name")),
        service=_clean_value(row.get("service")),
        capacity=_clean_value(row.get("capacity")),
        size=_clean_value(row.get("size")),
        model=_clean_value(row.get("model")),
        rating=_clean_value(row.get("rating")),
        material=_clean_value(row.get("material")),
        design_pressure=_clean_value(row.get("design_pressure")),
        design_temperature=_clean_value(row.get("design_temperature")),
        operating_pressure=_clean_value(row.get("operating_pressure")),
        operating_temperature=_clean_value(row.get("operating_temperature")),
        source_file=source_file,
        page_no=_clean_int(row.get("page_no")),
        evidence=_build_evidence(row),
    )


def _build_evidence(row: dict[str, Any]) -> list[DocumentEvidence]:
    page_no = _clean_int(row.get("page_no"))
    if page_no is None:
        return []
    return [
        DocumentEvidence(
            page_no=page_no,
            bbox=_clean_bbox(row.get("bbox")),
            image_path=_clean_value(row.get("image_path")),
            raw_text=_clean_value(row.get("raw_text")),
            note=_clean_value(row.get("note")) or _clean_value(row.get("region_label")),
            confidence=_clean_float(row.get("confidence")),
        )
    ]


def _clean_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and isnan(value):
        return None

    text = str(value).strip()
    return text or None


def _clean_int(value: Any) -> int | None:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    return int(float(cleaned))


def _clean_float(value: Any) -> float | None:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    return float(cleaned)


def _clean_bbox(value: Any) -> tuple[int, int, int, int] | None:
    if value is None:
        return None
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
    else:
        parts = list(value)
    if len(parts) != 4:
        return None
    return tuple(int(float(part)) for part in parts)
