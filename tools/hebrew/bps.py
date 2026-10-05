# -*- coding: utf-8 -*-
"""Make and check a BPS patch between two ROMs.

    python3 tools/hebrew/bps.py make  BASE.gba TARGET.gba OUT.bps
    python3 tools/hebrew/bps.py apply BASE.gba OUT.bps  RESULT.gba
    python3 tools/hebrew/bps.py check BASE.gba OUT.bps  TARGET.gba

A patch carries the difference between the two, not either of them, which is
how a translation is distributed without shipping the game it patches. The base
this fork patches is FireRed rev 0, and the decomp builds that from source as
well -- there is no need to find a copy of it anywhere:

    git worktree add --detach /tmp/base <the commit before the Hebrew work>
    cp -R tools/agbcc /tmp/base/tools/agbcc
    make -C /tmp/base            # sha1 41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc

The encoder has to find moved data, not just data that changed in place. A
translation shifts everything after each edit, so a run that is byte-identical
to the original at a different offset is the common case -- emitting those as
literals would copy the original game's own bytes into the patch, which is the
one thing a patch exists not to do. Measured on this fork: 17 of the 25 longest
literal runs a same-offset-only encoder produced appear verbatim elsewhere in
the base. So the source is indexed and matches are emitted as SourceCopy.

`check` applies the result and compares byte for byte, which is the only
statement about a patch worth making.
"""
import sys, zlib

MAGIC = b"BPS1"


def write_varint(out, n):
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return
        out.append(x)
        n -= 1


def read_varint(data, pos):
    result, shift = 0, 1
    while True:
        b = data[pos]; pos += 1
        result += (b & 0x7F) * shift
        if b & 0x80:
            return result, pos
        shift <<= 7
        result += shift


BLOCK = 24          # bytes that must match before a candidate is extended
STRIDE = 16         # how finely the source is indexed
MIN_COPY = 20       # shorter than this and a literal run is cheaper
MAX_CANDIDATES = 8


def build_index(src):
    idx = {}
    for o in range(0, len(src) - BLOCK, STRIDE):
        idx.setdefault(hash(src[o:o + BLOCK]), []).append(o)
    return idx


def run_length(a, ao, b, bo, limit):
    """How many bytes of a[ao:] and b[bo:] agree, compared in chunks."""
    n = 0
    while n < limit:
        step = min(4096, limit - n)
        if a[ao + n:ao + n + step] == b[bo + n:bo + n + step]:
            n += step
            continue
        lo, hi = 0, step
        while lo < hi:                       # first differing byte in this chunk
            mid = (lo + hi) // 2
            if a[ao + n:ao + n + mid + 1] == b[bo + n:bo + n + mid + 1]:
                lo = mid + 1
            else:
                hi = mid
        return n + lo
    return n


def make(base, target):
    idx = build_index(base)
    out = bytearray(MAGIC)
    write_varint(out, len(base))
    write_varint(out, len(target))
    write_varint(out, 0)                      # no metadata

    literals = bytearray()

    def flush():
        if literals:
            write_varint(out, ((len(literals) - 1) << 2) | 1)   # TargetRead
            out.extend(literals)
            del literals[:]

    i, n, src_rel = 0, len(target), 0
    while i < n:
        if i < len(base) and base[i] == target[i]:
            length = run_length(base, i, target, i, min(len(base), n) - i)
            flush()
            write_varint(out, ((length - 1) << 2) | 0)         # SourceRead
            i += length
            continue

        best_len, best_at = 0, 0
        if i + BLOCK <= n:
            for m in idx.get(hash(target[i:i + BLOCK]), ())[:MAX_CANDIDATES]:
                if base[m:m + BLOCK] != target[i:i + BLOCK]:
                    continue
                length = BLOCK + run_length(base, m + BLOCK, target, i + BLOCK,
                                            min(len(base) - m, n - i) - BLOCK)
                if length > best_len:
                    best_len, best_at = length, m

        if best_len >= MIN_COPY:
            flush()
            write_varint(out, ((best_len - 1) << 2) | 2)       # SourceCopy
            delta = best_at - src_rel
            write_varint(out, (abs(delta) << 1) | (1 if delta < 0 else 0))
            src_rel = best_at + best_len
            i += best_len
        else:
            literals.append(target[i])
            i += 1
    flush()

    out += (zlib.crc32(base) & 0xFFFFFFFF).to_bytes(4, "little")
    out += (zlib.crc32(target) & 0xFFFFFFFF).to_bytes(4, "little")
    out += (zlib.crc32(bytes(out)) & 0xFFFFFFFF).to_bytes(4, "little")
    return bytes(out)


def apply(base, patch):
    if patch[:4] != MAGIC:
        raise SystemExit("not a BPS patch")
    if zlib.crc32(patch[:-4]) & 0xFFFFFFFF != int.from_bytes(patch[-4:], "little"):
        raise SystemExit("patch is corrupt (its own checksum does not match)")
    if zlib.crc32(base) & 0xFFFFFFFF != int.from_bytes(patch[-12:-8], "little"):
        raise SystemExit("this is not the base the patch was made against")

    pos = 4
    src_size, pos = read_varint(patch, pos)
    tgt_size, pos = read_varint(patch, pos)
    meta_size, pos = read_varint(patch, pos)
    pos += meta_size
    if len(base) != src_size:
        raise SystemExit("base is %d bytes, patch expects %d" % (len(base), src_size))

    out = bytearray(tgt_size)
    o = src_rel = tgt_rel = 0
    end = len(patch) - 12
    while pos < end:
        data, pos = read_varint(patch, pos)
        cmd, length = data & 3, (data >> 2) + 1
        if cmd == 0:
            out[o:o + length] = base[o:o + length]; o += length
        elif cmd == 1:
            out[o:o + length] = patch[pos:pos + length]; pos += length; o += length
        else:
            delta, pos = read_varint(patch, pos)
            delta = (delta >> 1) * (-1 if delta & 1 else 1)
            if cmd == 2:
                src_rel += delta
                for _ in range(length):
                    out[o] = base[src_rel]; o += 1; src_rel += 1
            else:
                tgt_rel += delta
                for _ in range(length):
                    out[o] = out[tgt_rel]; o += 1; tgt_rel += 1
    if zlib.crc32(bytes(out)) & 0xFFFFFFFF != int.from_bytes(patch[-8:-4], "little"):
        raise SystemExit("patched result does not match the patch's own checksum")
    return bytes(out)


def main():
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    mode, a, b, c = sys.argv[1:5]
    if mode == "make":
        patch = make(open(a, "rb").read(), open(b, "rb").read())
        open(c, "wb").write(patch)
        print("%s  %d bytes" % (c, len(patch)))
    elif mode == "apply":
        open(c, "wb").write(apply(open(a, "rb").read(), open(b, "rb").read()))
        print("wrote %s" % c)
    elif mode == "check":
        got = apply(open(a, "rb").read(), open(b, "rb").read())
        want = open(c, "rb").read()
        if got != want:
            raise SystemExit("MISMATCH: patched base is not the target")
        print("ok: patching %s reproduces %s byte for byte" % (a, c))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
