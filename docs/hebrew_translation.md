# Hebrew translation guide

Everything in this file is about *this fork*. None of it applies to upstream `pret/pokefirered`.

## How Hebrew is stored

`charmap.txt` maps the Hebrew alphabet onto bytes `0x01`–`0x1B`, reusing the slots the accented
Latin characters occupied:

```
'א' = 01   'ב' = 02   'ג' = 03   ...   'ת' = 16
'ן' = 17   'ם' = 18   'ץ' = 19   'ף' = 1A   'ך' = 1B
```

Plain ASCII is untouched — `A`–`Z` at `0xBB`–`0xD4`, `a`–`z` at `0xD5`–`0xEE`, `0`–`9` at
`0xA1`–`0xAA` — so Latin text still works where it is wanted.

**Write Hebrew in normal logical order**, exactly as you would type it. Do not reverse words and do
not reverse strings. The renderer handles direction.

## How right-to-left actually works

There is no bidi algorithm. RTL exists because the renderer walks *backwards*:

- `RenderText()` in `src/text.c` **decrements** `currentX` after each glyph instead of incrementing
  it, so the first character of a string lands at the rightmost position.
- `AddTextPrinterParameterized2()` in `src/new_menu_helpers.c` starts the pen at `x = 200` instead
  of `0`, i.e. at the right edge of a standard dialogue window.

Two consequences that catch everybody out:

**1. There is more than one renderer.** `HelpSystemRenderText()` in `src/help_system_util.c` is a
completely separate glyph loop used by the help system and the save-failure screen. It had to be
converted to RTL separately. If you find a screen printing Hebrew mirrored, look for a renderer that
was never converted — the string data is usually fine.

**2. Multi-digit numbers must be typed reversed.** Since the pen walks one character leftwards at a
time, `"30"` typed normally renders as `03`. Literal numbers of two or more digits are therefore
written **backwards in the source**:

| You want on screen | You write in source |
| --- | --- |
| `Route 10` | `דרך 01` |
| `TM28` | `מ”מ82` |
| `level 30` | `רמה 03` |
| `¥500` | `¥005` |
| `2000` | `0002` |

Single digits need no reversal. **Runtime** numbers substituted through `{STR_VAR_1}` and friends are
already reversed by `strrev()` inside `ConvertIntToDecimalStringN()` (`src/string_util.c`) — never
hand-reverse a placeholder.

## Placing text: the anchor rule

`RenderText` decrements `currentX`, but `CopyGlyphToWindow` has already blitted
the glyph **at** `currentX` and clips it at the window border. So a printer's `x`
is the **first glyph's left edge**, not the string's right edge, and a run that
should sit flush against a boundary starts one glyph cell (8px) short of it.
That is why the 26-tile dialogue box prints at 200 rather than 208.

Passing an upstream left inset straight through is the single most common way to
break a Hebrew screen: the run walks off the left edge and only its first
character or two stay inside the window. Use the helpers in `include/window.h`
rather than a literal:

```c
RTL_ANCHOR_WINDOW(windowId)     // flush inside a window's right edge
RTL_ANCHOR_EDGE(rightEdgePx)    // flush inside an arbitrary edge, for scratch
                                // windows only partly copied out (healthbox)
RTL_MIRROR(widthPx, ltrX)       // the mirror of an upstream left-aligned column
```

Two things that are *not* anchors but look like them:

- Centring is `(box + width) / 2`, not `(box - width) / 2`.
- Padding written to right-align a number in LTR now renders to the number's
  **right**. Drop it; the pen already fixes the right edge.

Layout is identical on every emulator. The GBA framebuffer is 240x160 in
hardware and the text is positioned by the ROM's own code, so cores cannot
differ. Verified by running the same ROM and save on mGBA, VBA-M, VBA-Next,
gpSP and Mednafen: all five report `base 240x160, max 240x160` and render the
start menu and both trainer-card faces pixel-for-pixel identically. Cores differ
only in colour post-processing (and in pixel format - normalise to RGB565 before
diffing frames, or XRGB8888 cores will look different when they are not).

## Rules for editing text

1. **Every `.string` block ends with `$`.** A missing terminator produces no build error and runs
   two messages together at runtime. Only the *last* `.string` of a block carries the `$`.
2. **Preserve control codes byte for byte**, and put them where they still make sense for Hebrew
   word order: `{STR_VAR_1..3}`, `{PLAYER}`, `{RIVAL}`, `{COLOR ...}`, `{PALETTE n}`, `{CLEAR_TO n}`,
   `{PLAY_SE ...}`.
3. **Keep the same line structure.** `\n` = next line, `\l` = scroll up one line and continue,
   `\p` = wait for A then clear the box. Dropping a `\p` merges two message boxes; dropping a `\n`
   runs a line off the edge.
4. **Budget about 28–30 Hebrew characters per line.** A dialogue box is ~208px and Hebrew glyphs are
   6–7px. Hebrew that is longer than the English must be rewritten shorter, not allowed to overflow.
5. **Only characters in `charmap.txt` are legal.** There is no straight double quote — use the curly
   `”`. Use the single ellipsis character `…`, not three periods.
6. **Never rename a label.** The `Foo_Text_Bar::` symbols are referenced by scripts; renaming one
   fails the link.
7. **Respect fixed-size fields.** Some tables are hard-capped and overflowing them corrupts adjacent
   data or fails the build:

   | Field | Constant | Value |
   | --- | --- | --- |
   | Move names | `MOVE_NAME_LENGTH` | 12 |
   | Species names / nicknames | `POKEMON_NAME_LENGTH` | 10 |
   | Player and preset names | `PLAYER_NAME_LENGTH` | 7 |

8. **Some things must stay untranslated.** Japanese upstream leftovers, blocks commented `@ Unused`,
   the braille text in `data/text/braille.inc` (separate font), and the Latin chat keyboard rows in
   `src/keyboard_text.c`.

## Generated files

`src/data/region_map/region_map_entry_strings.h` is generated at build time from
`src/data/region_map/region_map_sections.json` and is gitignored. Edit the JSON.

`src/data/items.h` is likewise generated — edit the JSON source, not the header.

## Memory budget

EWRAM sits at **99.6% full** (about 1.1 KB free) and IWRAM at 91%. Text and translation work lives
in ROM, which is only ~46% used, so it is safe. But any fix that adds a RAM buffer, grows a global,
or widens a struct that is instantiated as a global array **will fail to link**. Check
`--print-memory-usage` output after a build.

## Before you commit

```bash
make -j$(sysctl -n hw.ncpu)          # must succeed
```

The build catches illegal characters, assembly syntax errors and array overflows. It does **not**
catch a missing `$`, a dropped control code, a renamed label or a wrongly-ordered number — check
those by reading your diff.

For terminology, follow what the already-translated files use rather than coining new wording;
`rg` for a proper noun before inventing a spelling for it.

## RAM layout and cheat codes

**This fork does not move anything in RAM.** Cheat codes written for English FireRed (BPRE)
— GameShark, Action Replay, CodeBreaker — work unchanged, because they address fixed RAM
locations and every one of those is still where vanilla put it:

| Symbol | Address |
| --- | --- |
| `gPlayerParty` | `0x02024284` |
| `gEnemyParty` | `0x0202402C` |
| `gBattleMons` | `0x02023BE4` |
| `gSaveBlock1` | `0x0202552C` |
| `gSaveBlock2` | `0x02024588` |
| `gSaveBlock1Ptr` | `0x03005008` |
| `gSaveBlock2Ptr` | `0x0300500C` |
| `gMain` | `0x030030F0` |

Verified, not assumed: the full RAM symbol table (963 symbols in EWRAM `0x02…` and IWRAM
`0x03…`) is byte-identical between this fork and the last upstream `pret/pokefirered` commit
before the Hebrew work began (`d61f95945`). Nothing has moved since the fork started.

That is not luck, and it is not automatic — it is a constraint you have to keep respecting.

Translation work is safe by nature: strings are `const` and live in ROM, which is only ~46%
used. What moves RAM is **code**: adding a global, growing a `static` array, widening a field
in a struct that is instantiated globally, or anything that changes the size or order of `.bss`
and COMMON symbols. Any of those shifts every symbol after it and silently invalidates a whole
class of cheat codes, on top of the risk that it simply fails to link — EWRAM is **99.6% full**,
with roughly 1.1 KB free.

So when you change C code, check it:

```bash
make                                   # note the --print-memory-usage output
arm-none-eabi-nm pokefirered.elf | awk '$1 ~ /^0[23]/ {print $1, $3}' | sort > after.txt
# build the previous revision the same way into before.txt, then:
diff before.txt after.txt              # must be empty
```

An empty diff means no RAM symbol moved. If EWRAM or IWRAM usage changed at all in
`--print-memory-usage`, something moved and the diff will show you what.
