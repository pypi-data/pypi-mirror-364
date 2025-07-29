"""Core functionality for gnuplot style."""

import os
from typing import Any, List, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

from .constants import (
    COLORS,
    FILL_STYLES,
    LINE_STYLES,
    MARKERS,
    PATTERN_FILL_STYLES,
    PATTERNS,
    STYLE_MAP,
)


def use(style: str = "color", apply_mplstyle: bool = True) -> None:
    """Apply gnuplot style with a single command.

    Parameters
    ----------
    style : str
        Style to apply:
        - 'color' or 'c': Just colors (default)
        - 'line' or 'l': Just line styles
        - 'marker' or 'm': Just markers
        - 'color+line' or 'cl': Colors with line styles
        - 'color+marker' or 'cm': Colors with markers
        - 'all' or 'clm': Colors, lines, and markers
    apply_mplstyle : bool, optional
        Whether to apply gnuplot.mplstyle settings (default: True)

    Raises
    ------
    ValueError
        If an unknown style is provided.
    """
    # Reset to defaults first
    mpl.rcdefaults()

    # Apply gnuplot.mplstyle if requested and available
    if apply_mplstyle:
        # Look for gnuplot.mplstyle in the same directory as this module
        style_path = os.path.join(os.path.dirname(__file__), "gnuplot.mplstyle")
        if os.path.exists(style_path):
            plt.style.use(style_path)

    # Normalize style name
    style = STYLE_MAP.get(style, style)

    # Build the prop_cycle based on style
    if style == "color":
        # Just colors
        plt.rc("axes", prop_cycle=cycler("color", COLORS))

    elif style == "line":
        # Just line styles (keep default colors)
        plt.rc("axes", prop_cycle=cycler("linestyle", LINE_STYLES))

    elif style == "marker":
        # Just markers - no connecting lines, pair element-wise
        plt.rc(
            "axes",
            prop_cycle=cycler(
                marker=MARKERS,
                fillstyle=FILL_STYLES,
                linestyle=["none"] * len(MARKERS),
            ),
        )

    elif style == "color+line":
        # Create paired colors and lines element-wise
        colors = []
        lines = []
        for i in range(8):
            colors.append(COLORS[i % len(COLORS)])
            lines.append(LINE_STYLES[i % len(LINE_STYLES)])
        plt.rc("axes", prop_cycle=cycler(color=colors, linestyle=lines))

    elif style == "color+marker":
        # Create paired colors and markers element-wise
        colors = []
        markers = []
        fills = []
        for i in range(8):
            colors.append(COLORS[i % len(COLORS)])
            markers.append(MARKERS[i % len(MARKERS)])
            fills.append(FILL_STYLES[i % len(FILL_STYLES)])
        plt.rc("axes", prop_cycle=cycler(color=colors, marker=markers, fillstyle=fills))

    elif style == "all":
        # All three combined element-wise
        colors = []
        lines = []
        markers = []
        fills = []
        for i in range(8):
            colors.append(COLORS[i % len(COLORS)])
            lines.append(LINE_STYLES[i % len(LINE_STYLES)])
            markers.append(MARKERS[i % len(MARKERS)])
            fills.append(FILL_STYLES[i % len(FILL_STYLES)])
        plt.rc(
            "axes",
            prop_cycle=cycler(
                color=colors, linestyle=lines, marker=markers, fillstyle=fills
            ),
        )

    else:
        raise ValueError(
            f"Unknown style: {style}. Use 'c', 'l', 'm', 'cl', 'cm', or 'all'"
        )


def apply_pattern(
    bars: Union[Any, List[Any]], pattern: int, color: str = "black"
) -> None:
    """Apply gnuplot-style pattern fills to existing bars.

    Parameters
    ----------
    bars : BarContainer or list of patches
        The bars to apply patterns to
    pattern : int
        Pattern index (0-7) for gnuplot pattern fills
    color : str, optional
        Color to use for solid fills (pattern 3), default is 'black'
    """
    if pattern is None or pattern < 0 or pattern >= len(PATTERNS):
        return

    fillstyle = PATTERN_FILL_STYLES[pattern]
    hatch = PATTERNS[pattern]

    # Handle single bar or container
    if hasattr(bars, "patches"):
        patches = bars.patches
    elif hasattr(bars, "__iter__"):
        patches = bars
    else:
        patches = [bars]

    for patch in patches:
        if fillstyle == "none":
            patch.set_facecolor("none")
        else:  # fillstyle == 'full'
            patch.set_facecolor(color)

        if hatch is not None:
            patch.set_hatch(hatch)
