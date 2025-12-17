from typing import Any


def format_value(value: float, unit: str) -> str:
    """
    Format a numeric value based on unit specification.

    Args:
        value: The numeric value to format
        unit: Unit specification ('float_2_dig', 'float_1_dig', '%', or empty)

    Returns:
        Formatted value string
    """
    if unit == "float_2_dig":
        return f"{value:.2f}"
    elif unit == "float_1_dig":
        return f"{value:.1f}"
    elif unit == "%":
        return f"{value} %"
    else:
        return str(value)

