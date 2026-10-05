# Pokémon FireRed in Hebrew

A full Hebrew translation of Pokémon FireRed, playable start to finish. The game's text is
translated and its text engine was rewritten to lay Hebrew out right to left — every menu, box
and label, not just the dialogue.

| | |
|---|---|
| ![](screenshots/battle_menu.png) | ![](screenshots/battle_moves.png) |
| ![](screenshots/bag.png) | ![](screenshots/shop.png) |

## Getting it

**One command**, if you have a FireRed **rev 0** ROM (`sha1: 41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`):

```bash
python3 tools/hebrew/getrom.py path/to/firered.gba
```

That needs nothing but Python. It fetches the patch from the latest release, applies it, and
writes `pokefirered-heb.gba`. The patch refuses any base but the right one and checks its own
result, so if it finishes you have the right ROM.

**No FireRed ROM?** A decompilation builds its own, so you do not have to find one — the commit
before the Hebrew work began is still English FireRed:

```bash
python3 tools/hebrew/getrom.py --build-base
```

That one needs the toolchain below, and a few minutes. Or skip the patch entirely and build this
fork directly with `make`, which lands at the same ROM.

The patch, `pokefirered-heb.bps`, is attached to the
[latest release](https://github.com/ronyeh2/pokefirered-heb/releases/latest) if you would rather
apply it with [Floating IPS](https://www.romhacking.net/utilities/1040/),
[beat](https://www.romhacking.net/utilities/893/) or an online patcher. Every release records the
SHA-1 of the ROM it produces, so you can always check what you ended up with.

## Building from source

Three steps, once per machine.

<details open>
<summary><strong>macOS</strong> — detail in <a href="INSTALL.md#macos">INSTALL.md</a></summary>

```bash
xcode-select --install                                   # if not already installed
brew install libpng pkg-config arm-none-eabi-binutils     # needs https://brew.sh
export CPATH=/opt/homebrew/include                        # /usr/local on an Intel Mac
export LIBRARY_PATH=/opt/homebrew/lib
```

Those two `export`s are not optional — without them the build stops at
`fatal error: 'png.h' file not found`, which looks like a broken repository and is the first
thing anyone hits on a Mac. Do **not** `brew install arm-none-eabi-gcc`; Homebrew's copy ships
without newlib. agbcc, below, brings its own.
</details>

<details>
<summary><strong>Linux</strong> (Debian/Ubuntu) — detail in <a href="INSTALL.md#linux">INSTALL.md</a></summary>

```bash
sudo apt install build-essential binutils-arm-none-eabi git libpng-dev pkg-config
```
</details>

<details>
<summary><strong>Windows</strong> — detail in <a href="INSTALL.md#windows-1011-wsl1">INSTALL.md</a></summary>

Build inside [WSL](https://learn.microsoft.com/windows/wsl/install) rather than natively: install
it, pick Ubuntu, and follow the Linux line above. msys2 and Cygwin also work and are covered in
[INSTALL.md](INSTALL.md#windows-msys2).
</details>

Then the compiler, [pret/agbcc](https://github.com/pret/agbcc), which installs itself into
`tools/agbcc/`:

```bash
git clone https://github.com/ronyeh2/pokefirered-heb.git
git clone https://github.com/pret/agbcc
cd agbcc && ./build.sh && ./install.sh ../pokefirered-heb && cd ..
```

And build:

```bash
cd pokefirered-heb
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
sha1sum pokefirered.gba        # shasum on macOS
```

`make` builds FireRed rev 0, the only target the Hebrew text and layout have been built and
checked against. `make leafgreen`, `make firered_rev1` and `make leafgreen_rev1` survive from
upstream and still compile, but nothing in them has been looked at here.

## Playing it

Any GBA emulator — [mGBA](https://mgba.io/), [VBA-M](https://vba-m.com/), a
[RetroArch](https://www.retroarch.com/) core. Text layout is decided by the ROM's own code, so it
renders identically on all of them.

A battery save (`.sav`/`.srm`) carries across builds of this fork; the save-block layout is
untouched. **A save state does not** — it holds CPU registers against code addresses a new build
has moved. Save in-game before switching ROMs.

Cheat codes for English FireRed (BPRE) — GameShark, Action Replay, CodeBreaker — work unchanged.
Nothing has moved in RAM; see
[RAM layout and cheat codes](docs/hebrew_translation.md#ram-layout-and-cheat-codes).

## State of the translation

Every screen reachable in single-player has been checked **on screen**, not just in the source:
the overworld and dialogue, the start menu, the bag and item descriptions, the Pokédex list and
entry pages, the Pokémon Storage System, shops, the trainer card, the Fame Checker, the Hall of
Fame viewer, the battle HUD and battle menus, the summary screen and move relearner, the party
menu, the options menu, the help system, the Game Corner, the player's PC, the diploma, the
Safari Zone, and the save and clock dialogues.

Not verified: everything behind the link cable and wireless adapter — trading, the Union Room,
Berry Crush, the Dodrio game, Mystery Gift's card screens and Easy Chat — plus mail, the credits
and the Day Care level menu, which no test save could bring up. The layout work was done for all
of them.

Latin text inside a Hebrew string still renders backwards; there is no bidi pass. A new game is
unaffected because the names are Hebrew, but a save made before the species names were translated
shows `DRAZIRAHC` in the party list, and a player-chosen Latin nickname always will. Braille, the
Latin chat keyboard and the Japanese leftovers from upstream are untranslated by design.

## Contributing

Issues and pull requests are welcome. This is a personal project done in spare time, so there is
no promise about when they get looked at.

**If you are editing text, read
[docs/hebrew_translation.md](docs/hebrew_translation.md) first.** It documents how right-to-left
works here and the traps everyone hits: there is more than one text renderer, literal
multi-digit numbers have to be typed backwards, and a line's width is not what counting
characters suggests.

Before committing text changes:

```bash
python3 tools/hebrew/audit.py     # every string against the window that prints it
python3 tools/hebrew/anchors.py   # printer anchors that were never mirrored
python3 tools/hebrew/numbers.py   # literal numbers, against the English original
```

`audit.py` exits non-zero on anything that would clip or run into the next message, none of which
the build itself catches; `tools/hebrew/rewrap.py --apply` fixes the line breaks it reports. The
emulator harness in `tools/hebrew/emu/` is what the screenshots come from, and
`make RTL_CLIP_REPORT=1` builds a ROM that reports glyphs drawn outside their window.

## About this fork

A fork of [pret/pokefirered](https://github.com/pret/pokefirered), which is a decompilation of
the English game — the code here is theirs, rearranged to read Hebrew. Upstream's own
documentation lives in [INSTALL.md](INSTALL.md), and the pret projects are at
[pret.github.io](https://pret.github.io/).

No ROM is distributed here. The patch contains the translation; the game it patches is Nintendo's
and you bring your own, or build it from source as above.

## Credits

Thanks to the team behind [Nog-Frog/pokered](https://github.com/Nog-Frog/pokered) — a lot of the
early translation work here was inspired by, and in places taken from, their Hebrew translation
of Pokémon Red/Blue. Their work is what got this started.
