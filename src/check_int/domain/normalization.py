def normalize_field_value(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.strip().split()).lower()
    if not normalized:
        return None

    return normalized