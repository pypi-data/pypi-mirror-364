import os
import sys
import ctypes

def _enable_windows_ansi():
    """
    Enables ANSI escape sequence support on Windows terminals.

    On Windows, ANSI codes are not enabled by default in CMD or PowerShell.
    This function uses ctypes to activate virtual terminal processing so that
    ANSI sequences (for colors, styles, etc.) work correctly.
    """
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
        kernel32.SetConsoleMode(handle, 7)   # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

# Automatically enable ANSI sequences if running on Windows
_enable_windows_ansi()


class AnsiCodes:
    """
    Base class for ANSI escape code formatting.

    Attributes:
        RESET (str): ANSI sequence to reset formatting for this type (e.g., text or background).

    Methods:
        __getattr__(name): Returns the ANSI escape sequence for a given attribute name.
        _code_map(): Abstract method to be implemented by subclasses with specific ANSI mappings.
    """

    def __init__(self, prefix: str):
        """
        Initializes the AnsiCodes instance.

        Args:
            prefix (str): Prefix used in escape code (e.g., '' for text, '10' for background).
        """
        self._prefix = prefix
        self.RESET = f'\033[{prefix}0m'  # General reset for this group

    def __getattr__(self, name: str) -> str:
        """
        Dynamically gets the ANSI escape code for a given color or style name.

        Args:
            name (str): The name of the color/style (e.g., 'RED', 'LIGHTBLUE').

        Returns:
            str: The ANSI escape code corresponding to the name.

        Raises:
            AttributeError: If the name is not in the color map.
        """
        code = self._code_map().get(name.upper())
        if code is None:
            raise AttributeError(f"{name} is not a valid ANSI code")
        return f'\033[{self._prefix}{code}m'

    def _code_map(self) -> dict:
        """
        Abstract method to be overridden in subclasses.

        Returns:
            dict: Mapping of names to ANSI code numbers.
        """
        return {}


class TextColor(AnsiCodes):
    """
    ANSI codes for text (foreground) colors.
    Inherits from AnsiCodes.
    """

    def _code_map(self):
        return {
            'BLACK': 30,
            'RED': 31,
            'GREEN': 32,
            'YELLOW': 33,
            'BLUE': 34,
            'MAGENTA': 35,
            'CYAN': 36,
            'WHITE': 37,
            'RESET': 0,
            'LIGHTBLACK': 90,
            'LIGHTRED': 91,
            'LIGHTGREEN': 92,
            'LIGHTYELLOW': 93,
            'LIGHTBLUE': 94,
            'LIGHTMAGENTA': 95,
            'LIGHTCYAN': 96,
            'LIGHTWHITE': 97,
        }


class BgColor(AnsiCodes):
    """
    ANSI codes for background colors.
    Inherits from AnsiCodes.
    """

    def _code_map(self):
        return {
            'BLACK': 40,
            'RED': 41,
            'GREEN': 42,
            'YELLOW': 43,
            'BLUE': 44,
            'MAGENTA': 45,
            'CYAN': 46,
            'WHITE': 47,
            'RESET': 0,
            'LIGHTBLACK': 100,
            'LIGHTRED': 101,
            'LIGHTGREEN': 102,
            'LIGHTYELLOW': 103,
            'LIGHTBLUE': 104,
            'LIGHTMAGENTA': 105,
            'LIGHTCYAN': 106,
            'LIGHTWHITE': 107,
        }


class Style:
    """
    ANSI codes for text styling (bold, underline, invert, etc.).

    These are static values, not dynamically generated.
    """

    RESET_ALL = '\033[0m'       # Resets all attributes (color and style)
    BOLD = '\033[1m'          # Bold or bright text
    DIM = '\033[2m'             # Dim text (faint)
    NORMAL = '\033[22m'         # Normal intensity
    UNDERLINE = '\033[4m'       # Underlined text
    NO_UNDERLINE = '\033[24m'   # Cancel underline
    INVERT = '\033[7m'          # Inverted foreground/background
    NO_INVERT = '\033[27m'      # Cancel invert


# Exported API
Text = TextColor('')    # Foreground color codes
Bg = BgColor('')        # Background color codes
Style = Style()         # Text styles
