from math import isnan
from typing import Any

from check_int.domain.enums import DocumentType
from check_int.domain.models import EquipmentRecord


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
        operating_temperature=_clean_value(row.get("operating_temperature")),
        source_file=source_file,
        page_no=_clean_int(row.get("page_no")),
    )


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