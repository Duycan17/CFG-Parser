"""Utility functions and helpers."""

from typing import Any


def sanitize_code_snippet(code: str, max_length: int = 100) -> str:
    """Sanitize and truncate code snippet for display."""
    code = code.strip()
    code = " ".join(code.split())
    if len(code) > max_length:
        return code[:max_length] + "..."
    return code


def generate_node_id(prefix: str, index: int) -> str:
    """Generate a unique node identifier."""
    return f"{prefix}_{index}"


def flatten_list(nested: list[Any]) -> list[Any]:
    """Flatten a nested list structure."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get an attribute from an object."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default
