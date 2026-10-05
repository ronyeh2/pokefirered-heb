# Pokémon FireRed and LeafGreen

This is a decompilation of English Pokémon FireRed and LeafGreen.

It builds the following ROM images:

* [**pokefirered.gba**](https://datomatic.no-intro.org/?page=show_record&s=23&n=1616) `sha1: 41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`
* [**pokeleafgreen.gba**](https://datomatic.no-intro.org/?page=show_record&s=23&n=1617) `sha1: 574fa542ffebb14be69902d1d36f1ec0a4afd71e`
* [**pokefirered_rev1.gba**](https://datomatic.no-intro.org/?page=show_record&s=23&n=1672) `sha1: dd5945db9b930750cb39d00c84da8571feebf417`
* [**pokeleafgreen_rev1.gba**](https://datomatic.no-intro.org/index.php?page=show_record&s=23&n=1668) `sha1: 7862c67bdecbe21d1d69ce082ce34327e1c6ed5e`

To set up the repository, see [INSTALL.md](INSTALL.md).

For contacts and other pret projects, see [pret.github.io](https://pret.github.io/).

## About this Fork

This repository is a fork of [pret/pokefirered](https://github.com/pret/pokefirered), aiming to translate Pokémon FireRed and LeafGreen to be fully playable in **Hebrew**.

- **State of the translation:**
  - Every screen reachable in single-player has been checked on screen, not just in the source:
    the overworld and dialogue, the start menu, bag and item descriptions, the Pokédex list and
    entry pages, the Pokémon Storage System, shops, the trainer card, the Fame Checker, the Hall
    of Fame viewer, the battle HUD and battle menus, the summary screen and move relearner, the
    party menu, the option menu, the help system, the Game Corner, the player's PC, the diploma,
    the Safari Zone, and the save and clock dialogues.
  - What has *not* been verified is everything behind the link cable and wireless adapter —
    trading, Union Room, Berry Crush, the Dodrio game, Mystery Gift and Easy Chat — plus three
    single-player screens no test save could set up: mail, the credits, and the Day Care level
    menu. The layout work was done for all of them.
  - Braille, the Latin chat keyboard and the Japanese upstream leftovers are untranslated by
    design.
- **Contributions:**
  - Issues and pull requests are welcome! Please note that this is a personal project done in my free time, so I can't guarantee when I'll be able to address them.
- **Translating:**
  - See [docs/hebrew_translation.md](docs/hebrew_translation.md) for how Hebrew and right-to-left
    rendering work in this fork, and the rules to follow when editing text. Reading it first will
    save you from the traps everyone hits: there is more than one text renderer, literal
    multi-digit numbers have to be typed backwards, and a line's width is not what counting
    characters suggests.
  - Before committing text changes, run `python3 tools/hebrew/audit.py`. It checks every string
    against the window that actually prints it — including the ~1900 defined in C — and exits
    non-zero on anything that would clip or run into the next message, none of which the build
    itself catches. `python3 tools/hebrew/rewrap.py --apply` fixes the line breaks it reports,
    and `python3 tools/hebrew/numbers.py` checks that literal numbers are stored backwards, by
    comparing them against the English original.
- **Building on macOS:**
  - See the [macOS section of INSTALL.md](INSTALL.md#macos). Use agbcc; Homebrew's
    `arm-none-eabi-gcc` ships without newlib and cannot build the modern target.
- **Cheat codes still work:**
  - This fork does not move anything in RAM, so GameShark / Action Replay / CodeBreaker
    codes written for English FireRed (BPRE) work unchanged. See
    [RAM layout and cheat codes](docs/hebrew_translation.md#ram-layout-and-cheat-codes).

## Getting the ROM

There is no `.gba` in this repository — you build it from this source. It takes a few minutes,
and the result is byte-for-byte the ROM whose SHA-1 the release records, so you can check you
got the right one.

### 1. Install the toolchain (once per machine)

<details open>
<summary><strong>macOS</strong> — full detail in <a href="INSTALL.md#macos">INSTALL.md</a></summary>

```bash
xcode-select --install                                        # if not already installed
brew install libpng pkg-config arm-none-eabi-binutils          # needs https://brew.sh
export CPATH=/opt/homebrew/include                             # /usr/local on an Intel Mac
export LIBRARY_PATH=/opt/homebrew/lib
```

Those two `export`s are not optional: Homebrew keeps its headers off the default search path, so
without them the build stops at `fatal error: 'png.h' file not found`. Put them in your shell
profile or set them in the shell you build from.

Do **not** `brew install arm-none-eabi-gcc` — Homebrew's copy ships without newlib. agbcc, below,
brings its own.
</details>

<details>
<summary><strong>Linux</strong> (Debian/Ubuntu) — full detail in <a href="INSTALL.md#linux">INSTALL.md</a></summary>

```bash
sudo apt install build-essential binutils-arm-none-eabi git libpng-dev pkg-config
```
</details>

<details>
<summary><strong>Windows</strong> — full detail in <a href="INSTALL.md#windows-1011-wsl1">INSTALL.md</a></summary>

Build inside WSL rather than natively. Install
[WSL](https://learn.microsoft.com/windows/wsl/install), pick Ubuntu, then follow the Linux
instructions above inside it. msys2 and Cygwin also work and are covered in
[INSTALL.md](INSTALL.md#windows-msys2).
</details>

### 2. Install agbcc (once per clone)

The compiler this build uses is [pret/agbcc](https://github.com/pret/agbcc). It installs itself
into `tools/agbcc/`, which is gitignored:

```bash
git clone https://github.com/ronyeh2/pokefirered-heb.git
git clone https://github.com/pret/agbcc
cd agbcc
./build.sh
./install.sh ../pokefirered-heb
cd ..
```

### 3. Build

```bash
cd pokefirered-heb
git checkout firered-v1.0
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
```

`firered-v1.0` is the tag of the [latest release](https://github.com/ronyeh2/pokefirered-heb/releases/latest);
omit the `git checkout` to build the tip of the branch instead.

### 4. Check what you built

The ROM lands at `pokefirered.gba` in the repository root:

```bash
shasum pokefirered.gba          # macOS
sha1sum pokefirered.gba         # Linux
```

| | |
| --- | --- |
| `pokefirered.gba` | 16,777,216 bytes |
| SHA-1 | `01816e6f078b8b6ab82670b1d8ac3c887d310239` |
| SHA-256 | `7cca97bcbe44174344629091b1b284e274b2f2f37775d53f52e52adf322fa57f` |

A different hash means a different build, not necessarily a broken one — check you are on the
tag above, and that `make` finished without errors.

### 5. Play it

Any GBA emulator runs it: [mGBA](https://mgba.io/) (recommended),
[VBA-M](https://vba-m.com/), or a [RetroArch](https://www.retroarch.com/) core. Text layout is
decided by the ROM's own code, so it renders identically on all of them.

Your battery save (`.sav`/`.srm`) carries across builds of this fork. A **save state does not** —
it stores CPU registers against code addresses a new build has moved, so save in-game before
switching ROMs.

### Other targets

`make` builds FireRed rev 0, which is the only target the Hebrew text and layout have been built
and checked against. The Makefile still carries `make leafgreen`, `make firered_rev1` and
`make leafgreen_rev1` from upstream; those build, but nothing in them has been verified here.

## Credits

A special thanks to the team behind [Nog-Frog/pokered](https://github.com/Nog-Frog/pokered) — a lot of the early translation work for this project was inspired by (and in some cases taken from) their Hebrew translation of Pokémon Red/Blue. Their efforts and resources were invaluable in getting this project started.

## Screenshots

<!-- Add screenshots below. Example: -->

| battle menu| battle moves |
|---------------------|---------------------|
| ![](screenshots/battle_menu.png) | ![](screenshots/battle_moves.png) |

| bag | shop |
|---------------------|---------------------|
| ![](screenshots/bag.png) | ![](screenshots/shop.png) |

| pokecenter |
|---------------------|
| ![](screenshots/pokecenter.png) |