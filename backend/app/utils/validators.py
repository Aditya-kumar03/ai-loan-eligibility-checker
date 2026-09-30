from typing import Optional

def sanitize_string(val: Optional[str], max_len: int = 100) -> str:
    if not val:
        return ""
    # Strip potential control chars or script tags
    cleaned = "".join(ch for ch in str(val) if ch.isprintable())
    return cleaned.strip()[:max_len]

def validate_positive_number(val: float, field_name: str, allow_zero: bool = True) -> float:
    if allow_zero and val < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0.")
    if not allow_zero and val <= 0:
        raise ValueError(f"{field_name} must be strictly greater than 0.")
    return float(val)
