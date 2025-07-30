"""
mplstyles-seaborn: Matplotlib style sheets based on seaborn-v0_8-dark theme

This package provides matplotlib style sheets that replicate the seaborn-v0.8-dark
theme with various combinations of palettes and contexts, allowing you to use 
seaborn-like styling without requiring seaborn as a dependency.

Available styles:
- seaborn-v0_8-darkgrid-dark-notebook (default)
- seaborn-v0_8-whitegrid-colorblind-talk
- seaborn-v0_8-dark-muted-poster
- And many more combinations across 5 styles, 6 palettes, and 4 contexts...

Usage:
    import matplotlib.pyplot as plt
    import mplstyles_seaborn
    
    # Use a specific style by name
    plt.style.use('seaborn-v0_8-whitegrid-colorblind-talk')
    
    # Or use the convenience function with all parameters
    mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')
    
    # Or use defaults for some parameters
    mplstyles_seaborn.use_style(palette='colorblind', context='talk')  # uses darkgrid
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Literal

__version__ = "0.1.0"

# Get the styles directory
_STYLES_DIR = Path(__file__).parent / "styles"

# Available options
STYLES = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
PALETTES = ['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep']
CONTEXTS = ['paper', 'notebook', 'talk', 'poster']

def list_available_styles():
    """List all available style combinations."""
    styles = []
    for style_file in _STYLES_DIR.glob("*.mplstyle"):
        styles.append(style_file.stem)
    return sorted(styles)

def use_style(
    style: Literal['darkgrid', 'whitegrid', 'dark', 'white', 'ticks'] = 'darkgrid',
    palette: Literal['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep'] = 'dark',
    context: Literal['paper', 'notebook', 'talk', 'poster'] = 'notebook'
):
    """
    Apply a seaborn-v0_8 style with specified style, palette and context.
    
    Parameters
    ----------
    style : str, default 'darkgrid'
        Style type to use. Options: 'darkgrid', 'whitegrid', 'dark', 'white', 'ticks'
    palette : str, default 'dark'
        Color palette to use. Options: 'dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep'
    context : str, default 'notebook' 
        Context scaling for elements. Options: 'paper', 'notebook', 'talk', 'poster'
        
    Examples
    --------
    >>> import mplstyles_seaborn
    >>> mplstyles_seaborn.use_style('whitegrid', 'colorblind', 'talk')
    >>> mplstyles_seaborn.use_style(palette='colorblind', context='talk')  # uses default darkgrid
    """
    if style not in STYLES:
        raise ValueError(f"style must be one of {STYLES}")
    if palette not in PALETTES:
        raise ValueError(f"palette must be one of {PALETTES}")
    if context not in CONTEXTS:
        raise ValueError(f"context must be one of {CONTEXTS}")
        
    style_name = f"seaborn-v0_8-{style}-{palette}-{context}"
    style_path = _STYLES_DIR / f"{style_name}.mplstyle"
    
    if not style_path.exists():
        raise FileNotFoundError(f"Style file not found: {style_path}")
        
    plt.style.use(str(style_path))

def register_styles():
    """Register all styles with matplotlib so they can be used by name."""
    import matplotlib.style as mplstyle
    
    for style_file in _STYLES_DIR.glob("*.mplstyle"):
        # Register with both full path and just the name
        mplstyle.library[style_file.stem] = str(style_file)

# Auto-register styles when the module is imported
register_styles()

__all__ = ['use_style', 'list_available_styles', 'register_styles', 'STYLES', 'PALETTES', 'CONTEXTS']
