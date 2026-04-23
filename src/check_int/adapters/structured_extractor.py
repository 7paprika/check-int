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