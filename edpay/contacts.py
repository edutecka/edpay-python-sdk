"""Phone number normalization and validation helpers."""

from typing import Any, Dict, List, Optional, Tuple


def _parse(value: str, options: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    config = options or {}
    country_code = str(config.get("country_calling_code", "258"))
    if country_code.startswith("+"):
        country_code = country_code[1:]
    national_length = int(config.get("national_length", 9))
    if not country_code.isascii() or not country_code.isdigit() or not country_code or country_code.startswith("0") or len(country_code) > 3:
        raise ValueError("country_calling_code must contain 1 to 3 digits and cannot start with 0.")
    if national_length < 1 or len(country_code) + national_length > 15:
        raise ValueError("national_length must fit within the E.164 limit of 15 digits.")
    if not isinstance(value, str):
        raise TypeError("Phone number must be a string.")
    raw = value.strip()
    if not raw or any(char not in "+0123456789 ().-" for char in raw):
        raise ValueError("Phone number contains unsupported characters.")
    if raw.count("(") != raw.count(")"):
        raise ValueError("Phone number has unbalanced parentheses.")
    digits = "".join(char for char in raw if char.isdigit())
    international = raw.startswith("+")
    if digits.startswith("00"):
        digits, international = digits[2:], True
    if not international and digits.startswith(country_code) and len(digits) > national_length:
        international = True
    if international:
        if not digits.startswith(country_code):
            raise ValueError("Phone number does not use the configured country calling code.")
        digits = digits[len(country_code):]
    if len(digits) != national_length:
        raise ValueError("Phone number does not match the configured national length.")
    prefixes = config.get("national_prefixes", [])
    if not isinstance(prefixes, (list, tuple)) or any(
        not isinstance(prefix, str) or not prefix.isascii() or not prefix.isdigit()
        for prefix in prefixes
    ):
        raise ValueError("national_prefixes must contain non-empty digit strings.")
    if prefixes and not any(digits.startswith(prefix) for prefix in prefixes):
        raise ValueError("Phone number does not match the configured national prefixes.")
    return country_code, digits


def normalize_phone_number(value: str, *, country_calling_code: str = "258", national_length: int = 9,
                           national_prefixes: Optional[List[str]] = None, output: str = "international") -> str:
    country, national = _parse(value, {"country_calling_code": country_calling_code,
                                       "national_length": national_length,
                                       "national_prefixes": national_prefixes or []})
    if output not in ("international", "country-code", "national"):
        raise ValueError("output must be 'international', 'country-code', or 'national'.")
    if output == "national":
        return national
    return (f"+{country}" if output == "international" else country) + national


def phone_number_options_for_method(method: str) -> Optional[Dict[str, Any]]:
    """Return known phone rules; None means non-phone or unknown method."""
    key = method.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    if key == "emola":
        return {"country_calling_code": "258", "national_length": 9, "national_prefixes": ["86", "87"], "output": "national"}
    if key == "mpesa":
        return {"country_calling_code": "258", "national_length": 9, "national_prefixes": ["84", "85"], "output": "country-code"}
    return None


def add_country_prefix(value: str, **options: Any) -> str:
    options["output"] = "international"
    return normalize_phone_number(value, **options)


def remove_country_prefix(value: str, **options: Any) -> str:
    options["output"] = "national"
    return normalize_phone_number(value, **options)


def format_phone_number(value: str, *, country_calling_code: str = "258", national_length: int = 9,
                        national_prefixes: Optional[List[str]] = None, group_sizes: Optional[List[int]] = None) -> str:
    country, national = _parse(value, {"country_calling_code": country_calling_code,
                                       "national_length": national_length,
                                       "national_prefixes": national_prefixes or []})
    groups = group_sizes or ([2, 3, 4] if country == "258" and len(national) == 9 else [len(national)])
    parts, offset = [], 0
    for size in groups:
        if not isinstance(size, int) or isinstance(size, bool) or size < 1:
            raise ValueError("group_sizes must contain positive integers.")
        if offset >= len(national):
            break
        parts.append(national[offset:offset + size])
        offset += size
    if offset < len(national):
        parts.append(national[offset:])
    return f"+{country} {' '.join(parts)}"


def validate_phone_number(value: str, **options: Any) -> bool:
    try:
        _parse(value, {key: item for key, item in options.items() if key != "output" and key != "group_sizes"})
        return options.get("output", "international") in ("international", "country-code", "national")
    except (TypeError, ValueError):
        return False
