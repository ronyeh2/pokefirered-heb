# Automated render journeys

Reading the source is not enough. Most of the layout defects fixed in this fork were only
visible on screen, and several confident static readings of `src/text.c` turned out to be
wrong. This directory is the harness that settled those arguments: a headless emulator, driven
by a text script, that walks to a screen and photographs it.

## Build

```bash
git clone --depth 1 -b 0.10.5 https://github.com/mgba-emu/mgba /tmp/mgba
cmake -S /tmp/mgba -B /tmp/mgba/build -DBUILD_QT=OFF -DBUILD_SDL=OFF
make -C /tmp/mgba/build -j
make -C tools/hebrew/emu MGBA=/tmp/mgba
```

A packaged libmgba works too (`make MGBA_PREFIX=/opt/homebrew`), but Homebrew's records an
*absolute* path to ffmpeg's `libavcodec`, so it stops loading the moment Homebrew bumps ffmpeg's
soname — `Library not loaded: …/libavcodec.62.dylib`, which no rpath can override. The source
build needs no ffmpeg at all with Qt and SDL off.

You also need a save to start from. Put one at `tools/hebrew/emu/base.sav`, or point `HEB_SAVE`
at it. Nothing here ships a save or a ROM.

## `runner` — one screen, scripted

`runner <rom> <outdir> [save.sav]` reads a script on stdin:

| Line | Meaning |
| --- | --- |
| `60 A` | run 60 frames with A held |
| `300 -` | run 300 frames with no input |
| `shot name` | dump the framebuffer to `<outdir>/name.raw` |
| `read 03005008 4` | hex-dump 4 bytes to stderr |
| `w8`/`w16`/`w32 addr val` | poke RAM |
| `ss file` / `sl file` | save / load a savestate |

Keys are `A B START SELECT UP DOWN LEFT RIGHT Lb Rb`. `topng.py` turns the `.raw` dumps into
PNGs at 2x.

## `journey.py` — warp somewhere, then script it

```bash
python3 tools/hebrew/emu/journey.py OUTDIR MAPGROUP MAPNUM SCRIPT [X Y]
```

It boots, warps to the map, then feeds `SCRIPT` to the runner with `@SB1@`, `@LOC@` and `@FLG@`
substituted for the live `gSaveBlock1Ptr`, its `->location`, and the `FLAG_SYS_SAFARI_MODE` byte.
Map group/number constants are in `include/constants/map_groups.h`.

The worked example that found two real bugs — a Safari encounter with the ball counter visible:

```
w8 @FLG@ 1              # FLAG_SYS_SAFARI_MODE, so the encounter is a Safari battle
30 -
70 LEFT                 # pace in the grass until something appears
20 -
70 RIGHT
20 -
... (repeat)
2 A                     # into the battle
300 -
w8 02039994 1E          # gNumSafariBalls = 30
10 -
2 A                     # throw a ball, so the count redraws as 29
180 -
shot safari
```

```
$ python3 tools/hebrew/emu/journey.py out 1 63 safari.txt 16 16
SaveBlock1: 0202554C before the warp, 02025530 after
shot safari @6844
```

## Five things that cost real time

**FireRed relocates its save blocks.** The value at `0x03005008` *changes* when a map loads —
the game shuffles the save blocks deliberately. A flag poked at the address read before the warp
lands in memory that by then belongs to something else, which looks exactly like the game
ignoring your poke, or like a particular map crashing. `journey.py` therefore replays the
boot-and-warp prefix twice, once to learn where SaveBlock1 ended up and again for real; the
line it prints above shows the address moving. An afternoon went into blaming individual maps
for what were really writes into stale memory.

**Warping needs the position as well as the destination.** Setting `->location` and calling
`CB2_LoadMap` loads the map but leaves the player object behind. Set `->pos` too.

**`CB2_LoadMap` moves on every rebuild.** Read it from the ELF, never hard-code it. Same for
anything else you poke by symbol — `journey.py` shells out to `arm-none-eabi-nm`.

**A savestate does not survive a rebuild.** Code addresses shift, so a state saved against one
build is garbage against the next; it produces plausible nonsense rather than an error. Script a
cold boot instead — that is what `boot.txt` is.

**Text prints progressively, and A does two jobs.** Wait for a page to finish before capturing.
And tap A briefly: holding it for 20 frames completes the current page *and* advances past the
next one, so you screenshot a page later than you think you do. Two measurements in this fork's
history were wrong for exactly that reason, which is how a real rendering rule got mistaken for
a non-existent one and back again.

## Rendering many lines in one run

Tempting, and there are three traps. All three produce output that looks like
data rather than like a broken harness, which is what makes them expensive.

**The expansion buffer is 1000 bytes.** `ShowFieldMessage` expands the *whole*
string -- every `\p` page of it -- into `gStringVar4`, which is
`EWRAM_DATA u8 gStringVar4[1000]` (src/string_util.c). A test label holding 400
pages overflows it and the results are garbage that still looks like
screenshots. Keep a test string well under 1000 bytes of expanded text, or feed
one line at a time.

**A sign message closes itself.** Wait long enough after opening one and it
closes on its own, so the next A press re-opens it instead of advancing, and
every capture after that is one page out of step. Counter-intuitively a *longer*
wait is worse: 130 frames per page worked, 280 desynced the entire run. If the
lines you are rendering are long enough to need more time than that, render them
one at a time rather than paging.

**`{STR_VAR_1}` alone is the reliable way to render arbitrary text.** Point a
sign at a label whose entire content is `{STR_VAR_1}$`, then poke the line you
want into `gStringVar1` before each A press. `gStringVar1`, `2` and `3` are
adjacent, so a single write starting at `gStringVar1` has about 68 bytes before
it would reach `gStringVar4` -- enough for any dialogue line. One build renders
anything, with no paging and no buffer to overflow. Just remember the line you
poke is a single line: if you need to see a real multi-line page as the player
sees it, put the real page in the test label instead.

## Measuring a screenshot

Two things will quietly mislead you.

The message box has a dark border, so a naive "count dark pixels in this row"
picks up the frame at both edges and reports a 208px-wide line whatever the text
is. Restrict the scan to the box interior.

And a clipped glyph does not smear against the edge -- it **vanishes**.
`currentX` is a `u8`, so when the pen walks past zero it wraps to about 250 and
the glyph is blitted off the right of the window instead. So a clipped line's
leftmost ink can sit comfortably inside the box while a word is missing
entirely. Compare the rendered ink *span* against the predicted width rather
than looking at where the line starts; a fully-rendered line matches within
about 2px, or up to 8px when its extreme glyph is `.`, `…` or `!`, whose ink
does not fill its cell.

## Printing a ruler

When a width calculation is in doubt, stop calculating and measure. Temporarily point a sign's
`msgbox` at a string of known width and read off where it clips:

```asm
PalletTown_Text_TownSign::
    .string "תתתתתתתתתתתתתתתתתתתת\n"    @ 20 wide letters
    .string "וווווווווווווווווווו$"    @ 20 narrow ones, same count
```

Put the two strings on the *two lines of one page* rather than on separate pages — then one
screenshot shows both and there is no way to be looking at the wrong page. Warp to Pallet Town
(group 3, map 0) at (9,12), press UP then A, and compare the inked columns:

```
line1 (20 tav): left= 84 right=221   -> 7.21px per glyph
line2 (20 vav): left=104 right=219   -> 6.05px per glyph
```

That one pixel of difference is `src/text.c:877` padding wide Hebrew letters, and it is the rule
that 64 clipping lines had been measured without. `tools/hebrew/textwidth.py` predicts
82..222 for that line, which is the match that settled it.

**Restore the string afterwards.** Keep a copy before you edit, and check `git diff` before
committing — a ruler left in a sign is a very silly thing to ship.

## `crosscore` — the same ROM on five emulators

`crosscore <core.dylib> <rom> <outdir> [save.sav]` is a minimal libretro frontend taking the
same script on stdin. Download the mGBA, VBA-M, VBA-Next, gpSP and Mednafen-GBA libretro cores,
run the same script through each, and diff the frames.

Layout cannot actually differ between cores — the GBA framebuffer is 240x160 in hardware and
text is positioned by the ROM's own code — and that is what the comparison shows: all five
report `base 240x160, max 240x160` and render the start menu and both trainer-card faces
pixel-for-pixel identically. Worth re-running after layout work anyway, because it is cheap and
it answers the question directly.

One trap when diffing: cores differ in pixel format. Normalise to RGB565 before comparing, or
an XRGB8888 core shows hundreds of "differing" pixels that are nothing but rounding.
