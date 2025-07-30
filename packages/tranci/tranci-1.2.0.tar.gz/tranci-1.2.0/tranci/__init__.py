"""
Tranci: a no-dependencies, lightweight, easy-to-use ANSI library

Copyright (c) 2025 Butterroach

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import re  # tragedy
import sys
from enum import Enum
from typing import cast, Union

if sys.platform == "win32":
    os.system("")  # fix ANSI on conhost

RESET: str = "\033[0m"

__version__: str = "1.2.0"


class BaseText(str):
    """
    Base class for colors and styles. Does not include operations.
    """

    def __new__(cls, code: str, text: Union[str, None] = None) -> "BaseText":
        if text is None:
            return cast("BaseText", super().__new__(cls))  # type: ignore[redundant-cast]
        return cast("BaseText", super().__new__(  # type: ignore[redundant-cast]
            cls,
            code
            + re.sub(
                r"\r\n|\n",
                lambda m: f"{RESET}{m.group(0)}{code}",  # type: ignore
                text.replace(RESET, code),
            )
            + RESET,
        ))

    def __init__(self, code: str, text: Union[str, None] = None) -> None:
        self.code = code

    def __call__(self, text: str) -> str:
        """
        Returns the text provided in the same style. Useful for saving colors and reusing them over and over again.
        """

        return BaseText.__new__(BaseText, self.code, text)


class Hyperlink(str):
    """
    Bet you didn't know this was a thing! Yeah, it's real. Hyperlinks. In a terminal. Crazy. Just be aware that this is not too standard.
    """

    def __new__(cls, url: str, text: Union[str, BaseText, None] = None) -> "Hyperlink":
        if text is None:
            return cast("Hyperlink", super().__new__(cls))  # type: ignore[redundant-cast]
        return cast("Hyperlink",  # type: ignore[redundant-cast]
                    super().__new__(cls, f"\033]8;;{url}\033\\{text}\033]8;;\033"))

    def __init__(self, url: str, text: Union[str, BaseText, None] = None) -> None:
        self.url = url

    def __call__(self, text: str) -> "Hyperlink":
        """
        Why are you doing this with hyperlinks
        """

        return Hyperlink.__new__(Hyperlink, self.url, text)


class Bold(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Bold":  # NOQA
        code = '\x1b[1m'
        return cast("Bold", super().__new__(cls, code, text))


class Dim(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Dim":  # NOQA
        code = '\x1b[2m'
        return cast("Dim", super().__new__(cls, code, text))


class Italicized(BaseText):
    """Some legacy terminals don't support italicized text."""
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Italicized":  # NOQA
        code = '\x1b[3m'
        return cast("Italicized", super().__new__(cls, code, text))


class Underlined(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Underlined":  # NOQA
        code = '\x1b[4m'
        return cast("Underlined", super().__new__(cls, code, text))


class Blinking(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Blinking":  # NOQA
        code = '\x1b[5m'
        return cast("Blinking", super().__new__(cls, code, text))


class SlowlyBlinking(BaseText):
    """Support for slow blinking is highly limited. Most modern terminals will treat this the same as normal blink."""
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "SlowlyBlinking":  # NOQA
        code = '\x1b[6m'
        return cast("SlowlyBlinking", super().__new__(cls, code, text))


class Inverted(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Inverted":  # NOQA
        code = '\x1b[7m'
        return cast("Inverted", super().__new__(cls, code, text))


class Hidden(BaseText):
    """This has absolutely no use. I don't know why this is in ANSI at all."""
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Hidden":  # NOQA
        code = '\x1b[8m'
        return cast("Hidden", super().__new__(cls, code, text))


class Striked(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Striked":  # NOQA
        code = '\x1b[9m'
        return cast("Striked", super().__new__(cls, code, text))


class Black(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Black":  # NOQA
        code = '\x1b[30m'
        return cast("Black", super().__new__(cls, code, text))


class Red(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Red":  # NOQA
        code = '\x1b[31m'
        return cast("Red", super().__new__(cls, code, text))


class Green(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Green":  # NOQA
        code = '\x1b[32m'
        return cast("Green", super().__new__(cls, code, text))


class Yellow(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Yellow":  # NOQA
        code = '\x1b[33m'
        return cast("Yellow", super().__new__(cls, code, text))


class Blue(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Blue":  # NOQA
        code = '\x1b[34m'
        return cast("Blue", super().__new__(cls, code, text))


class Magenta(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Magenta":  # NOQA
        code = '\x1b[35m'
        return cast("Magenta", super().__new__(cls, code, text))


class Cyan(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Cyan":  # NOQA
        code = '\x1b[36m'
        return cast("Cyan", super().__new__(cls, code, text))


class White(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "White":  # NOQA
        code = '\x1b[37m'
        return cast("White", super().__new__(cls, code, text))


class Gray(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "Gray":  # NOQA
        code = '\x1b[90m'
        return cast("Gray", super().__new__(cls, code, text))


class BrightRed(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightRed":  # NOQA
        code = '\x1b[91m'
        return cast("BrightRed", super().__new__(cls, code, text))


class BrightGreen(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightGreen":  # NOQA
        code = '\x1b[92m'
        return cast("BrightGreen", super().__new__(cls, code, text))


class BrightYellow(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightYellow":  # NOQA
        code = '\x1b[93m'
        return cast("BrightYellow", super().__new__(cls, code, text))


class BrightBlue(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightBlue":  # NOQA
        code = '\x1b[94m'
        return cast("BrightBlue", super().__new__(cls, code, text))


class BrightMagenta(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightMagenta":  # NOQA
        code = '\x1b[95m'
        return cast("BrightMagenta", super().__new__(cls, code, text))


class BrightCyan(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightCyan":  # NOQA
        code = '\x1b[96m'
        return cast("BrightCyan", super().__new__(cls, code, text))


class BrightWhite(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BrightWhite":  # NOQA
        code = '\x1b[97m'
        return cast("BrightWhite", super().__new__(cls, code, text))


class BGBlack(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBlack":  # NOQA
        code = '\x1b[40m'
        return cast("BGBlack", super().__new__(cls, code, text))


class BGRed(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGRed":  # NOQA
        code = '\x1b[41m'
        return cast("BGRed", super().__new__(cls, code, text))


class BGGreen(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGGreen":  # NOQA
        code = '\x1b[42m'
        return cast("BGGreen", super().__new__(cls, code, text))


class BGYellow(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGYellow":  # NOQA
        code = '\x1b[43m'
        return cast("BGYellow", super().__new__(cls, code, text))


class BGBlue(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBlue":  # NOQA
        code = '\x1b[44m'
        return cast("BGBlue", super().__new__(cls, code, text))


class BGMagenta(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGMagenta":  # NOQA
        code = '\x1b[45m'
        return cast("BGMagenta", super().__new__(cls, code, text))


class BGCyan(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGCyan":  # NOQA
        code = '\x1b[46m'
        return cast("BGCyan", super().__new__(cls, code, text))


class BGWhite(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGWhite":  # NOQA
        code = '\x1b[47m'
        return cast("BGWhite", super().__new__(cls, code, text))


class BGGray(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGGray":  # NOQA
        code = '\x1b[100m'
        return cast("BGGray", super().__new__(cls, code, text))


class BGBrightRed(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightRed":  # NOQA
        code = '\x1b[101m'
        return cast("BGBrightRed", super().__new__(cls, code, text))


class BGBrightGreen(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightGreen":  # NOQA
        code = '\x1b[102m'
        return cast("BGBrightGreen", super().__new__(cls, code, text))


class BGBrightYellow(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightYellow":  # NOQA
        code = '\x1b[103m'
        return cast("BGBrightYellow", super().__new__(cls, code, text))


class BGBrightBlue(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightBlue":  # NOQA
        code = '\x1b[104m'
        return cast("BGBrightBlue", super().__new__(cls, code, text))


class BGBrightMagenta(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightMagenta":  # NOQA
        code = '\x1b[105m'
        return cast("BGBrightMagenta", super().__new__(cls, code, text))


class BGBrightCyan(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightCyan":  # NOQA
        code = '\x1b[106m'
        return cast("BGBrightCyan", super().__new__(cls, code, text))


class BGBrightWhite(BaseText):
    def __new__(cls, text: Union[str, BaseText, None] = None) -> "BGBrightWhite":  # NOQA
        code = '\x1b[107m'
        return cast("BGBrightWhite", super().__new__(cls, code, text))


class RGB(BaseText):
    def __new__(cls, r: int, g: int, b: int, text: Union[str, BaseText, None] = None) -> "RGB":
        return cast("RGB", super().__new__(cls, f"\033[38;2;{int(r)};{int(g)};{int(b)}m", text))

    def __init__(self, r: int, g: int, b: int, text: Union[str, BaseText, None] = None) -> None:  # NOQA
        self.code = f"\033[38;2;{int(r)};{int(g)};{int(b)}m"


class HEX(RGB):
    def __new__(cls, hexa: Union[str, int], text: Union[str, BaseText, None] = None) -> "HEX":
        if isinstance(hexa, str):
            hexa = int(hexa.replace("#", ""), 16)
        return cast("HEX", super().__new__(
            cls, (hexa >> 16) & 255, (hexa >> 8) & 255, hexa & 255, text
        ))

    def __init__(self, hexa: Union[str, int], text: Union[str, BaseText, None] = None) -> None:
        if isinstance(hexa, str):
            hexa = int(hexa.replace("#", ""), 16)
        super().__init__((hexa >> 16) & 255, (hexa >> 8) & 255, hexa & 255)


class BGRGB(BaseText):
    def __new__(cls, r: int, g: int, b: int, text: Union[str, BaseText, None] = None) -> "BGRGB":
        return cast("BGRGB", super().__new__(cls, f"\033[48;2;{int(r)};{int(g)};{int(b)}m", text))

    def __init__(self, r: int, g: int, b: int, text: Union[str, BaseText, None] = None) -> None:  # NOQA
        self.code = f"\033[48;2;{int(r)};{int(g)};{int(b)}m"


class BGHEX(BGRGB):
    def __new__(cls, hexa: Union[str, int], text: Union[str, BaseText, None] = None) -> "BGHEX":
        if isinstance(hexa, str):
            hexa = int(hexa.replace("#", ""), 16)
        return cast("BGHEX", super().__new__(
            cls, (hexa >> 16) & 255, (hexa >> 8) & 255, hexa & 255, text
        ))

    def __init__(self, hexa: Union[str, int], text: Union[str, BaseText, None] = None) -> None:
        if isinstance(hexa, str):
            hexa = int(hexa.replace("#", ""), 16)
        super().__init__((hexa >> 16) & 255, (hexa >> 8) & 255, hexa & 255)


class Direction(Enum):
    UP = "A"
    DOWN = "B"
    RIGHT = "C"
    LEFT = "D"


def move_cursor_dir(direction: Direction, lines: int, do_print: bool = True) -> str:
    code = f"\033[{lines}{direction.value}"
    if do_print:
        print(code, end="")
    return code


def move_cursor_pos(row: int, col: int, do_print: bool = True) -> str:
    """
    move_cursor_pos(1, 1) will move the cursor to the top left corner.
    """

    code = f"\033[{row};{col}H"
    if do_print:
        print(code, end="")
    return code


def save_cursor_pos(do_print: bool = True) -> str:
    """
    Tells the terminal emulator to save the current position for later use during the current session.
    """

    code = "\033[s"
    if do_print:
        print(code, end="")
    return code


def restore_cursor_pos(do_print: bool = True) -> str:
    """
    Tells the terminal emulator to move the cursor back to the last saved position.
    """

    code = "\033[u"
    if do_print:
        print(code, end="")
    return code


def set_cursor_visibility(visible: bool, do_print: bool = True) -> str:
    if visible:
        code = "\033[?25h"
    else:
        code = "\033[?25l"
    if do_print:
        print(code, end="")
    return code


def clear_screen(do_print: bool = True) -> str:
    code = "\033[2J"
    if do_print:
        print(code, end="")
    return code


def clear_line(do_print: bool = True) -> str:
    code = "\033[2K"
    if do_print:
        print(code, end="")
    return code
