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

## Numbers

The renderer draws a string glyph by glyph from right to left, so the source's *first* character
ends up furthest right. A number written the way you read it therefore comes out backwards: the
Game Corner charged `081` coins for an Abra because the source said `180`.

**Literal numbers in text must be written backwards.** `052 steps` is what puts `250 steps` on
screen; `TM01` is written `מ”מ 10`.

Numbers built at runtime are already handled — `ConvertIntToDecimalStringN` ends in a `strrev`, so
a level, a price or an ID prints the right way round on its own. The same goes for the Pokédex
height and weight fields, which reverse their own buffers after formatting.

Nothing about a literal on its own says which way round it is, so this cannot be eyeballed.
`tools/hebrew/numbers.py` compares every string against the same string in English upstream,
matched by identifier or by label, and reports any digit run that is still in English order:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/pret/pokefirered /tmp/pokefirered-en
git -C /tmp/pokefirered-en sparse-checkout set src data
python3 tools/hebrew/numbers.py          # report
python3 tools/hebrew/numbers.py --fix    # reverse them in place
```

It skips any string whose Hebrew has a different count of digit runs from its English original,
because matching those by position would be guesswork — re-read those by hand.

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

`tools/hebrew/printers.py` checks this automatically. For a right-to-left print the pen budget
*is* `x` — the first glyph is blitted at `x` and the pen walks left — so a run needs
`total - firstGlyph` pixels to its left and the test needs to know nothing about the window. It
resolves the string argument of every `AddTextPrinterParameterized*` call that has a literal `x`,
including arrays indexed at runtime and `gStringVar4` traced back to whatever filled it, and
reports the ones that cannot fit. It found 39 unmirrored sites, among them the party menu's field
move description, the Pokédex's egg-hatch text, the Game Corner coin box and the clear-save-data
screen.

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

## Measuring a line

Do not count characters, and do not sum glyph widths. Both under-measure, the
build says nothing, and the line quietly clips in game. Use
`tools/hebrew/textwidth.py`, which models what the renderer does:

```python
import sys; sys.path.insert(0, "tools/hebrew")
import textwidth as T
T.overhang("שלום עולם")        # px outside the dialogue box; <= 0 means it fits
T.overhang(line, pen=T.PEN_ITEM_DESC)
T.help_width(line)             # the help system's separate renderer
```

Two things a naive sum gets wrong.

**A wide letter costs an extra pixel.** `src/text.c:877` subtracts one more pixel
after each of `א ב ד ה ח ט מ ס ע פ ש ת ם ף` when the *next* character is not
`י`, `ו` or `ן`. A line of 30 `ת` is 210px, not 180px. This one pixel per letter
is why 64 lines that looked comfortably inside the box were in fact clipping.

**The budget is not the window width.** A printer's `x` is where the first glyph
is blitted, and the pen then walks left, so a run occupies
`[x - (total - firstGlyphWidth), x + firstGlyphWidth)`. A line therefore fits
when `total - firstGlyphWidth <= x`, which is a few pixels more generous than
`total <= x`. Getting this wrong in the strict direction is harmless; getting it
wrong the other way loses a glyph.

| Window | Size | Pen | Fits when |
| --- | --- | --- | --- |
| Overworld dialogue box | 26 tiles / 208px | 200 | `total - first <= 200` |
| Battle message box | 28 tiles / 224px | 216 | `total - first <= 216` |
| Item description pane | 25 tiles / 200px | 192 | `total - first <= 192` |
| Help system main panel | 208px | 208, right edge | `help_width <= 208` |
| Safari ball label (healthbox) | 64px strip | 58 | `total - first <= 58` |
| Safari ball count (healthbox) | 48px strip | 43 | `total - first <= 43` |

The healthbox rows are the trap worth remembering: those scratch windows are
8 tiles wide but only *part* of each is copied into sprite VRAM, so the usable
strip is narrower than the window. Count the tiles the `TextIntoHealthboxObject`
calls actually copy, not the window's width.

**`{MIN_LETTER_SPACING n}` is the escape hatch for a strip that is too narrow.**
`FONT_SMALL` is forced to a 6px minimum in `src/text_printer.c:90`; prefixing a
string with `{MIN_LETTER_SPACING 5}` brings it back to the glyphs' own widths.
It can only pad a glyph *out*, never make one narrower, so it buys at most 1px
per character. Both Safari healthbox strings need it.

**Runtime substitutions have to be budgeted, per site.** `{PLAYER}` and
`{RIVAL}` are 49px at worst -- 7 glyphs, `PLAYER_NAME_LENGTH`, of the widest
Hebrew letter. (The naming keyboard also offers lowercase Latin, but every Latin
glyph is a flat 6px with no wide-letter padding, so Hebrew wins.) `{STR_VAR_n}`
is the harder one: a species name reaches 60px, a nickname 70, an item name 81,
a fishing record about 50, a level counter 12. Measuring every site against the
widest condemns lines that are fine; measuring against the narrowest ships lines
that clip the moment a player uses a long nickname.

`tools/hebrew/substitutions.py` resolves it per site -- scripts declare what
they buffer and `call`ed subroutines are followed, and the sites filled from C
(the day care, the fishing-record houses) are listed explicitly with the code
that writes them. `audit.py` uses it automatically. Wrap for that maximum, or
the line clips only for some players, which is exactly the bug that never shows
up in testing.

**The two renderers do not agree.** `HelpSystemRenderText()` uses a hard 4px
space, applies no wide-letter padding, and *drops* a glyph that would cross the
panel's left edge instead of clipping it. So help-system text measures narrower
than the same words in a dialogue box, and overflows there lose whole letters
rather than slivers.

## Rules for editing text

1. **Every `.string` block ends with `$`.** A missing terminator produces no build error and runs
   two messages together at runtime. Only the *last* `.string` of a block carries the `$`.
2. **Preserve control codes byte for byte**, and put them where they still make sense for Hebrew
   word order: `{STR_VAR_1..3}`, `{PLAYER}`, `{RIVAL}`, `{COLOR ...}`, `{PALETTE n}`, `{CLEAR_TO n}`,
   `{PLAY_SE ...}`.
3. **Keep the same line structure.** `\n` = next line, `\l` = scroll up one line and continue,
   `\p` = wait for A then clear the box. Dropping a `\p` merges two message boxes; dropping a `\n`
   runs a line off the edge.
4. **Measure every line you touch** with `tools/hebrew/audit.py` — see *Measuring a line*
   above. As a rough guide a dialogue line holds 28–30 Hebrew characters, but the real budget
   depends on which letters they are, so do not trust the count. Hebrew that is longer than the
   English must be rewritten shorter, not allowed to overflow.
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
python3 tools/hebrew/audit.py        # must print clean; exits non-zero otherwise
python3 tools/hebrew/numbers.py      # needs an English checkout, see Numbers above
```

The build catches illegal characters, assembly syntax errors and array overflows. `audit.py`
catches what it cannot: a line outside its window, a line that only clips once a player name is
filled in, an item description wider than its pane, a move description wider than the summary
panel, battle text wider than the battle box, a help-system line that loses letters, a printer
whose `x` cannot hold the string it prints, and a block with no `$` terminator. If a line it
flags cannot be re-wrapped, `python3 tools/hebrew/rewrap.py --apply` moves the line breaks for
you and reports anything that needs shortening instead.

Neither catches a dropped control code or a renamed label — read your diff for those.

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

## Testing in an emulator

Reading the source is not enough — most of the defects fixed in this fork were only visible on
screen, and several confident static readings of `src/text.c` turned out to be wrong. A headless
emulator driven by a script, taking screenshots, is the tool that settles arguments.

`tools/hebrew/emu/` is that harness, and [its README](../tools/hebrew/emu/README.md) is the
full guide: how to build it, the script language, a worked Safari journey, the ruler technique
for measuring a width you are unsure of, and the five pitfalls that cost real time. The short
version:

```bash
make -C tools/hebrew/emu MGBA=/path/to/your/mgba/checkout
python3 tools/hebrew/emu/journey.py out 1 63 safari.txt 16 16
```

- `runner` boots the ROM with a save and takes `<frames> <keys>`, `shot`, `read` and `w8/w16/w32`
  lines on stdin. `journey.py` wraps it to warp to a map first.
- **FireRed relocates its save blocks**, so `gSaveBlock1Ptr` at `0x03005008` changes value when a
  map loads. Read it *after* the warp — `journey.py` replays the prefix twice to do this. Poking
  the pre-warp address writes into memory that now belongs to something else, which looks
  convincingly like a crashing map.
- **A savestate does not survive a rebuild**, and a held A button skips a page. Both produce
  plausible nonsense rather than an error.
- **When a width calculation is in doubt, print a ruler** — put two strings of known width on the
  two lines of one page and read off the inked columns. That is how the wide-letter rule above
  was confirmed after three rounds of plausible-but-wrong arithmetic. Restore the string
  afterwards and check `git diff`.
- **A screen you cannot walk to is still testable.** `screen.py` boots to the overworld and then
  writes a function's address into `gMain.callback2`, which drops you straight into it:

  ```bash
  printf '260 -\nshot a\n' > plain.txt
  python3 tools/hebrew/emu/screen.py out CB2_SaveClearScreen_Init plain.txt
  ```

  That works for any callback that sets itself up from scratch — `CB2_SaveClearScreen_Init`,
  `CB2_InitMysteryGift`, `CB2_InitHofPC`, `CB2_ShowDiploma`, `CB2_InitSlotMachine`. One that
  expects an argument or a pre-filled static (`CB2_InitTrainerCard`, `CB2_InitMailView`) gives a
  black screenshot instead of an error; reach those through the menus.
- `crosscore` runs the same script through the mGBA, VBA-M, VBA-Next, gpSP and Mednafen libretro
  cores. All five render identically, which is expected — the framebuffer is 240x160 in hardware
  and the ROM positions its own text — but it is cheap to re-confirm.

## Save files and save states

**A battery save (`.sav` / `.srm`) survives a rebuild. A save state does not.**

The save file is data: the save block layout is untouched here, so the same file loads on any
build of this fork and on English FireRed. Verified in both directions on a real playthrough —
loaded, played, saved in-game and reloaded, on the current ROM and on the previous release.

A save state is the console's RAM and CPU registers, with no ROM in it. It resumes execution at
whatever address the program counter held, and every commit that changes code moves those
addresses. A state taken on one build therefore resets to the copyright screen within ten frames
on another — seen, not assumed: six states that run fine on `4322252…` all reset on the build
after it.

So: **tell players to save in-game before switching ROM builds.** If someone still has states
tied to an older build, the ROM for that build is reproducible — `git checkout <that commit> &&
make` gives the same SHA-1 — so they can resume the state there, save in-game, and carry the
battery save forward.

To inspect a state without RetroArch: `tools/hebrew/emu/unstate.py` unwraps RetroArch's RZIP and
RASTATE containers down to the raw core blob, and `crosscore`'s `state <blob>` command hands it
to `retro_unserialize`. The blob has to come from the same core, which `SERIALIZE size=` on
startup tells you — VBA-M's is 723,452 bytes, mGBA's 528,448.

## Where to continue

Reachable in single-player and verified on screen: the overworld, dialogue and signs, the
start menu, bag and item descriptions, the Pokédex list and entry pages, the Pokémon Storage
System, shops, the trainer card, the Fame Checker, the Hall of Fame viewer, the battle HUD and
battle menus, the move relearner and summary screen, the party menu's field-move descriptions,
the option menu, the help system, the Game Corner prize lists and coin box, the player's PC, the
clear-save-data screen, Mystery Gift's top menu, the diploma, the slot machine, the Safari Zone,
and the save and clock dialogues.

Checked on a real playthrough save (Victory Road, eight badges): the Day Care deposit flow, the
naming screen via the Name Rater, the Hall of Fame ceremony and its player-info page, the
department store elevator, the item PC and the player's PC menus.

Two of the link screens do open from a cold jump, and both are now checked: `CB2_LinkError`
draws the comm-error text in full, and `CB2_InitWirelessCommunicationScreen` draws the wireless
status board — which turned out to be showing one glyph per row and a truncated title, and is
mirrored now. The rest (`CB2_PokemonJump`, `CB2_EasyChatScreen`, `CB2_TradeMenu`,
`CB2_UnionRoomChatMain`) need a link session set up first and give a black screen cold.

Still not seen render: **mail** (needs a Pokémon holding some — the test save's mailbox is
empty), the **credits** (needs the Elite Four beaten; `CB2_Credits` will not start cold), and the
**Day Care level menu**. `ShowDaycareLevelMenu` is byte-identical to upstream and its window
never appeared in this build or the release before it — the script blocks on `waitstate` with the
message box still up and nothing drawn at the window's coordinates. Its two printers had the
same half-mirrored layout the rest of this fork started with (nickname at a left inset of 8, level
anchored on the right edge) and are swapped now, reasoned rather than watched: the two functions
are static and reached only from that menu, and twelve other screens are pixel-identical across
the change.

Not verified, because single-player cannot reach it at all: everything behind the link cable and
wireless adapter — trading, Union Room, Berry Crush, the Dodrio berry game, Mystery Gift and
the Easy Chat system. Their centring maths was mirrored the same way as the rest, but nobody
has seen it render. If you have two emulator instances linked, those screens are the first
place to look.

Still untranslated by design: the braille text in `data/text/braille.inc` (its own font), the
Latin chat keyboard rows in `src/keyboard_text.c`, the Japanese upstream leftovers, and blocks
marked `@ Unused`.

**What is left.** `audit.py` now covers the strings defined in C as well as those in `data/`, but
"covers" means one specific thing: a printer call whose `x` is a literal. That is 138 of the call
sites. It is not most of them.

- **157 printer calls compute their `x`** — from a parameter, a measured width, a struct field —
  and nothing checks those. (A further 70 compute it through an `RTL_ANCHOR_*` helper and are
  right by construction.) This is the same shape of gap as the one that hid the move relearner,
  one level up, and it is where the remaining bugs are: the item PC was found this way, not by a
  tool. Its whole screen printed through a local wrapper that takes `x` as a parameter, so every
  call passed upstream's left inset and every item showed one glyph.
- **Six printer entry points are not scanned at all**: `AddTextPrinterParameterized2` (44 calls —
  it has no `x` and prints from the window origin), `AddTextPrinterToWindow1` (27),
  `AddTextPrinter` (18), `AddTextPrinterAndCreateWindowOnHealthbox` (14),
  `AddTextPrinterDiffStyle` (3), `AddTextPrinterForMessage` (3).
- **A `ListMenuTemplate`'s `item_X` is a left inset too**, and it is set by assignment rather than
  passed to a printer, so no check sees it. `item_menu.c`, `berry_pouch.c`, `fame_checker.c`,
  `field_specials.c`, `item_pc.c` and `daycare.c` mirror theirs; `learn_move.c` (8) still does
  not. Grep `item_X` before trusting a list screen.
- **A cursor can sit on top of the text without either one clipping.** A menu window is sized for
  its text plus one cursor cell; if the mirrored anchor also subtracts that cell, the run ends up
  inside it, and redrawing the cursor erases the glyph underneath for good. Nothing measures this,
  because nothing is outside its window. It cost Nurse Joy the ן of כן. When a menu's last letter
  goes missing, check what the cursor is drawn over before assuming a width problem.
- **Only the left edge is tested.** A run whose first glyph starts past the window's right edge
  is not caught — that is why the healthbox level label loses its ר.
- **74 printer sites hold a runtime buffer** — a nickname, an Easy Chat phrase, a Wonder Card
  field. `SHOW_UNRESOLVED=1 python3 tools/hebrew/printers.py` lists them. Their `x` was mirrored
  by hand; none has been watched render with a worst-case value in it.
- **`numbers.py` cannot see a single digit in the wrong place.** It compares digit *runs* against
  English and skips runs of one character, because a single digit cannot be reversed. It
  therefore said nothing about `gText_2F` being `"ק2"` where `gText_2F_2` was `"2ק"` — same two
  characters, opposite order on screen. It also skips a string whose Hebrew has a different
  number of runs from its English original (44 such strings carry a number; all were checked by
  hand and are correct).
- **Latin text.** There is no bidi pass, so any Latin run inside a Hebrew string renders
  backwards — a save made before the species names were translated shows `DRAZIRAHC` in the
  party list. New games are unaffected because the names are Hebrew; old saves and
  player-chosen Latin nicknames are not fixable without a real bidi implementation.

One thing that looks wrong in a diff but is right on screen: the menu cursor `▶` sits to the
*left* of a right-aligned Hebrew entry, which is where it has to be — it points rightwards, into
the text. Its position is deliberately left where upstream put it; several callers pass a left
inset of 0, and moving the cursor clips the first glyph of every entry.
