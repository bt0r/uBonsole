#!/usr/bin/env python3
"""Recolors installed uBonsole files with a pastel accent color.

The repository files use the pink palette below as reference values. install.sh copies them,
then runs this script on the copies, which swaps every reference shade for the matching shade of
the chosen color:

    python3 tools/recolor.py blue ~/.config/i3/config ~/.config/i3/i3blocks.conf ...
    python3 tools/recolor.py --list

Run it on fresh copies only: once recolored, a file no longer contains the reference values.
"""
import re
import sys
from pathlib import Path

# Reference palette used in the repository files (the default pink)
REFERENCE = {
    "accent": "E09AB4",   # text, borders, selection
    "dim": "8A5A6E",      # separators, inactive borders, placeholders
    "light": "F2C9D9",    # Qt text on dark fields
    "mid": "C77FA0",      # Qt visited links
    "dark": "6B4A57",     # Qt disabled text
    "darker": "3A2A31",   # Qt disabled highlight
}

# Pastel accents, all readable on black. Pink keeps the hand-tuned reference shades.
ACCENTS = {
    "pink": "E09AB4",
    "blue": "9AC0E0",
    "red": "E0A0A0",
    "green": "A8D8A8",
    "yellow": "E0D49A",
    "white": "E0E0E0",
}


def rgb(hex6):
    return [int(hex6[i:i + 2], 16) for i in (0, 2, 4)]


def to_hex(values):
    return "".join("%02X" % max(0, min(255, round(v))) for v in values)


def shades(name):
    """Derives the secondary shades with the same ratios as the reference pink."""
    if name == "pink":
        return dict(REFERENCE)
    c = rgb(ACCENTS[name])
    return {
        "accent": ACCENTS[name],
        "dim": to_hex(v * 0.616 for v in c),
        "light": to_hex((v + 255) / 2 for v in c),
        "mid": to_hex(v * 0.89 for v in c),
        "dark": to_hex(v * 0.48 for v in c),
        "darker": to_hex(v * 0.26 for v in c),
    }


def recolor(text, name):
    new = shades(name)
    for key, ref in REFERENCE.items():
        # Keep the case of each occurrence (i3 uses #E09AB4, Qt uses #ffe09ab4)
        text = re.sub(ref, lambda m: new[key] if m.group().isupper() else new[key].lower(), text, flags=re.I)
    return text


def main(argv):
    if argv[:1] == ["--list"]:
        print(" ".join(ACCENTS))
        return 0
    if len(argv) < 2 or argv[0] not in ACCENTS:
        print("usage: recolor.py {%s} FILE..." % "|".join(ACCENTS), file=sys.stderr)
        return 1
    for f in argv[1:]:
        p = Path(f)
        p.write_text(recolor(p.read_text(), argv[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
