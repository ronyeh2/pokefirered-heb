# -*- coding: utf-8 -*-
"""How wide a Hebrew string renders, according to what src/text.c actually does.

Import this rather than summing glyph widths by hand. A plain sum is wrong twice
over, and both mistakes are silent -- the build succeeds and the text clips.

1. src/text.c:877 subtracts an extra 1px after each of 14 "wide" Hebrew letters
   when the following character is not י, ו or ן. A line of 30 ת is 210px, not
   180px.
2. A printer's x is where the FIRST glyph is blitted, and the pen then walks
   left. So a run occupies [x - (total - firstGlyphWidth), x + firstGlyphWidth)
   and it fits a window iff (total - firstGlyphWidth) <= x.

Both were verified against the running game with a ruler string: 20 ת printed in
the Pallet Town sign box lands at screen x 84..221, which is what this model
predicts to the pixel (82..222 window-relative plus the box's 16px offset).
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The letters src/text.c:877 pads, and the letters that suppress the padding.
WIDE_LETTERS = {0x01, 0x02, 0x04, 0x05, 0x08, 0x09, 0x0D,
                0x0F, 0x10, 0x11, 0x15, 0x16, 0x18, 0x1A}
NO_PAD_AFTER = {0x0A, 0x06, 0x17}          # י ו ן

# Window budgets, as (pen, comment). A line fits iff total - first <= pen.
PEN_MESSAGE_BOX = 200      # 26 tiles, AddTextPrinterParameterized2
PEN_ITEM_DESC   = 192      # 25-tile description pane
PEN_BATTLE_BOX  = 216      # 28 tiles, B_WIN_MSG

# Worst-case glyph counts for runtime substitutions, so a line that fits the
# budget fits for every real substitution.
PLACEHOLDER_GLYPHS = {"PLAYER": 7, "RIVAL": 7,          # PLAYER_NAME_LENGTH
                      "STR_VAR_1": 8, "STR_VAR_2": 8, "STR_VAR_3": 8}

_ZERO_WIDTH = re.compile(
    r"^(COLOR|HIGHLIGHT|SHADOW|COLOR_HIGHLIGHT_SHADOW|PALETTE|SIZE|"
    r"PAUSE|PAUSE_UNTIL_PRESS|PAUSE_MUSIC|RESUME_MUSIC|PLAY_BGM|PLAY_SE|"
    r"WAIT_SE|CLEAR|CLEAR_TO|SKIP|MIN_LETTER_SPACING|ESCAPE|SHIFT_RIGHT|"
    r"SHIFT_DOWN|JPN|ENG|NO_MUSIC)\b")
_PLACEHOLDER = re.compile(r"\{(PLAYER|RIVAL|STR_VAR_[123])\}")


def _charmap():
    cm = {}
    for line in io.open(os.path.join(ROOT, "charmap.txt"), encoding="utf-8"):
        for pattern in (r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$",
                        r"^'\\(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$"):   # e.g. '\'' = B4
            m = re.match(pattern, line)
            if m and m.group(1) not in cm:
                cm[m.group(1)] = int(m.group(2), 16)
    cm.setdefault(" ", 0x00)
    return cm


def _glyph_widths(name):
    src = io.open(os.path.join(ROOT, "src/text.c"), encoding="utf-8").read()
    m = re.search(r"static const u8 %s\[\] =\s*\{(.*?)\};" % name, src, re.S)
    body = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    return [int(x) for x in re.findall(r"\d+", body)]


CHARMAP = _charmap()
WIDTHS = {"small":  _glyph_widths("sFontSmallLatinGlyphWidths"),
          "normal": _glyph_widths("sFontNormalLatinGlyphWidths"),
          "copy1":  _glyph_widths("sFontNormalCopy1LatinGlyphWidths")}
DEFAULT_MIN_SPACING = {"small": 6, "normal": 0, "copy1": 0}   # src/text_printer.c:90


def to_bytes(text, placeholders=False):
    """Charmap bytes for a source string, or None if the width is unknowable.

    Zero-width control codes are dropped. With placeholders=True, {PLAYER} and
    friends are budgeted at their worst case; otherwise they make the string
    unmeasurable. Anything else in braces -- {FONT_*}, keypad icons -- always
    does, because its width depends on state we cannot see here.
    """
    out, i = [], 0
    while i < len(text):
        if text[i] == "{":
            j = text.find("}", i)
            if j < 0:
                return None
            code = text[i + 1:j]
            ph = _PLACEHOLDER.match("{%s}" % code)
            if ph:
                if not placeholders:
                    return None
                out += [0x15] * PLACEHOLDER_GLYPHS[code]      # ש, a widest glyph
            elif not (_ZERO_WIDTH.match(code) or code.isdigit()):
                return None
            i = j + 1
            continue
        if text[i] == "\\" or text[i] not in CHARMAP:
            return None
        out.append(CHARMAP[text[i]])
        i += 1
    return out


def width(text, font="normal", min_spacing=None, placeholders=False):
    """Rendered width in px, or None if the string is not statically measurable."""
    if min_spacing is None:
        min_spacing = DEFAULT_MIN_SPACING[font]
    data = text if isinstance(text, (list, tuple)) else to_bytes(text, placeholders)
    if data is None:
        return None
    table, total = WIDTHS[font], 0
    for i, b in enumerate(data):
        # min_spacing only pads a glyph out; it can never make one narrower.
        total += max(table[b], min_spacing) if min_spacing else table[b]
        nxt = data[i + 1] if i + 1 < len(data) else 0xFF
        if b in WIDE_LETTERS and nxt not in NO_PAD_AFTER:
            total += 1
    return total


def first_glyph(text, font="normal", min_spacing=None, placeholders=False):
    if min_spacing is None:
        min_spacing = DEFAULT_MIN_SPACING[font]
    data = text if isinstance(text, (list, tuple)) else to_bytes(text, placeholders)
    if not data:
        return None
    w = WIDTHS[font][data[0]]
    return max(w, min_spacing) if min_spacing else w


def overhang(text, pen=PEN_MESSAGE_BOX, font="normal", min_spacing=None,
             placeholders=False):
    """px by which the line falls outside its window. <= 0 means it fits."""
    data = text if isinstance(text, (list, tuple)) else to_bytes(text, placeholders)
    if not data:
        return None
    w = width(data, font, min_spacing)
    return w - first_glyph(data, font, min_spacing) - pen


def fits(text, pen=PEN_MESSAGE_BOX, **kw):
    o = overhang(text, pen, **kw)
    return o is not None and o <= 0


def help_width(text):
    """The help system has its OWN renderer (src/help_system_util.c): spaces are
    a hard 4px, there is no wide-letter padding, and a glyph that would cross the
    panel's left edge is dropped whole rather than clipped. Its main panel is
    208px and x is the right edge, so a line fits iff width <= 208."""
    data = to_bytes(text)
    if data is None:
        return None
    return sum(4 if b == 0x00 else WIDTHS["normal"][b] for b in data)
