"""Tests for gnuplot_style package."""

import os
import sys

# Add src directory to path to import gnuplot_style
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402

import gnuplot_style as gp  # noqa: E402


def test_import():
    """Test that the package can be imported."""
    assert gp.__version__ == "0.1.2"


def test_colors_constant():
    """Test that COLORS constant is accessible and correct."""
    assert len(gp.COLORS) == 8
    assert gp.COLORS[0] == "#9400D3"


def test_use_color():
    """Test applying color style."""
    gp.use("color")
    # Should not raise an exception


def test_use_shorthand():
    """Test shorthand style codes."""
    styles = ["c", "l", "m", "cl", "cm", "all"]
    for style in styles:
        gp.use(style)  # Should not raise


def test_invalid_style():
    """Test that invalid style raises ValueError."""
    with pytest.raises(ValueError, match="Unknown style"):
        gp.use("invalid")


def test_convenience_functions():
    """Test that convenience functions work."""
    gp.colors()
    gp.lines()
    gp.markers()
    gp.colors_lines()
    gp.colors_markers()
    gp.all()


def test_apply_pattern():
    """Test pattern application to bar charts."""
    fig, ax = plt.subplots()
    bars = ax.bar([1, 2, 3], [1, 2, 3])

    # Test valid patterns
    for i in range(8):
        gp.apply_pattern(bars, i)

    # Test invalid patterns (should not raise)
    gp.apply_pattern(bars, -1)
    gp.apply_pattern(bars, 10)
    gp.apply_pattern(bars, None)

    plt.close(fig)


def test_mplstyle_loading():
    """Test that mplstyle file is loaded."""
    # Reset first
    plt.rcdefaults()

    # Apply style
    gp.use()

    # Check that mplstyle is loaded by verifying specific settings
    assert plt.rcParams["font.family"] == ["sans-serif"]
    assert plt.rcParams["figure.figsize"] == [6.4, 4.8]
    assert plt.rcParams["figure.dpi"] == 150


def test_apply_style_to_existing_axes():
    """Test applying style to axes created before gp.use()."""
    # Create axes first
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Apply style after axes creation
    gp.use("cl")

    # Method 1: Apply to specific axes
    ax1.set_prop_cycle(plt.rcParams["axes.prop_cycle"])

    # Method 2: Let the second axes use default (won't have the style)
    # This demonstrates the difference

    x = np.linspace(0, 2 * np.pi, 50)

    # Plot on both axes
    for i in range(3):
        ax1.plot(x, np.sin(x + i * 0.5), linewidth=2, label=f"Line {i+1}")
        ax2.plot(x, np.sin(x + i * 0.5), linewidth=2, label=f"Line {i+1}")

    ax1.set_title("With prop_cycle applied")
    ax2.set_title("Without prop_cycle (default colors)")
    ax1.legend()
    ax2.legend()

    output_path = os.path.join(
        os.path.dirname(__file__), "test_prop_cycle_comparison.png"
    )
    plt.savefig(output_path, dpi=100)
    plt.close(fig)


def test_generate_reference_figures():
    """Generate reference figures for visual inspection."""
    # This test generates figures but doesn't assert anything
    # It's useful for manual inspection during development

    # Apply style first, then create plot
    gp.use("cl")

    # Simple test plot
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.linspace(0, 2 * np.pi, 50)

    for i in range(4):
        ax.plot(x, np.sin(x + i * 0.5), linewidth=2, label=f"Line {i+1}")

    ax.set_title("Test: Colors + Lines")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Save to same directory as this script
    output_path = os.path.join(os.path.dirname(__file__), "test_colors_lines.png")
    plt.savefig(output_path, dpi=100)
    plt.close()


def test_extended_cycle_mode():
    """Test extended cycle mode functionality."""
    # Test color+line extended mode (72 combinations)
    gp.use("cl", cycle_mode="extended")
    cycle = list(plt.rcParams["axes.prop_cycle"])
    assert len(cycle) == 72  # 8 colors × 9 lines

    # Test color+marker extended mode (136 combinations)
    gp.use("cm", cycle_mode="extended")
    cycle = list(plt.rcParams["axes.prop_cycle"])
    assert len(cycle) == 136  # 8 colors × 17 markers

    # Test that first 8 have the same marker (empty string)
    for i in range(8):
        assert cycle[i]["marker"] == gp.MARKERS[0]  # Empty string ""
    # Test that colors cycle within each marker group
    for i in range(8):
        assert cycle[i]["color"] == gp.COLORS[i]
        assert cycle[i + 8]["color"] == gp.COLORS[i]  # Colors repeat
        assert cycle[i + 8]["marker"] == gp.MARKERS[1]  # Different marker (.)


def test_skip_no_marker():
    """Test skip_no_marker functionality."""
    # Test with marker style
    gp.use("m", skip_no_marker=True)
    cycle = list(plt.rcParams["axes.prop_cycle"])
    assert len(cycle) == 16  # 17 markers - 1 (no symbol)
    assert cycle[0]["marker"] == gp.MARKERS[1]  # Should start with dot

    # Test with color+marker default mode
    gp.use("cm", skip_no_marker=True)
    cycle = list(plt.rcParams["axes.prop_cycle"])
    assert len(cycle) == 8
    assert cycle[0]["marker"] == gp.MARKERS[1]  # Should start with dot

    # Test with color+marker extended mode
    gp.use("cm", cycle_mode="extended", skip_no_marker=True)
    cycle = list(plt.rcParams["axes.prop_cycle"])
    assert len(cycle) == 128  # 8 colors × 16 markers (17 - 1)
    assert cycle[0]["marker"] == gp.MARKERS[1]  # Should start with dot

    # Test with all style
    gp.use("all", skip_no_marker=True)
    cycle = list(plt.rcParams["axes.prop_cycle"])
    assert len(cycle) == 16
    assert cycle[0]["marker"] == gp.MARKERS[1]  # Should start with dot


def test_default_vs_extended_visual():
    """Visual test comparing default vs extended cycle modes."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Cycle Mode Comparison: Default vs Extended", fontsize=14)

    x = np.linspace(0, 2 * np.pi, 30)
    n_lines = 20

    # Default color+line (top left)
    ax = axes[0, 0]
    gp.use("cl")  # default mode
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    ax.set_title("Color+Line Default (8 unique)")
    for i in range(n_lines):
        y = np.sin(x + i * 0.2) * (0.9 - i * 0.02)
        ax.plot(x, y, linewidth=2, label=f"{i+1}")
    ax.legend(ncol=4, fontsize=6)
    ax.grid(True, alpha=0.3)

    # Extended color+line (top right)
    ax = axes[0, 1]
    gp.use("cl", cycle_mode="extended")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    ax.set_title("Color+Line Extended (72 unique)")
    for i in range(n_lines):
        y = np.sin(x + i * 0.2) * (0.9 - i * 0.02)
        ax.plot(x, y, linewidth=2, label=f"{i+1}")
    ax.legend(ncol=4, fontsize=6)
    ax.grid(True, alpha=0.3)

    # Default color+marker (bottom left)
    ax = axes[1, 0]
    gp.use("cm")  # default mode
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    ax.set_title("Color+Marker Default (8 unique)")
    x_sparse = x[::3]
    for i in range(n_lines):
        y = np.sin(x_sparse + i * 0.2) * (0.9 - i * 0.02)
        ax.plot(x_sparse, y, linewidth=1, markersize=6, label=f"{i+1}")
    ax.legend(ncol=4, fontsize=6)
    ax.grid(True, alpha=0.3)

    # Extended color+marker (bottom right)
    ax = axes[1, 1]
    gp.use("cm", cycle_mode="extended")
    ax.set_prop_cycle(plt.rcParams["axes.prop_cycle"])
    ax.set_title("Color+Marker Extended (136 unique)")
    for i in range(n_lines):
        y = np.sin(x_sparse + i * 0.2) * (0.9 - i * 0.02)
        ax.plot(x_sparse, y, linewidth=1, markersize=6, label=f"{i+1}")
    ax.legend(ncol=4, fontsize=6)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "test_cycle_modes.png")
    plt.savefig(output_path, dpi=100)
    plt.close()


if __name__ == "__main__":
    # Run visual test when executed directly
    test_generate_reference_figures()
    test_apply_style_to_existing_axes()
    test_default_vs_extended_visual()
    print("Test figures saved:")
    print("  - test_colors_lines.png (Colors + Lines example)")
    print("  - test_prop_cycle_comparison.png (Comparison with/without prop_cycle)")
    print("  - test_cycle_modes.png (Default vs Extended cycle modes)")
