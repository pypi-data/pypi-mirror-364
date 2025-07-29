"""Convenience API functions for gnuplot style."""

from .core import use


def colors() -> None:
    """Apply just gnuplot colors."""
    use("color")


def lines() -> None:
    """Apply just gnuplot line styles."""
    use("line")


def markers() -> None:
    """Apply just gnuplot markers."""
    use("marker")


def colors_lines() -> None:
    """Apply gnuplot colors and line styles."""
    use("color+line")


def colors_markers() -> None:
    """Apply gnuplot colors and markers."""
    use("color+marker")


def all() -> None:
    """Apply all gnuplot styles: colors, lines, and markers."""
    use("all")
