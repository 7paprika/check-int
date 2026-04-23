from check_int.adapters.structured_extractor import HybridStructuredExtractor
from check_int.domain.enums import DocumentType


class _FakeLlmExtractor:
    def to_structured_fields(self, text: str, document_type: DocumentType) -> dict[str, str]:
        return {
            "tag_no": "P-1201",
            "service": "Cooling Water",
            "material": "SS316",
        }


def test_hybrid_structured_extractor_parses_key_value_pairs_with_rules() -> None:
    extractor = HybridStructuredExtractor()

    result = extractor.to_structured_fields(
        "TAG NO: P-1201\nSERVICE: Cooling Water\nMATERIAL: SS316\nDESIGN PRESSURE: 10 BAR",
        DocumentType.PID,
    )

    assert result["tag_no"] == "P-1201"
    assert result["service"] == "Cooling Water"
    assert result["material"] == "SS316"
    assert result["design_pressure"] == "10 BAR"


def test_hybrid_structured_extractor_falls_back_to_llm_when_rules_find_no_tag() -> None:
    extractor = HybridStructuredExtractor(llm_extractor=_FakeLlmExtractor())

    result = extractor.to_structured_fields(
        "pump for cooling water service / ss316 construction",
        DocumentType.DATASHEET,
    )

    assert result["tag_no"] == "P-1201"
    assert result["service"] == "Cooling Water"
