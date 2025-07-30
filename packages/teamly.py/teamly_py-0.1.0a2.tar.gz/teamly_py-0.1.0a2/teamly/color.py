'''
MIT License

Copyright (c) 2025 Fatih Kuloglu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import re
import random
from typing import Tuple

__all__ = ['Color']

class Color:
    """
    Represents a 24-bit RGB color.

    The color is internally stored as an integer between 0x000000 and 0xFFFFFF.
    This class provides utility methods for converting between integer, hex,
    RGB tuples, and string representations.

    Example:
        c = Color(0xFF0000)
        print(c.to_rgb())       # (255, 0, 0)
        print(str(c))           # <Color #FF0000>
    """

    __slots__ = ('value')

    def __init__(self, value: int):
        """
        Initializes a Color instance from an integer.

        Parameters:
            value (int): Integer between 0x000000 and 0xFFFFFF.

        Raises:
            ValueError: If the value is out of range.
        """

        if not (0 <= value <= 0xFFFFFF):
            raise ValueError("Color value must be between 0x000000 and 0xFFFFFF")
        self.value = value

    def __int__(self):
        """
        Returns the integer value of the color.

        Returns:
            int: The 24-bit RGB integer.
        """

        return self.value

    def __repr__(self):
        """
        Returns the string representation of the color in hex format.

        Returns:
            str: A string like <Color #RRGGBB>.
        """

        return f"<Color #{self.value:06X}>"

    def to_rgb(self) -> Tuple[int, int, int]:
        """
        Converts the color to an (R, G, B) tuple.

        Returns:
            tuple: A tuple of 3 integers between 0 and 255.
        """

        r = (self.value >> 16) & 0xFF
        g = (self.value >> 8) & 0xFF
        b = self.value & 0xFF
        return (r, g, b)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        """
        Creates a Color instance from RGB values.

        Parameters:
            r (int): Red component (0–255).
            g (int): Green component (0–255).
            b (int): Blue component (0–255).

        Returns:
            Color: A new Color instance.

        Raises:
            ValueError: If any value is out of the 0–255 range.
        """

        if not all(0 <= n <= 255 for n in (r, g, b)):
            raise ValueError("RGB values must be between 0 and 255")
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """
        Creates a Color from a hex string.

        Supports 3-digit (e.g., "#f00") or 6-digit (e.g., "#ff0000") formats.

        Parameters:
            hex_str (str): Hex color string (with or without '#').

        Returns:
            Color: A new Color instance.

        Raises:
            ValueError: If the string is not a valid 3- or 6-digit hex code.
        """

        hex_str = hex_str.strip().lstrip("#")
        if len(hex_str) not in (3, 6):
            raise ValueError("Hex string must be 3 or 6 characters")
        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)
        return cls(int(hex_str, 16))

    @classmethod
    def from_str(cls, value: str) -> "Color":
        """
        Parses a color from a string.

        Supported formats:
            - "#RRGGBB"
            - "#RGB"
            - "rgb(R, G, B)"

        Parameters:
            value (str): A color string in hex or RGB format.

        Returns:
            Color: A new Color instance.

        Raises:
            ValueError: If the string format is invalid or unrecognized.
        """
        value = value.strip()
        if value.startswith("#"):
            return cls.from_hex(value)
        if value.lower().startswith("rgb"):
            match = re.fullmatch(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", value)
            if not match:
                raise ValueError("Invalid RGB string format")
            r, g, b = map(int, match.groups())
            return cls.from_rgb(r, g, b)
        raise ValueError(f"Unknown color format: {value}")

    @classmethod
    def red(cls) -> "Color":
        """Returns a standard red color (#E74C3C)."""
        return cls(0xE74C3C)

    @classmethod
    def green(cls) -> "Color":
        """Returns a standard green color (#2ECC71)."""
        return cls(0x2ECC71)

    @classmethod
    def blue(cls) -> "Color":
        """Returns a standard blue color (#3498DB)."""
        return cls(0x3498DB)

    @classmethod
    def yellow(cls) -> "Color":
        """Returns a standard yellow color (#F1C40F)."""
        return cls(0xF1C40F)

    @classmethod
    def orange(cls) -> "Color":
        """Returns a standard orange color (#E67E22)."""
        return cls(0xE67E22)

    @classmethod
    def purple(cls) -> "Color":
        """Returns a standard purple color (#9B59B6)."""
        return cls(0x9B59B6)

    @classmethod
    def teal(cls) -> "Color":
        """Returns a standard teal color (#1ABC9C)."""
        return cls(0x1ABC9C)

    @classmethod
    def pink(cls) -> "Color":
        """Returns a standard pink color (#FF69B4)."""
        return cls(0xFF69B4)

    @classmethod
    def random(cls) -> "Color":
        """
        Returns a randomly generated Color.

        Returns:
            Color: A color with a random 24-bit RGB value.
        """

        return cls(random.randint(0x000000, 0xFFFFFF))
