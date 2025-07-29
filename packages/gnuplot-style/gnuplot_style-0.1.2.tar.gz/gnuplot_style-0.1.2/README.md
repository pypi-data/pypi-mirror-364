# gnuplot-style

[![PyPI version](https://badge.fury.io/py/gnuplot-style.svg)](https://badge.fury.io/py/gnuplot-style)
[![Python versions](https://img.shields.io/pypi/pyversions/gnuplot-style.svg)](https://pypi.org/project/gnuplot-style/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python package that provides gnuplot-style aesthetics for matplotlib plots.

## Features

- Easy-to-use API for applying gnuplot styles to matplotlib
- Support for gnuplot's default colors, line styles, markers, and patterns
- Modular design allowing selective application of styles
- Compatible with matplotlib's style system
- Includes pattern fills for histograms and bar charts
- Smart cycling: 16 unique combinations when using all styles together

## Installation

```bash
pip install gnuplot-style
```

## Quick Start

```python
import matplotlib.pyplot as plt
import numpy as np
import gnuplot_style as gp

# Apply gnuplot aesthetics BEFORE creating figures
gp.use()  # Default: colors only

# Create your plots as usual
x = np.linspace(0, 2*np.pi, 100)
for i in range(4):
    plt.plot(x, np.sin(x + i*0.5), label=f'Series {i+1}')

plt.legend()
plt.show()
```

### Note on Axes Created Before Style Application

If you create axes before calling `gp.use()`, you need to explicitly apply the style:

```python
# If axes already exist
fig, ax = plt.subplots()

# Apply style
gp.use('cl')

# Apply the prop_cycle to existing axes
ax.set_prop_cycle(plt.rcParams['axes.prop_cycle'])

# Now plot with the new style
ax.plot(x, y)
```

## Style Options

The package provides several style combinations:

```python
# Individual components
gp.use('color')    # or 'c' - Just colors (default)
gp.use('line')     # or 'l' - Just line styles
gp.use('marker')   # or 'm' - Just markers

# Combinations
gp.use('color+line')    # or 'cl' - Colors + line styles
gp.use('color+marker')  # or 'cm' - Colors + markers
gp.use('all')          # or 'clm' - Everything combined
```

### Convenience Functions

```python
gp.colors()         # Apply colors only
gp.lines()          # Apply line styles only
gp.markers()        # Apply markers only
gp.colors_lines()   # Apply colors + lines
gp.colors_markers() # Apply colors + markers
gp.all()           # Apply all styles
```

## Pattern Fills

Apply gnuplot-style patterns to bar charts:

```python
# Create a bar chart
bars = plt.bar(['A', 'B', 'C'], [1, 2, 3])

# Apply pattern (0-7)
gp.apply_pattern(bars, pattern=1)  # Cross-hatch pattern
```

Available patterns:
- 0: Empty (no fill)
- 1: Cross-hatch
- 2: Dense cross-hatch
- 3: Solid fill
- 4: Diagonal lines (45°)
- 5: Diagonal lines (-45°)
- 6: Wide diagonal lines (45°)
- 7: Wide diagonal lines (-45°)

## Style Cycling

When you have more than 8 datasets:

### Default Mode
- **Colors only** (`'c'`): Cycles through 8 colors
- **Colors + Lines** (`'cl'`): Cycles through 8 combinations
- **Colors + Markers** (`'cm'`): Cycles through 8 combinations
- **All styles** (`'all'`): Cycles through **16 unique combinations**
  - First 8: Colors 1-8 with markers 1-8
  - Next 8: Colors 1-8 with markers 9-16

### Extended Mode (NEW!)
For even more unique combinations, use `cycle_mode='extended'`:

```python
# 72 unique combinations (8 colors × 9 line styles)
gp.use('cl', cycle_mode='extended')

# 136 unique combinations (8 colors × 17 markers)
gp.use('cm', cycle_mode='extended')

# Also works with convenience functions
gp.colors_lines(cycle_mode='extended')
gp.colors_markers(cycle_mode='extended')
```

Extended mode cycles through all color combinations for each line/marker style before moving to the next, providing maximum visual distinction for complex plots.

### Scatter Plots (NEW!)
For scatter plots where line styles are not used, you can skip marker index 0 (no symbol) to ensure all data points are visible:

```python
# Skip the "no symbol" marker for scatter plots
gp.use('cm', skip_no_marker=True)  # Starts from marker 1 (dot)
gp.use('m', skip_no_marker=True)   # Markers only, no invisible first marker

# Works with extended mode too
gp.use('cm', cycle_mode='extended', skip_no_marker=True)

# Then create scatter plots where all datasets are visible
for i in range(8):
    x = np.random.normal(i, 0.3, 50)
    y = np.random.normal(i, 0.3, 50)
    plt.plot(x, y, linestyle='none', markersize=8)
```

Without `skip_no_marker=True`, the first dataset would be invisible because gnuplot's marker 0 is "no symbol".

#### Important Note on Scatter vs Plot

In matplotlib, `scatter()` and `plot()` handle markers differently:

- **`plot()`** automatically uses markers from the prop_cycle
- **`scatter()`** does NOT automatically use markers from the prop_cycle

For scatter-like visualizations with automatic marker cycling from gnuplot styles:

```python
# ✅ Recommended: Use plot() with linestyle='none'
gp.use('cm', skip_no_marker=True)  # Apply style BEFORE creating figures

# Create figure AFTER applying style
fig, ax = plt.subplots()
for i in range(8):
    x = np.random.normal(i, 0.3, 50)
    y = np.random.normal(i, 0.3, 50)
    plt.plot(x, y, linestyle='none', markersize=8)  # Markers cycle automatically

# ❌ Not recommended: scatter() requires manual marker specification
# The markers from gnuplot style won't be applied automatically
for i in range(8):
    plt.scatter(x, y)  # Will use default circular markers only
```

If you must use `scatter()`, you need to manually extract and apply markers from the prop_cycle.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/vectorsss/gnuplot-style.git
cd gnuplot-style

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gnuplot_style

# Generate reference figures
python tests/test_reference_gnuplot_style.py
```

### Code Formatting

The project uses pre-commit hooks to ensure code quality:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Or let them run automatically on commit
git commit -m "Your message"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality (`pytest && pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Releasing (For Maintainers)

The package is automatically published to PyPI when a GitHub release is created.

### Setup (one-time)

1. Create PyPI API tokens:
   - Go to https://pypi.org/manage/account/token/
   - Create a token for this project
   - Add it as `PYPI_API_TOKEN` in GitHub repository secrets

2. Create TestPyPI API token (optional):
   - Go to https://test.pypi.org/manage/account/token/
   - Create a token for this project
   - Add it as `TEST_PYPI_API_TOKEN` in GitHub repository secrets

### Release Process

1. Update version in `src/gnuplot_style/__init__.py`
2. Create a GitHub release:
   - For pre-releases: Check "Set as pre-release" (publishes to TestPyPI)
   - For production releases: Leave unchecked (publishes to PyPI)

## Acknowledgments

- Inspired by the aesthetic of gnuplot's default terminal
- Built on top of matplotlib's excellent style system
