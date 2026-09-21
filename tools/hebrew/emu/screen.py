# -*- coding: utf-8 -*-
"""Jump straight into a screen's entry callback and photograph it.

    python3 tools/hebrew/emu/screen.py OUTDIR SYMBOL SCRIPT

Boots the ROM with a save, waits for the overworld, then writes SYMBOL's
address into gMain.callback2 and hands SCRIPT (runner input, see runner.c) to
the runner. That reaches screens no amount of button pressing can get to from a
mid-game save -- the clear-save-data screen, Mystery Gift, the Hall of Fame
viewer, the diploma -- so their Hebrew layout can be checked like any other.

SYMBOL is any function name in pokefirered.elf; the Thumb bit is set for you.
It has to be a callback that sets itself up from scratch (the CB2_Init* family
and CB2_Show*), because nothing else will have run first. A screen that expects
an argument or a pre-filled static struct will hang or crash instead, which
looks like a black screenshot.

The same @SB1@ / @SB2@ / @FLG@ / @LOC@ substitutions journey.py documents work
here too.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import journey

CB2_HOOK = journey.CB2_HOOK


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    outdir = os.path.abspath(sys.argv[1])
    sym, script_path = sys.argv[2], sys.argv[3]

    os.makedirs(outdir, exist_ok=True)
    if not os.path.exists(os.path.join(outdir, "cur.sav")):
        with open(journey.SAVE_TEMPLATE, "rb") as src, \
             open(os.path.join(outdir, "cur.sav"), "wb") as dst:
            dst.write(src.read())

    boot = open(os.path.join(HERE, "boot.txt")).read()
    addr = journey.symbol(sym) | 1

    probe = journey.run(outdir, boot + "read %08X 4\nread %08X 4\n"
                        % (journey.GSAVEBLOCK1PTR, journey.GSAVEBLOCK2PTR))
    sb1 = journey.read32(probe, journey.GSAVEBLOCK1PTR)
    sb2 = journey.read32(probe, journey.GSAVEBLOCK2PTR)

    body = (open(script_path).read()
            .replace("@SB1@", "%08X" % sb1)
            .replace("@LOC@", "%08X" % (sb1 + 4))
            .replace("@SB2@", "%08X" % sb2)
            .replace("@FLG@", "%08X" % (sb1 + journey.SAFARI_FLAG_BYTE)))
    bases = {"SB1": sb1, "SB2": sb2}
    body = re.sub(r"@(SB[12])\+([0-9A-Fa-f]+)@",
                  lambda m: "%08X" % (bases[m.group(1)] + int(m.group(2), 16)), body)
    leftover = re.findall(r"@[A-Za-z0-9_+]+@", body)
    if leftover:
        raise SystemExit("unsubstituted marker(s) in %s: %s" % (script_path, sorted(set(leftover))))

    out = journey.run(outdir, boot + "w32 %08X %08X\n" % (CB2_HOOK, addr) + body)
    open(os.path.join(outdir, "run.log"), "w").write(out)
    sys.stderr.write("%s -> %08X\n" % (sym, addr))
    for line in re.findall(r"(shot [A-Za-z0-9_]+ @\d+|MEM [0-9A-F]{8}:(?: [0-9A-F]{2})+)", out):
        print(line)
    for name in sorted(os.listdir(outdir)):
        if name.endswith(".raw"):
            subprocess.run([sys.executable, os.path.join(HERE, "topng.py"),
                            os.path.join(outdir, name)], capture_output=True)


if __name__ == "__main__":
    main()
