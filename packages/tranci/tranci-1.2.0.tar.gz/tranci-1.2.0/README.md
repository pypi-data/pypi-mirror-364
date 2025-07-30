# tranci: puts you in a trance.

<img src="screenshot.png" alt="Screenshot of Tranci's __main__.py output.">

## What in the world is a "tranci"?

`tranci` is a no-dependencies, lightweight, easy-to-use, Pythonic ANSI library. It officially supports Python 3.9-3.13. You can move the cursor around, do some colors. Idk, just general ANSI.

## How do I use this?

Install the `tranci` package with `pip`. Run `python -m tranci` to confirm it works.

Example code:

```py
import tranci

print(tranci.Red("Red text"))
print(tranci.BGRed("Red background"))
print(tranci.RGB(164, 106, 120, "RGB code"))
print(tranci.HEX("#A44A44", "HEX code"))

weird_cyan_green_color_thing = tranci.HEX(0x3affad)

print(weird_cyan_green_color_thing("You can save them too"))
```

You can figure out everything else just by looking at your IDE's autocomplete! (or just look at the cool `tranci/__main__.py` source code)

## Why would I use this over anything else

-   Auto reset handling
-   Actual nesting functionality
-   IDE auto-complete won't cry seeing the code
-   True color
-   Zero dependencies

## Ok but ~~[that one clone of a JS library that shall not be named]~~ exists

-   It's a clone of a JS library. What do you think?
-   `tranci` has everything ~~[that one clone of a JS library that shall not be named]~~ has except fallbacks.
-   You don't need fallbacks/capabilities-detection. It just adds bloat.
-   Even if the JS clone is slightly lighter, `tranci` isn't just colors and styles and <font color="red"><u>**_~~oooo look at this bold italic striked underlined red text!!!~~_**</u></font>. It also supports a bit more general ANSI, in a more Pythonic extendable syntax. You can add your own ANSI things to `tranci` with the class system. Plus the world won't end if your project is 51.82KiB larger than it could be.

Download tranci now! or something uhh what do those mobile game ads say at the end again
