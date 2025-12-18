"""Value formatting utilities for scan results display."""


def format_value(value: float, unit: str) -> str:
    """
    Format a numeric value based on unit specification.

    Args:
        value: The numeric value to format
        unit: Unit specification ('float_2_dig', 'float_1_dig', '%', or empty)

    Returns:
        Formatted value string
    """
    match unit:
        case "float_2_dig":
            return f"({value:.2f})"
        case "float_1_dig":
            return f"{value:.1f}"
        case "%":
            return f"{value:.1f} %"
        case _:
            return str(value)
