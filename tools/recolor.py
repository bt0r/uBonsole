#!/usr/bin/env python3
"""Recolors installed uBonsole files with an accent color.

The repository files use the pink palette below as reference values. install.sh copies them,
then runs this script on the copies, which swaps every reference shade for the matching shade of
the chosen color: one of the pastel names, or any custom #RRGGBB.

    python3 tools/recolor.py blue ~/.config/i3/config ~/.config/i3/i3blocks.conf ...
    python3 tools/recolor.py '#A0C4FF' ~/.config/i3/config ...
    python3 tools/recolor.py --list
    python3 tools/recolor.py --check '#A0C4FF'    # normalized color + contrast on black

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


MIN_CONTRAST = 7.0   # WCAG AAA for normal text; every pastel above is around 9-14 on black


def parse(color):
    """Returns the accent as RRGGBB (uppercase) from a pastel name or #RRGGBB, or None."""
    if color in ACCENTS:
        return ACCENTS[color]
    hex6 = color.lstrip("#")
    if re.fullmatch(r"[0-9A-Fa-f]{6}", hex6):
        return hex6.upper()
    return None


def contrast_on_black(hex6):
    """WCAG contrast ratio of the color against pure black."""
    lin = [(v / 255) / 12.92 if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in rgb(hex6)]
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return (lum + 0.05) / 0.05


def shades(color):
    """Derives the secondary shades with the same ratios as the reference pink."""
    if color == "pink":
        return dict(REFERENCE)
    accent = parse(color)
    c = rgb(accent)
    return {
        "accent": accent,
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
    if argv[:1] == ["--check"] and len(argv) == 2:
        accent = parse(argv[1])
        if accent is None:
            return 1
        ratio = contrast_on_black(accent)
        print("#%s %.1f %s" % (accent, ratio, "ok" if ratio >= MIN_CONTRAST else "low"))
        return 0
    if len(argv) < 2 or parse(argv[0]) is None:
        print("usage: recolor.py {%s|#RRGGBB} FILE..." % "|".join(ACCENTS), file=sys.stderr)
        return 1
    for f in argv[1:]:
        p = Path(f)
        p.write_text(recolor(p.read_text(), argv[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
