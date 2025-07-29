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
    assert gp.__version__ == "0.1.0"


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
    original_font = plt.rcParams["font.family"]

    # Apply style
    gp.use()

    # Check that font changed (mplstyle sets serif)
    assert plt.rcParams["font.family"] != original_font


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


if __name__ == "__main__":
    # Run visual test when executed directly
    test_generate_reference_figures()
    test_apply_style_to_existing_axes()
    print("Test figures saved:")
    print("  - test_colors_lines.png (Colors + Lines example)")
    print("  - test_prop_cycle_comparison.png (Comparison with/without prop_cycle)")
