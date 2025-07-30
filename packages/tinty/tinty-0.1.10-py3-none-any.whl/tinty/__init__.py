"""
Colorize - A Python library for terminal text colorization and highlighting.

This library provides ANSI color code functionality for Python strings,
similar to the Ruby colorize gem.

Enhanced API for production use:
    from tinty import colored, C, ColorString

    # Fluent chaining
    colored("hello").red().bold()

    # Operator chaining
    colored("world") | BLUE | UNDERLINE

    # Global convenience object
    C.red("hello")
    C("hello").red().bold()

Legacy API (still supported):
    from tinty import Colorize, ColorizedString

    colorizer = Colorize()
    colored_text = colorizer.colorize("hello", RED)
"""

# Enhanced production-safe API (recommended)
# Legacy API (backward compatibility)
# Note: string_extensions module removed - use enhanced API or core classes directly
from importlib.metadata import version

__version__ = version("tinty")
from .color_codes import ColorCode, ColorManager, color_manager
from .colors import *  # noqa: F403

# Export enhanced API as primary interface
from .colors import __all__ as _colors_all
from .enhanced import (
    C,
    ColorContext,
    ColorString,
    colored,
    txt,
)
from .tinty import Colorize, ColorizedString, colorize

__all__ = [
    "C",
    "ColorCode",
    "ColorContext",
    "ColorManager",
    "ColorString",
    "Colorize",
    "ColorizedString",
    "__version__",
    "color_manager",
    "colored",
    "colorize",
    "txt",
]
__all__.extend(_colors_all)
