from pathlib import Path

import pandas as pd

from check_int.domain.enums import DocumentType
from check_int.domain.models import EquipmentRecord
from check_int.services.record_mapper import map_structured_row_to_equipment_record


def parse_eq_list(path: str | Path) -> list[EquipmentRecord]:
    frame = pd.read_excel(path)
    source_file = Path(path).name
    records: list[EquipmentRecord] = []

    for row in frame.to_dict(orient="records"):
        record = map_structured_row_to_equipment_record(
            row,
            document_type=DocumentType.EQ_LIST,
            source_file=source_file,
        )
        if record.tag_no:
            records.append(record)

    return records