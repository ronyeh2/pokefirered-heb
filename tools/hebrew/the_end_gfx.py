# -*- coding: utf-8 -*-
"""Redraw the credits' closing card as הסוף.

    python3 tools/hebrew/the_end_gfx.py          # rewrite the asset, then rebuild

"THE END" is not text -- it is 14 tiles arranged by a 32x32 tilemap, so it
cannot be translated by editing a string. The letters sit in a 20x3-tile band
of that map; everything around them is the card's own background and is left
exactly as it is. The Hebrew word is drawn at the same 4px stroke and 18px
cap height, cut into fresh tiles appended after the original 14, and only the
entries inside that band are rewritten.
"""
import io, os, struct
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GFX = os.path.join(ROOT, "graphics/credits")
INK, BG = 15, 1          # palette indices the original letters and field use
BAND_ROWS = range(8, 11) # the three tile rows the lettering occupies
BAND_COLS = range(5, 25)

S = 4                    # stroke
# Each glyph is a list of (row_start, row_end, col_start, col_end) ink boxes.
GLYPHS = {
    # ה: top bar, right stem, and a left leg that hangs clear of the bar
    "he":  (22, [(0, 3, 0, 21), (4, 17, 18, 21), (7, 17, 0, 3)]),
    # ס: a closed box
    "sam": (22, [(0, 3, 0, 21), (14, 17, 0, 21), (4, 13, 0, 3), (4, 13, 18, 21)]),
    # ו: a head and a stem
    "vav": (10, [(0, 3, 0, 9), (4, 17, 6, 9)]),
    # ף: top bar, an inner tongue, and a stem that drops below the line
    "pef": (22, [(0, 3, 0, 21), (4, 11, 0, 3), (8, 11, 0, 17), (4, 23, 18, 21)]),
}
WORD = ["pef", "vav", "sam", "he"]   # הסוף, drawn left to right
GAP = 8


def draw_word():
    w = sum(GLYPHS[g][0] for g in WORD) + GAP * (len(WORD) - 1)
    h = len(BAND_ROWS) * 8
    img = Image.new("P", (len(BAND_COLS) * 8, h), BG)
    px = img.load()
    x = (img.width - w) // 2
    for g in WORD:
        gw, boxes = GLYPHS[g]
        for r0, r1, c0, c1 in boxes:
            for yy in range(r0, r1 + 1):
                for xx in range(c0, c1 + 1):
                    if yy < h:
                        px[x + xx, yy] = INK
        x += gw + GAP
    return img


def main():
    strip = Image.open(os.path.join(GFX, "the_end.png"))
    pal = strip.getpalette()
    base_tiles = strip.width // 8
    sp = strip.load()
    tiles = []
    for t in range(base_tiles):
        tiles.append(tuple(sp[t * 8 + x, y] for y in range(8) for x in range(8)))

    word = draw_word()
    wp = word.load()
    index = {t: i for i, t in enumerate(tiles)}
    entries = {}
    for ri, r in enumerate(BAND_ROWS):
        for ci, c in enumerate(BAND_COLS):
            key = tuple(wp[ci * 8 + x, ri * 8 + y] for y in range(8) for x in range(8))
            if key not in index:
                index[key] = len(tiles)
                tiles.append(key)
            entries[(r, c)] = index[key]

    out = Image.new("P", (len(tiles) * 8, 8))
    out.putpalette(pal)
    op = out.load()
    for i, t in enumerate(tiles):
        for y in range(8):
            for x in range(8):
                op[i * 8 + x, y] = t[y * 8 + x]
    out.save(os.path.join(GFX, "the_end.png"))

    raw = bytearray(open(os.path.join(GFX, "the_end.bin"), "rb").read())
    for (r, c), t in entries.items():
        off = (r * 32 + c) * 2
        # Keep the palette bits, drop the flips: several of the original entries
        # mirror a tile to build a symmetric Latin letter, and inheriting that
        # draws the new Hebrew one backwards.
        struct.pack_into("<H", raw, off, (struct.unpack_from("<H", raw, off)[0] & 0xF000) | t)
    open(os.path.join(GFX, "the_end.bin"), "wb").write(bytes(raw))
    print("tiles %d -> %d, rewrote %d tilemap entries" % (base_tiles, len(tiles), len(entries)))


if __name__ == "__main__":
    main()
