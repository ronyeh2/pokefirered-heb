# -*- coding: utf-8 -*-
"""Drive the headless runner to a screen and photograph it.

    python3 tools/hebrew/emu/journey.py OUTDIR MAPGROUP MAPNUM SCRIPT [X Y]

Boots the ROM with a save, warps to a map, then feeds SCRIPT to the runner.
SCRIPT is runner input (see runner.c) with three substitutions available:

    @SB1@   gSaveBlock1Ptr's value, re-read AFTER the warp
    @FLG@   the FLAG_SYS_SAFARI_MODE byte, i.e. @SB1@ + 0xFE0
    @LOC@   gSaveBlock1Ptr->location, i.e. @SB1@ + 4

Why the pointer is read twice
-----------------------------
FireRed deliberately relocates its save blocks, so the value at 0x03005008
CHANGES when a map loads. A flag poked at the address read before the warp
lands in memory that by then belongs to something else -- which looks exactly
like the game ignoring your poke, or like a particular map crashing. So this
runs the boot-and-warp prefix twice: once to learn where SaveBlock1 ended up,
and again for real with the addresses that pass fixed up. Emulation is
deterministic, so the second run puts it in the same place.

Warping needs BOTH the destination and the position: setting ->location and
calling CB2_LoadMap loads the map but leaves the player object behind, so
->pos is set too when X and Y are given.

CB2_LoadMap's address moves on every rebuild, so it is read from the ELF
rather than hard-coded.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ROM = os.path.join(ROOT, "pokefirered.gba")
ELF = os.path.join(ROOT, "pokefirered.elf")
RUNNER = os.path.join(HERE, "runner")
SAVE_TEMPLATE = os.environ.get("HEB_SAVE", os.path.join(HERE, "base.sav"))

GSAVEBLOCK1PTR = 0x03005008        # unchanged from vanilla; see docs
FLAGS_OFFSET = 0xEE0               # SaveBlock1.flags
SAFARI_FLAG_BYTE = FLAGS_OFFSET + (0x800 >> 3)     # FLAG_SYS_SAFARI_MODE
CB2_HOOK = 0x030030F4              # gMain.callback2


def symbol(name):
    out = subprocess.run(["arm-none-eabi-nm", ELF], capture_output=True, text=True).stdout
    for line in out.splitlines():
        f = line.split()
        if len(f) == 3 and f[2] == name:
            return int(f[0], 16)
    raise SystemExit("symbol not found in %s: %s" % (ELF, name))


def run(outdir, script):
    p = subprocess.run([RUNNER, ROM, outdir, os.path.join(outdir, "cur.sav")],
                       input=script, capture_output=True, text=True,
                       cwd=HERE, errors="replace")
    return p.stdout + p.stderr


def read32(output, addr):
    m = re.search(r"MEM %08X:((?: [0-9A-F]{2})+)" % addr, output)
    if not m:
        raise SystemExit("no read-back of %08X -- did the boot script fail?" % addr)
    b = [int(x, 16) for x in m.group(1).split()]
    return b[0] | b[1] << 8 | b[2] << 16 | b[3] << 24


def main():
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    # absolute, because the runner is invoked with cwd=HERE
    outdir = os.path.abspath(sys.argv[1])
    group, num, script_path = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    pos = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else None

    os.makedirs(outdir, exist_ok=True)
    if not os.path.exists(os.path.join(outdir, "cur.sav")):
        if not os.path.exists(SAVE_TEMPLATE):
            raise SystemExit("no save at %s -- set HEB_SAVE to a .sav to start from" % SAVE_TEMPLATE)
        with open(SAVE_TEMPLATE, "rb") as src, open(os.path.join(outdir, "cur.sav"), "wb") as dst:
            dst.write(src.read())

    boot = open(os.path.join(HERE, "boot.txt")).read()
    load_map = symbol("CB2_LoadMap") | 1          # Thumb

    # Pass 1: where is SaveBlock1 before anything moves?
    before = read32(run(outdir, boot + "read %08X 4\n" % GSAVEBLOCK1PTR), GSAVEBLOCK1PTR)

    prefix = boot
    if pos:
        prefix += "w16 %08X %04X\nw16 %08X %04X\n" % (before, pos[0], before + 2, pos[1])
    prefix += ("w8 %08X %X\nw8 %08X %X\nw8 %08X 0\n"
               "w16 %08X FFFF\nw16 %08X FFFF\n"
               "w32 %08X %08X\n400 -\n400 -\n"
               % (before + 4, group, before + 5, num, before + 6,
                  before + 8, before + 10, CB2_HOOK, load_map))

    # Pass 2: the same prefix, replayed, to learn where it ended up.
    after = read32(run(outdir, prefix + "read %08X 4\n" % GSAVEBLOCK1PTR), GSAVEBLOCK1PTR)
    sys.stderr.write("SaveBlock1: %08X before the warp, %08X after\n" % (before, after))

    body = (open(script_path).read()
            .replace("@SB1@", "%08X" % after)
            .replace("@LOC@", "%08X" % (after + 4))
            .replace("@FLG@", "%08X" % (after + SAFARI_FLAG_BYTE)))
    out = run(outdir, prefix + body)
    open(os.path.join(outdir, "run.log"), "w").write(out)

    for line in re.findall(r"(shot [A-Za-z0-9_]+ @\d+|MEM [0-9A-F]{8}:(?: [0-9A-F]{2})+)", out):
        print(line)
    for name in sorted(os.listdir(outdir)):
        if name.endswith(".raw"):
            subprocess.run([sys.executable, os.path.join(HERE, "topng.py"),
                            os.path.join(outdir, name)],
                           capture_output=True)


if __name__ == "__main__":
    main()
