"""Gnuplot style for matplotlib.

Simple and working implementation of gnuplot aesthetics for matplotlib.

Usage:
    import gnuplot_style as gp
    gp.use()  # Apply gnuplot colors (default)
    gp.use('cl')  # Apply colors + lines
"""

from .api import all, colors, colors_lines, colors_markers, lines, markers
from .constants import (
    COLORS,
    FILL_STYLES,
    LINE_STYLES,
    MARKERS,
    PATTERN_FILL_STYLES,
    PATTERNS,
)
from .core import apply_pattern, use

__version__ = "0.1.1"

__all__ = [
    # Main functions
    "use",
    "apply_pattern",
    # Convenience functions
    "colors",
    "lines",
    "markers",
    "colors_lines",
    "colors_markers",
    "all",
    # Constants (for advanced users)
    "COLORS",
    "LINE_STYLES",
    "MARKERS",
    "FILL_STYLES",
    "PATTERNS",
    "PATTERN_FILL_STYLES",
]
