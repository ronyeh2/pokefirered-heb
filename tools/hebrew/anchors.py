# -*- coding: utf-8 -*-
"""Printer anchors that look like they were never mirrored.

printers.py asks whether a known string fits a known pen. This asks the
complementary question, which needs no string at all: is the pen itself
plausible for a right-to-left print?

Under RTL the x handed to a printer is where the FIRST glyph is blitted, and
the pen then walks left. So x is the entire budget the rest of the run has.
Two shapes of anchor are wrong on sight:

  * a small x -- upstream's left inset, left behind. A pen of 0 draws one glyph
    and wraps the u8 on the next, so the run vanishes rather than clips. This is
    what hid the TM mart's move name and the "restore which move" list.
  * an x past the right edge of its own window. The pen is outside, so every
    glyph until it walks back inside is lost. This is what hid the first words
    of every TM description, where a pen sized for the 25-tile regular layout
    was reused in the 18-tile TM one.

Window widths are resolved where the file makes it possible: InitWindows on a
template array indexed by a literal id, or a single named template passed to
AddWindow. Sites whose window cannot be pinned down are listed separately
rather than guessed at.
"""
import io, os, re, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as T
from printers import strip_comments, split_args, SRCS

ROOT = T.ROOT

# name -> (windowId argument index, x argument index); None means the entry
# point has no x of its own and prints from a default set in new_menu_helpers.c.
SIGS = {"AddTextPrinterParameterized":  (0, 3),
        "AddTextPrinterParameterized2": (0, None),
        "AddTextPrinterParameterized3": (0, 2),
        "AddTextPrinterParameterized4": (0, 2),
        "AddTextPrinterParameterized5": (0, 3)}
CALL = re.compile(r"\b(AddTextPrinterParameterized[2345]?)\s*\(")

# The pen AddTextPrinterParameterized2 hardcodes (src/new_menu_helpers.c).
PARAM2_PEN = 200

SMALL_PEN = 24          # three glyphs at most, whatever the string is
TEMPLATE = re.compile(
    r"struct\s+WindowTemplate\s+(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\n\};", re.S)
ONE_TEMPLATE = re.compile(
    r"struct\s+WindowTemplate\s+(\w+)\s*=\s*\{(.*?)\n\};", re.S)
WIDTH_FIELD = re.compile(r"\.width\s*=\s*(\d+)")
INIT = re.compile(r"InitWindows\s*\(\s*(\w+)\s*\)")


def template_widths(body):
    """Widths of each entry of a WindowTemplate[] initialiser, in order."""
    widths, depth, cur = [], 0, []
    for ch in body:
        if ch == "{":
            depth += 1
            if depth == 1:
                cur = []
                continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                m = WIDTH_FIELD.search("".join(cur))
                widths.append(int(m.group(1)) if m else None)
                continue
        if depth >= 1:
            cur.append(ch)
    return widths


def file_windows(text):
    """{windowId: widthPx} for a file, as far as it can be worked out."""
    arrays = {name: template_widths(body) for name, body in TEMPLATE.findall(text)}
    singles = {name: int(m.group(1)) if (m := WIDTH_FIELD.search(body)) else None
               for name, body in ONE_TEMPLATE.findall(text)}
    out = {}
    for name in INIT.findall(text):
        for i, w in enumerate(arrays.get(name, [])):
            if w is not None:
                # A later InitWindows of a different array means the same id can
                # be two widths; keep the narrower, which is the one that clips.
                out[i] = min(out.get(i, w), w)
    return out, singles


def main():
    small, past_edge, unknown = [], [], []
    for path in SRCS:
        if not path.endswith(".c"):
            continue
        text = strip_comments(io.open(path, encoding="utf-8").read())
        windows, _ = file_windows(text)
        rel = os.path.relpath(path, ROOT)
        for m in CALL.finditer(text):
            name = m.group(1)
            args = split_args(text, m.end() - 1)
            if not args:
                continue
            wi, xi = SIGS[name]
            if wi >= len(args):
                continue
            win = args[wi].strip()
            pen = PARAM2_PEN if xi is None else (
                args[xi].strip() if xi < len(args) else None)
            line = text[:m.start()].count("\n") + 1
            site = (rel, line, name, win, pen)
            if pen is None:
                continue
            if re.fullmatch(r"\d+", str(pen)):
                penv = int(pen)
            elif xi is None:
                penv = PARAM2_PEN
            else:
                continue                      # computed pen: printers.py's gap
            if not re.fullmatch(r"\d+", win):
                unknown.append(site + (penv,))
                continue
            width = windows.get(int(win))
            if width is None:
                unknown.append(site + (penv,))
                continue
            width *= 8
            if penv + 8 > width:
                past_edge.append(site + (penv, width))
            elif penv < SMALL_PEN:
                small.append(site + (penv, width))

    def show(title, rows, note):
        print("\n%s  (%d)" % (title, len(rows)))
        print("  " + note)
        for r in rows:
            print("    %-46s %-30s win %-3s pen %-4s window %spx"
                  % ("%s:%d" % (r[0], r[1]), r[2], r[3], r[5], r[6]))

    show("pen starts past its own window's right edge", past_edge,
         "every glyph is lost until the pen walks back inside")
    show("pen too small to hold a right-to-left run", small,
         "x is the first glyph's left edge, so this is upstream's inset")
    print("\nliteral pen, window not resolvable here: %d" % len(unknown))
    if os.environ.get("SHOW_UNRESOLVED"):
        for r in unknown:
            print("    %-46s %-30s win %-20s pen %s"
                  % ("%s:%d" % (r[0], r[1]), r[2], r[3], r[5]))


if __name__ == "__main__":
    main()
