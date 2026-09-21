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
    trading, Union Room, Berry Crush, the Dodrio game, Mystery Gift and Easy Chat — plus a few
    single-player screens this save could not set up: the Day Care level readout, the item PC's
    quantity prompt, mail and the credits. The layout work was done for all of them.
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

There is no ROM in this repository or in its releases, and there will not be: a built
`pokefirered.gba` contains Nintendo's game — its graphics, music, maps and original text —
so distributing one would be distributing their copyrighted work. This is the same reason
[pret](https://pret.github.io/) never ships ROMs.

Build it yourself; it takes a couple of minutes:

```bash
git clone https://github.com/ronyeh2/pokefirered-heb.git
cd pokefirered-heb
# see INSTALL.md for the toolchain (agbcc + devkitARM's binutils)
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
```

Each release records the SHA-1 of the ROM that commit produces, so you can confirm your
build matches. Any GBA emulator will run it — the layout is decided by the ROM's own code,
so it renders identically on mGBA, VBA-M, VBA-Next, gpSP and Mednafen.

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