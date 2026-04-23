from dataclasses import dataclass, field

from check_int.domain.enums import ComparisonStatus, DocumentType


@dataclass(slots=True)
class DocumentEvidence:
    page_no: int
    bbox: tuple[int, int, int, int] | None = None
    image_path: str | None = None
    raw_text: str | None = None
    note: str | None = None
    confidence: float | None = None


@dataclass(slots=True)
class EquipmentRecord:
    document_type: DocumentType
    tag_no: str
    equipment_name: str | None = None
    service: str | None = None
    capacity: str | None = None
    size: str | None = None
    model: str | None = None
    rating: str | None = None
    material: str | None = None
    design_pressure: str | None = None
    design_temperature: str | None = None
    operating_temperature: str | None = None
    source_file: str = ""
    page_no: int | None = None
    evidence: list[DocumentEvidence] = field(default_factory=list)


@dataclass(slots=True)
class FieldComparisonResult:
    field_name: str
    master_value: str | None
    pid_value: str | None
    datasheet_value: str | None
    status: ComparisonStatus
    master_evidence: DocumentEvidence | None = None
    pid_evidence: DocumentEvidence | None = None
    datasheet_evidence: DocumentEvidence | None = None


@dataclass(slots=True)
class IntegrityCheckResult:
    tag_no: str
    comparisons: list[FieldComparisonResult] = field(default_factory=list)
    summary: dict[ComparisonStatus, int] = field(default_factory=dict)