def infer_tag_from_text(text: str) -> str | None:
    text_lower = text.lower()

    if "hr" in text_lower or "human resource" in text_lower:
        return "HR"

    if "finance" in text_lower or "accounts" in text_lower:
        return "FINANCE"

    if "legal" in text_lower:
        return "LEGAL"

    return None
