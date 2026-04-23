from check_int.domain.enums import DocumentType
from check_int.domain.models import EquipmentRecord
from check_int.services.record_mapper import map_structured_row_to_equipment_record


def parse_pid_rows(rows: list[dict[str, object]], *, source_file: str) -> list[EquipmentRecord]:
    return [
        map_structured_row_to_equipment_record(
            row,
            document_type=DocumentType.PID,
            source_file=source_file,
        )
        for row in rows
        if row.get("tag_no")
    ]