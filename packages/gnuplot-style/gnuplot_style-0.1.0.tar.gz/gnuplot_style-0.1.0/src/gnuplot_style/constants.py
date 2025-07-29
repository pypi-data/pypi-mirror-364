"""Gnuplot style constants."""

# Gnuplot default colors
COLORS = [
    "#9400D3",  # Dark violet
    "#009E73",  # Teal/green
    "#56B4E9",  # Sky blue
    "#E69F00",  # Orange
    "#F0E442",  # Yellow
    "#0072B2",  # Dark blue
    "#E51E10",  # Red
    "#000000",  # Black
]

# Gnuplot line styles (dash patterns for line types 0-8)
LINE_STYLES = [
    "-",  # LT0: solid
    (0, (4, 2)),  # LT1: dashed
    (0, (2, 2)),  # LT2: short dashed
    (0, (6, 2, 2, 2)),  # LT3: dash-dot
    (0, (2, 2, 6, 2, 2, 2)),  # LT4: dash-dot-dash
    (0, (8, 4)),  # LT5: long dashed
    (0, (3, 3, 3, 3, 3, 12)),  # LT6: complex dash
    (0, (6, 6, 2, 6)),  # LT7: dash-dot variant
    (0, (4, 4, 4, 12)),  # LT8: dash with gap
]

# Gnuplot point types mapped to matplotlib markers (1-16 only)
MARKERS = [
    ".",  # 1: point
    "+",  # 2: plus
    "x",  # 3: cross
    "*",  # 4: star
    "s",  # 5: square (open)
    "s",  # 6: square (filled)
    "o",  # 7: circle (open)
    "o",  # 8: circle (filled)
    "^",  # 9: triangle up (open)
    "^",  # 10: triangle up (filled)
    "v",  # 11: triangle down (open)
    "v",  # 12: triangle down (filled)
    "D",  # 13: diamond (open)
    "D",  # 14: diamond (filled)
    "p",  # 15: pentagon (open)
    "p",  # 16: pentagon (filled)
]

# Filled point types
FILL_STYLES = [
    "full",
    "none",
    "none",
    "none",
    "none",
    "full",
    "none",
    "full",
    "none",
    "full",
    "none",
    "full",
    "none",
    "full",
    "none",
    "full",
]

# Gnuplot pattern fills for histograms
PATTERNS = [
    None,  # 0: Empty
    "x",  # 1: Cross-hatch
    "xx",  # 2: Dense cross-hatch
    "",  # 3: Solid fill
    "/",  # 4: Diagonal lines 45°
    "\\",  # 5: Diagonal lines -45°
    "//",  # 6: Diagonal lines 45° (wider)
    "\\\\",  # 7: Diagonal lines -45° (wider)
]

# Pattern fill styles (whether to fill with color or not)
PATTERN_FILL_STYLES = [
    "none",  # 0: Empty - no fill
    "none",  # 1: Cross-hatch - no fill
    "none",  # 2: Dense cross-hatch - no fill
    "full",  # 3: Solid fill - filled
    "none",  # 4: Diagonal lines 45° - no fill
    "none",  # 5: Diagonal lines -45° - no fill
    "none",  # 6: Diagonal lines 45° (wider) - no fill
    "none",  # 7: Diagonal lines -45° (wider) - no fill
]

# Style name mapping
STYLE_MAP = {
    "c": "color",
    "l": "line",
    "cl": "color+line",
    "cm": "color+marker",
    "m": "marker",
    "clm": "all",
}
