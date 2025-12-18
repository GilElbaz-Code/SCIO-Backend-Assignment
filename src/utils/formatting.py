"""Value-formatting utilities for scan-result display."""

def _format_percent(value: float) -> str:
    """
    Format a percentage with up to three decimal places,
    stripping any insignificant trailing zeros.

    Examples
    --------
    10.512  -> "10.512 %"
    10.5    -> "10.5 %"
    10      -> "10 %"
    """
    rounded = f"{value:.3f}".rstrip("0").rstrip(".")
    return f"{rounded} %"


def format_value(value: float, unit: str) -> str:
    """
    Format a numeric value according to the widget-unit spec.

    Parameters
    ----------
    value : float
        The raw numeric value.
    unit : str
        Unit specifier – one of:
        - ``"float_2_dig"`` → two decimals, wrapped in parentheses.
        - ``"float_1_dig"`` → single decimal.
        - ``"%"``          → up to three decimals plus a percent sign.
        - anything else    → returned verbatim via ``str()``.

    Returns
    -------
    str
        Human-readable, correctly formatted string.
    """
    match unit:
        case "float_2_dig":
            return f"({value:.2f})"
        case "float_1_dig":
            return f"{value:.1f}"
        case "%":
            return _format_percent(value)
        case _:
            return str(value)
