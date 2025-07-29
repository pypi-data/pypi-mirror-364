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


def use(
    style: str = "color",
    apply_mplstyle: bool = True,
    cycle_mode: str = "default",
    skip_no_marker: bool = False,
) -> None:
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
    cycle_mode : str, optional
        Cycling mode for styles (default: 'default'):
        - 'default': Standard cycling (8 for most, 16 for 'all')
        - 'extended': Extended cycling for more combinations
          - 'cl': 72 combinations (8 colors × 9 lines)
          - 'cm': 136 combinations (8 colors × 17 markers)
          - 'all': 1224 combinations (8 colors × 9 lines × 17 markers)
                   or 1152 if skip_no_marker (8 × 9 × 16)
    skip_no_marker : bool, optional
        Whether to skip marker index 0 (no symbol) for scatter plots (default: False)

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
        if skip_no_marker:
            # Skip the first marker (no symbol)
            markers_to_use = MARKERS[1:]
            fills_to_use = FILL_STYLES[1:]
        else:
            markers_to_use = MARKERS
            fills_to_use = FILL_STYLES

        plt.rc(
            "axes",
            prop_cycle=cycler(
                marker=markers_to_use,
                fillstyle=fills_to_use,
                linestyle=["none"] * len(markers_to_use),
            ),
        )

    elif style == "color+line":
        # Create paired colors and lines
        if cycle_mode == "extended":
            # Extended mode: cycle through all combinations (8 colors × 9 lines = 72)
            colors = []
            lines = []
            for line_idx in range(len(LINE_STYLES)):
                for color_idx in range(len(COLORS)):
                    colors.append(COLORS[color_idx])
                    lines.append(LINE_STYLES[line_idx])
        else:
            # Default: element-wise pairing (8 combinations)
            colors = []
            lines = []
            for i in range(8):
                colors.append(COLORS[i % len(COLORS)])
                lines.append(LINE_STYLES[i % len(LINE_STYLES)])
        plt.rc("axes", prop_cycle=cycler(color=colors, linestyle=lines))

    elif style == "color+marker":
        # Create paired colors and markers
        if cycle_mode == "extended":
            # Extended mode: cycle through all combinations
            # (8 colors × 17 markers = 136, or 8 × 16 = 128 if skipping no marker)
            colors = []
            markers = []
            fills = []
            start_idx = 1 if skip_no_marker else 0
            for marker_idx in range(start_idx, len(MARKERS)):
                for color_idx in range(len(COLORS)):
                    colors.append(COLORS[color_idx])
                    markers.append(MARKERS[marker_idx])
                    fills.append(FILL_STYLES[marker_idx])
        else:
            # Default: element-wise pairing (8 combinations)
            colors = []
            markers = []
            fills = []
            start_idx = 1 if skip_no_marker else 0
            for i in range(8):
                colors.append(COLORS[i % len(COLORS)])
                marker_idx = (i + start_idx) % len(MARKERS)
                markers.append(MARKERS[marker_idx])
                fills.append(FILL_STYLES[marker_idx])
        plt.rc("axes", prop_cycle=cycler(color=colors, marker=markers, fillstyle=fills))

    elif style == "all":
        # All three combined
        colors = []
        lines = []
        markers = []
        fills = []

        if cycle_mode == "extended":
            # Extended mode: cycle through all combinations
            # (8 colors × 9 lines × 17 markers = 1224
            # or 8 × 9 × 16 = 1152 if skipping no marker)
            start_idx = 1 if skip_no_marker else 0
            for marker_idx in range(start_idx, len(MARKERS)):
                for line_idx in range(len(LINE_STYLES)):
                    for color_idx in range(len(COLORS)):
                        colors.append(COLORS[color_idx])
                        lines.append(LINE_STYLES[line_idx])
                        markers.append(MARKERS[marker_idx])
                        fills.append(FILL_STYLES[marker_idx])
        else:
            # Default: use 16 unique combinations
            # First 8: colors 1-8 with markers 0-7 (or 1-8 if skipping no marker)
            # Next 8: colors 1-8 with markers 8-15 (or 9-16 if skipping no marker)
            start_idx = 1 if skip_no_marker else 0
            for i in range(16):
                color_idx = i % 8
                line_idx = i % len(LINE_STYLES)
                marker_idx = (i + start_idx) % len(MARKERS)

                colors.append(COLORS[color_idx])
                lines.append(LINE_STYLES[line_idx])
                markers.append(MARKERS[marker_idx])
                fills.append(FILL_STYLES[marker_idx])

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
