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

- **Work in Progress:**
  - The translation is ongoing. Some screens may still be incorrectly formatted, and some text may be untranslated or incorrectly translated.
- **Contributions:**
  - Issues and pull requests are welcome! Please note that this is a personal project done in my free time, so I can't guarantee when I'll be able to address them.
- **Translating:**
  - See [docs/hebrew_translation.md](docs/hebrew_translation.md) for how Hebrew and right-to-left
    rendering work in this fork, and the rules to follow when editing text. Reading it first will
    save you from the two traps everyone hits: there is more than one text renderer, and literal
    multi-digit numbers have to be typed backwards.
- **Building on macOS:**
  - See the [macOS section of INSTALL.md](INSTALL.md#macos). Use agbcc; Homebrew's
    `arm-none-eabi-gcc` ships without newlib and cannot build the modern target.
- **Cheat codes still work:**
  - This fork does not move anything in RAM, so GameShark / Action Replay / CodeBreaker
    codes written for English FireRed (BPRE) work unchanged. See
    [RAM layout and cheat codes](docs/hebrew_translation.md#ram-layout-and-cheat-codes).

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