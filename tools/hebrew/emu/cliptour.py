# -*- coding: utf-8 -*-
"""Walk screens against the RTL_CLIP_REPORT build and say which ones lose glyphs.

    make RTL_CLIP_REPORT=1
    python3 tools/hebrew/emu/cliptour.py OUTDIR MAPGROUP MAPNUM SCRIPT [X Y]

The diagnostic build records every glyph blitted outside its window. A script
line of `clip <label>` expands to a read of the report buffer followed by a
reset of its counter, so each label gets the clips that happened since the last
one. Each report names the window, the font, the pen the printer was given, the
pen it had reached, and the address it had reached in the string -- which is
resolved back to the nearest symbol here, because that is what identifies the
screen in source.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ELF = os.path.join(ROOT, "pokefirered.elf")
REPORTS = 24
ENTRY = 12


def symbols():
    out = subprocess.run(["arm-none-eabi-nm", "-n", ELF],
                         capture_output=True, text=True).stdout
    syms = []
    for line in out.splitlines():
        f = line.split()
        if len(f) == 3 and f[1] in "DdRrTtBbVvWw":
            syms.append((int(f[0], 16), f[2]))
    return syms


def nearest(syms, addr):
    lo, hi = 0, len(syms) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if syms[mid][0] <= addr:
            best = syms[mid]; lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        return "%08X" % addr
    return "%s+%d" % (best[1], addr - best[0])


def main():
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    outdir, group, num, script_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    count_addr = int(subprocess.run(
        ["arm-none-eabi-nm", ELF], capture_output=True, text=True).stdout
        .split("gRtlClipReportCount")[0].strip().split("\n")[-1].split()[0], 16)
    base_addr = int(subprocess.run(
        ["arm-none-eabi-nm", ELF], capture_output=True, text=True).stdout
        .split("gRtlClipReports\n")[0].strip().split("\n")[-1].split()[0], 16)

    labels = []
    body = []
    for line in open(script_path):
        m = re.match(r"\s*clip\s+(\S+)", line)
        if m:
            labels.append(m.group(1))
            body.append("read %08X 2\n" % count_addr)
            body.append("read %08X %X\n" % (base_addr, REPORTS * ENTRY))
            body.append("w16 %08X 0000\n" % count_addr)
        else:
            body.append(line)
    tmp = os.path.join(outdir, "_tour.txt")
    os.makedirs(outdir, exist_ok=True)
    open(tmp, "w").write("".join(body))

    cmd = [sys.executable, os.path.join(HERE, "journey.py"), outdir, group, num, tmp] + sys.argv[5:]
    out = subprocess.run(cmd, capture_output=True, text=True)
    sys.stderr.write(out.stderr)
    dumps = re.findall(r"MEM [0-9A-F]{8}:((?: [0-9A-F]{2})+)", out.stdout)
    syms = symbols()

    for i, label in enumerate(labels):
        if 2 * i + 1 >= len(dumps):
            break
        cnt_b = [int(x, 16) for x in dumps[2 * i].split()]
        count = cnt_b[0] | cnt_b[1] << 8
        buf = [int(x, 16) for x in dumps[2 * i + 1].split()]
        print("\n%-24s %d glyph(s) outside a window" % (label, count))
        for k in range(min(count, REPORTS)):
            e = buf[k * ENTRY:(k + 1) * ENTRY]
            if len(e) < 9:
                break
            addr = e[0] | e[1] << 8 | e[2] << 16 | e[3] << 24
            print("    win %-2d font %-2d pen %-3d reached %-3d window %-3dpx  %s"
                  % (e[6], e[7], e[4], e[5], e[8] * 8, nearest(syms, addr)))


if __name__ == "__main__":
    main()
