"""Convenience API functions for gnuplot style."""

from .core import use


def colors() -> None:
    """Apply just gnuplot colors."""
    use("color")


def lines() -> None:
    """Apply just gnuplot line styles."""
    use("line")


def markers(skip_no_marker: bool = False) -> None:
    """Apply just gnuplot markers.

    Parameters
    ----------
    skip_no_marker : bool, optional
        Whether to skip marker index 0 (no symbol) for scatter plots
    """
    use("marker", skip_no_marker=skip_no_marker)


def colors_lines(cycle_mode: str = "default") -> None:
    """Apply gnuplot colors and line styles.

    Parameters
    ----------
    cycle_mode : str, optional
        'default' for 8 combinations, 'extended' for 72 combinations
    """
    use("color+line", cycle_mode=cycle_mode)


def colors_markers(cycle_mode: str = "default", skip_no_marker: bool = False) -> None:
    """Apply gnuplot colors and markers.

    Parameters
    ----------
    cycle_mode : str, optional
        'default' for 8 combinations, 'extended' for 136 combinations
        (128 if skip_no_marker)
    skip_no_marker : bool, optional
        Whether to skip marker index 0 (no symbol) for scatter plots
    """
    use("color+marker", cycle_mode=cycle_mode, skip_no_marker=skip_no_marker)


def all(cycle_mode: str = "default", skip_no_marker: bool = False) -> None:
    """Apply all gnuplot styles: colors, lines, and markers.

    Parameters
    ----------
    cycle_mode : str, optional
        'default' for 16 combinations, 'extended' for 1224 combinations (8 × 9 × 17)
        or 1152 if skip_no_marker (8 × 9 × 16)
    skip_no_marker : bool, optional
        Whether to skip marker index 0 (no symbol) for scatter plots
    """
    use("all", cycle_mode=cycle_mode, skip_no_marker=skip_no_marker)
