import re

from check_int.domain.enums import DocumentType


class StubStructuredExtractor:
    def __init__(self, structured_output: dict[str, str] | None = None) -> None:
        self._structured_output = structured_output or {}

    def to_structured_fields(
        self,
        text: str,
        document_type: DocumentType,
    ) -> dict[str, str]:
        if self._structured_output:
            return self._structured_output
        return {
            "document_type": document_type.value,
            "raw_text": text,
        }


class HybridStructuredExtractor:
    FIELD_PATTERNS = {
        "tag_no": [r"TAG(?:\s*NO)?\s*[:=]\s*(.+)"],
        "service": [r"SERVICE\s*[:=]\s*(.+)"],
        "material": [r"MATERIAL\s*[:=]\s*(.+)"],
        "capacity": [r"CAPACITY\s*[:=]\s*(.+)"],
        "size": [r"SIZE\s*[:=]\s*(.+)"],
        "model": [r"MODEL\s*[:=]\s*(.+)"],
        "design_pressure": [r"DESIGN\s*PRESSURE\s*[:=]\s*(.+)"],
        "design_temperature": [r"DESIGN\s*TEMPERATURE\s*[:=]\s*(.+)"],
        "operating_temperature": [r"OPERATING\s*TEMPERATURE\s*[:=]\s*(.+)"],
        "equipment_name": [r"EQUIPMENT(?:\s*NAME)?\s*[:=]\s*(.+)"],
    }

    def __init__(self, llm_extractor=None) -> None:
        self.llm_extractor = llm_extractor

    def to_structured_fields(
        self,
        text: str,
        document_type: DocumentType,
    ) -> dict[str, str]:
        parsed = self._parse_with_rules(text)
        if parsed.get("tag_no"):
            return parsed
        if self.llm_extractor is not None:
            fallback = self.llm_extractor.to_structured_fields(text, document_type)
            return {**parsed, **fallback}
        return parsed

    def _parse_with_rules(self, text: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for field_name, patterns in self.FIELD_PATTERNS.items():
            value = self._find_first_match(text, patterns)
            if value:
                result[field_name] = value
        return result

    def _find_first_match(self, text: str, patterns: list[str]) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
