#!/usr/bin/env python3
"""
Generate comprehensive reference figure for gnuplot_style.py
Creates a single reference image in multiple formats (PNG, PDF, SVG).
"""

import os
import sys

# Add src directory to path to import gnuplot_style
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

import matplotlib.gridspec as gridspec  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import gnuplot_style as gp  # noqa: E402


def create_reference():
    """Create comprehensive reference figure showing all gnuplot_style features."""

    # Create figure with proper layout
    fig = plt.figure(figsize=(20, 28))
    gs = gridspec.GridSpec(
        7, 3, height_ratios=[1, 1, 1, 1, 1, 1, 0.8], hspace=0.35, wspace=0.3
    )

    # Main title
    title_text = (
        "Gnuplot Style Reference - gnuplot_style.py\n"
        "(with integrated gnuplot.mplstyle)"
    )
    fig.suptitle(
        title_text,
        fontsize=20,
        fontweight="bold",
        y=0.985,
    )

    # Sample data
    x = np.linspace(0, 2 * np.pi, 100)  # Smooth lines, use markevery for markers

    # ============================================================================
    # Row 1: Line styles (without markers)
    # ============================================================================
    # Lines only (black, no markers)
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title('gp.use("l") - Lines Only', fontweight="bold", fontsize=14)
    gp.use("l")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    for i in range(6):
        y = np.sin(x + i * 0.5) * (0.8 - i * 0.15)
        ax.plot(x, y, linewidth=2, color="black", label=f"Data {i+1}")
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Lines + Colors (no markers)
    ax = fig.add_subplot(gs[0, 1])
    ax.set_title('gp.use("cl") - Lines + Colors', fontweight="bold", fontsize=14)
    gp.use("cl")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    for i in range(6):
        y = np.sin(x + i * 0.5) * (0.8 - i * 0.15)
        ax.plot(x, y, linewidth=2.5, label=f"Data {i+1}")
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Lines + Markers + Colors
    ax = fig.add_subplot(gs[0, 2])
    ax.set_title(
        'gp.use("all") - Lines + Markers + Colors', fontweight="bold", fontsize=14
    )
    gp.use("all")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    for i in range(6):
        y = np.sin(x + i * 0.5) * (0.8 - i * 0.15)
        ax.plot(x, y, linewidth=2, markersize=6, markevery=8, label=f"Data {i+1}")
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # ============================================================================
    # Row 2: Marker styles
    # ============================================================================
    # Markers only (black, no lines)
    ax = fig.add_subplot(gs[1, 0])
    ax.set_title('gp.use("m") - Markers Only', fontweight="bold", fontsize=14)
    gp.use("m")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    for i in range(6):
        y = np.sin(x + i * 0.5) * (0.8 - i * 0.15)
        ax.plot(
            x,
            y,
            linestyle="none",
            markersize=10,
            markevery=8,
            color="black",
            label=f"Data {i+1}",
        )
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Markers + Colors (with lines)
    ax = fig.add_subplot(gs[1, 1])
    ax.set_title('gp.use("cm") - Markers + Colors', fontweight="bold", fontsize=14)
    gp.use("cm")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    for i in range(6):
        y = np.sin(x + i * 0.5) * (0.8 - i * 0.15)
        ax.plot(x, y, linewidth=2, markersize=6, markevery=8, label=f"Data {i+1}")
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Colors only
    ax = fig.add_subplot(gs[1, 2])
    ax.set_title('gp.use("c") - Colors Only', fontweight="bold", fontsize=14)
    gp.use("c")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    for i in range(6):
        y = np.sin(x + i * 0.5) * (0.8 - i * 0.15)
        ax.plot(x, y, linewidth=2.5, label=f"Data {i+1}")
    ax.legend(fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # ============================================================================
    # Row 3: Colors and Line Styles
    # ============================================================================
    # Colors
    ax = fig.add_subplot(gs[2, 0])
    ax.set_title("Gnuplot Colors", fontsize=14, fontweight="bold")
    for i, color in enumerate(gp.COLORS):
        rect = mpatches.Rectangle(
            (0, i), 4, 0.8, facecolor=color, edgecolor="black", linewidth=2
        )
        ax.add_patch(rect)
        ax.text(4.2, i + 0.4, f"{i+1}: {color}", va="center", fontsize=10)
    ax.set_xlim(-0.5, 7)
    ax.set_ylim(-0.5, len(gp.COLORS))
    ax.axis("off")

    # Line Styles
    ax = fig.add_subplot(gs[2, 1])
    ax.set_title("Line Styles", fontsize=14, fontweight="bold")
    for i, linestyle in enumerate(gp.LINE_STYLES):
        y = len(gp.LINE_STYLES) - i - 1
        ax.plot([0, 5], [y, y], linestyle=linestyle, linewidth=3, color="black")
        ax.text(-0.2, y, f"{i+1}:", ha="right", va="center", fontsize=10)
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-0.5, len(gp.LINE_STYLES))
    ax.axis("off")

    # Markers
    ax = fig.add_subplot(gs[2, 2])
    ax.set_title("Markers (1-16)", fontsize=14, fontweight="bold")
    n_cols = 4
    n_rows = 4
    for i in range(16):
        row = i // n_cols
        col = i % n_cols
        x = col * 1.5 + 0.75
        y = n_rows - row - 0.5

        marker = gp.MARKERS[i]
        fillstyle = gp.FILL_STYLES[i]

        ax.plot(
            x,
            y,
            marker=marker,
            markersize=15,
            markeredgecolor="black",
            markerfacecolor="black" if fillstyle == "full" else "none",
            markeredgewidth=2,
            linestyle="none",
        )
        ax.text(x, y - 0.3, f"{i+1}", ha="center", fontsize=9)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # ============================================================================
    # Row 4: Pattern Fills
    # ============================================================================
    ax = fig.add_subplot(gs[3, :])
    ax.set_title("Pattern Fills for Bar Charts", fontsize=14, fontweight="bold")

    x = np.arange(len(gp.PATTERNS))
    heights = np.ones(len(gp.PATTERNS)) * 3
    bars = ax.bar(x, heights, width=0.8, edgecolor="black", linewidth=2)

    # Apply patterns using gp.apply_pattern
    for i, bar in enumerate(bars):
        gp.apply_pattern(bar, i)
        ax.text(
            i,
            -0.3,
            f"Pattern {i}",
            ha="center",
            va="top",
            fontweight="bold",
            fontsize=10,
        )
        pattern_desc = [
            "Empty",
            "Cross-hatch",
            "Dense cross",
            "Solid fill",
            "Diagonal left",
            "Diagonal right",
            "Wide left",
            "Wide right",
        ][i]
        ax.text(i, -0.6, pattern_desc, ha="center", va="top", fontsize=9)

    ax.set_ylim(-1, 3.5)
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in range(len(gp.PATTERNS))])
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylabel("Height")

    # ============================================================================
    # Row 5: Practical Examples
    # ============================================================================
    # Example 1: Scatter plot with Markers + Colors
    ax = fig.add_subplot(gs[4, 0])
    ax.set_title("Scatter Plot (Markers + Colors)", fontsize=12, fontweight="bold")
    gp.use("cm")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    np.random.seed(42)
    for i in range(6):
        x_scatter = np.random.normal(i * 0.8, 0.3, 20)
        y_scatter = np.random.normal(i * 0.5, 0.3, 20)
        # Use plot with linestyle='none' to get marker cycling
        ax.plot(
            x_scatter,
            y_scatter,
            linestyle="none",
            markersize=10,
            alpha=0.7,
            label=f"Group {i+1}",
        )
    ax.legend(ncol=2, fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Example 2: Scatter plot with Colors only
    ax = fig.add_subplot(gs[4, 1])
    ax.set_title("Scatter Plot (Colors Only)", fontsize=12, fontweight="bold")
    gp.use("c")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    np.random.seed(42)
    for i in range(6):
        x_scatter = np.random.normal(i * 0.8, 0.3, 20)
        y_scatter = np.random.normal(i * 0.5, 0.3, 20)
        # Use scatter to show color cycling without marker shape changes
        ax.scatter(x_scatter, y_scatter, s=60, alpha=0.7, label=f"Group {i+1}")
    ax.legend(ncol=2, fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Example 3: Grouped Bar Chart with Patterns
    ax = fig.add_subplot(gs[4, 2])
    ax.set_title("Grouped Bar Chart (Patterns)", fontsize=12, fontweight="bold")
    categories = ["Cat 1", "Cat 2", "Cat 3", "Cat 4"]
    x = np.arange(len(categories))
    width = 0.25
    np.random.seed(42)
    for i in range(3):
        values = np.random.randint(20, 60, len(categories))
        bars = ax.bar(
            x + i * width,
            values,
            width,
            edgecolor="black",
            linewidth=1.5,
            label=f"Group {i+1}",
        )
        # Apply different pattern to each group
        pattern_idx = [0, 1, 4][i]  # Use empty, cross-hatch, and diagonal
        for bar in bars:
            gp.apply_pattern(bar, pattern_idx)
    ax.set_xticks(x + width)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylabel("Value")

    # ============================================================================
    # Row 6: Bar Chart Examples
    # ============================================================================
    # Bar Chart with Colors
    ax = fig.add_subplot(gs[5, 0])
    ax.set_title("Bar Chart (Colors)", fontsize=12, fontweight="bold")
    gp.use("c")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    categories = ["A", "B", "C", "D", "E", "F"]
    values = [45, 38, 52, 41, 36, 48]
    # Plot each bar separately to get different colors
    for i, (cat, val) in enumerate(zip(categories, values)):
        ax.bar(cat, val, edgecolor="black", linewidth=1.5)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylabel("Value")

    # Bar Chart with Patterns
    ax = fig.add_subplot(gs[5, 1])
    ax.set_title("Bar Chart (Patterns)", fontsize=12, fontweight="bold")
    categories = ["A", "B", "C", "D", "E", "F"]
    values = [45, 38, 52, 41, 36, 48]
    bars = ax.bar(categories, values, edgecolor="black", linewidth=1.5)
    for i, bar in enumerate(bars):
        gp.apply_pattern(bar, i % 8)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylabel("Value")

    # Grouped Bar Chart with Colors
    ax = fig.add_subplot(gs[5, 2])
    ax.set_title("Grouped Bar Chart (Colors)", fontsize=12, fontweight="bold")
    gp.use("c")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    categories = ["Cat 1", "Cat 2", "Cat 3", "Cat 4"]
    x = np.arange(len(categories))
    width = 0.25
    for i in range(3):
        values = np.random.randint(20, 60, len(categories))
        ax.bar(
            x + i * width,
            values,
            width,
            edgecolor="black",
            linewidth=1.5,
            label=f"Group {i+1}",
        )
    ax.set_xticks(x + width)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylabel("Value")

    # ============================================================================
    # Bottom row: Usage examples
    # ============================================================================
    ax = fig.add_subplot(gs[6, :])
    ax.text(
        0.5,
        0.9,
        "Usage Examples",
        fontsize=16,
        fontweight="bold",
        ha="center",
        transform=ax.transAxes,
    )

    examples = [
        "import gnuplot_style as gp",
        "import matplotlib.pyplot as plt",
        "",
        "# Apply a style (automatically loads gnuplot.mplstyle)",
        "gp.use('cl')  # Colors + Lines",
        "gp.use('cm')  # Colors + Markers",
        "gp.use('all') # All features",
        "",
        "# Disable mplstyle if needed",
        "gp.use('c', apply_mplstyle=False)",
        "",
        "# Then plot normally",
        "plt.plot(x, y)",
        "",
        "# For bar patterns:",
        "bars = plt.bar(x, heights)",
        "gp.apply_pattern(bars, pattern_index)",
    ]

    example_text = "\n".join(examples)
    ax.text(
        0.05,
        0.75,
        example_text,
        fontsize=11,
        family="monospace",
        verticalalignment="top",
        transform=ax.transAxes,
    )

    # Available styles
    styles_text = """Available Styles:
  'c'   - Colors only
  'l'   - Lines only (black)
  'm'   - Markers only
  'cl'  - Colors + Lines
  'cm'  - Colors + Markers
  'all' - All combined

Convenience functions:
  gp.colors()
  gp.lines()
  gp.markers()
  gp.colors_lines()
  gp.colors_markers()
  gp.all()

Integrated gnuplot.mplstyle:
  Serif fonts (Computer Modern)
  Figure: 6.4x4.8, 300 DPI
  Ticks: gnuplot style
  Legend: white bg, black border
  No grid by default
  Error bars: no caps
  And much more..."""

    ax.text(
        0.55,
        0.75,
        styles_text,
        fontsize=11,
        verticalalignment="top",
        transform=ax.transAxes,
    )

    ax.axis("off")

    # Save in multiple formats
    plt.tight_layout()
    for fmt in ["png", "pdf", "svg"]:
        filename = os.path.join(
            os.path.dirname(__file__), f"gnuplot_style_reference.{fmt}"
        )
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"✓ Created: {filename}")

    plt.close()


if __name__ == "__main__":
    print("Generating gnuplot_style.py reference figure...")
    create_reference()
    print("\nReference generation complete!")
