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

import colorsys
import os
import shutil
import time
import tranci
from pathlib import Path

if __name__ == "__main__":
    try:
        for hue in range(360):
            r, g, b = colorsys.hsv_to_rgb(hue / 360, 1, 1)
            r, g, b = r * 255, g * 255, b * 255
            print(tranci.RGB(r, g, b, f"tranci"), end="\r")
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass

    FOLLOWUP_1 = ": puts you in a trance."
    FOLLOWUP_2 = f" v{tranci.__version__} | https://github.com/Butterroach/tranci"

    whitening_followup_1 = []
    whitening_followup_2 = []

    for i in range(len(FOLLOWUP_1)):
        _r, _g, _b = colorsys.hsv_to_rgb(hue / 360, 1 - (i + 1) / len(FOLLOWUP_1), 1)
        _r, _g, _b = _r * 255, _g * 255, _b * 255
        whitening_followup_1.append(tranci.RGB(_r, _g, _b, FOLLOWUP_1[i]))

    for i in range(len(FOLLOWUP_2)):
        _r, _g, _b = colorsys.hsv_to_rgb(hue / 360, 1 - (i + 1) / len(FOLLOWUP_2), 1)
        _r, _g, _b = _r * 255, _g * 255, _b * 255
        whitening_followup_2.append(tranci.RGB(_r, _g, _b, FOLLOWUP_2[i]))

    try:
        for i in range(1, len(FOLLOWUP_1)):
            if i > 1:
                time.sleep(0.15)
            print(
                f"\r{tranci.RGB(r, g, b, 'tranci')}{''.join(whitening_followup_1[:i])}",
                end="\r",
            )
    except KeyboardInterrupt:
        print(
            f"\r{tranci.RGB(r, g, b, 'tranci')}{''.join(whitening_followup_1)}",
            end="\r",
        )

    try:
        time.sleep(1)
    except:
        print(
            f"\r{tranci.RGB(r, g, b, 'tranci')}{''.join(whitening_followup_1)}",
            end="\r",
        )

    print(" " * shutil.get_terminal_size().columns, end="\r")
    print(f"{tranci.RGB(r, g, b, 'tranci')}{''.join(whitening_followup_2)}\n")

    time.sleep(0.1)

    print(
        tranci.Red(
            f"This is red text, \nbut {tranci.Blue('this is blue')}. And the rest is red."
        )
    )

    print(tranci.RGB(255, 165, 0, "This is custom RGB text."))
    print(tranci.HEX("#AFCBED", "This is custom HEX text with str."))
    print(tranci.HEX(0xEFEABD, "This is custom HEX text with int."))
    print(
        tranci.Bold(
            tranci.Italicized(
                tranci.Underlined(
                    tranci.BrightMagenta(
                        "This is bold, italicized, underlined, and bright magenta text."
                    )
                )
            )
        )
    )

    warning = tranci.HEX("#fff374")

    print(warning("This is a warning colored by saving a color and calling it."))
    print(warning("Another warning!"))
    print(tranci.Inverted(warning("And that's the inverted one!")))
    print(tranci.BGHEX("#fff374", tranci.HEX(0, "Or if you wanna be real, I suppose.")))

    print(
        tranci.Hyperlink(
            "https://rickroll.link",
            f"...{tranci.Italicized(warning('Hyperlinks'))}? What?",
        )
    )

    google = tranci.Hyperlink("https://www.google.com/")

    print(google("This supports saving too, for whatever reason."))
