# -*- coding: utf-8 -*-
"""Produce the Hebrew ROM in one command.

    python3 tools/hebrew/getrom.py path/to/firered.gba     # you have a FireRed rev 0 ROM
    python3 tools/hebrew/getrom.py --build-base            # you do not; build it from source

The first form needs nothing but Python: the patch carries the translation, and
applying it to a FireRed rev 0 ROM gives the same bytes a full build does. The
second form builds that base out of this repository's own history -- the commit
before the Hebrew work began is still English FireRed, and a decompilation
builds its ROM from source -- which takes a toolchain and a few minutes.

The patch comes from the latest release unless a .bps is already sitting in the
repository root or given with --patch. Nothing is trusted on the way through:
the base is checked against its SHA-1 before use, the patch checks the base's
CRC32 itself and refuses any other, and the result is checked against the
CRC32 the patch records for it.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE_SHA1 = "41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc"   # FireRed rev 0
BASE_COMMIT = "d61f95945"                                 # last commit before the Hebrew work
RELEASE_API = "https://api.github.com/repos/ronyeh2/pokefirered-heb/releases/latest"


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_base(where):
    """Build English FireRed rev 0 out of this repository's own history."""
    rom = os.path.join(where, "pokefirered.gba")
    if os.path.exists(rom) and sha1(rom) == BASE_SHA1:
        print("base already built at %s" % rom)
        return rom
    if not os.path.isdir(os.path.join(ROOT, "tools/agbcc/bin")):
        raise SystemExit("agbcc is not installed in this clone -- see README, step 2")
    if not os.path.isdir(where):
        print("checking out %s (English FireRed) into %s" % (BASE_COMMIT, where))
        subprocess.run(["git", "-C", ROOT, "worktree", "add", "--detach", where, BASE_COMMIT],
                       check=True)
    if not os.path.isdir(os.path.join(where, "tools/agbcc/bin")):
        shutil.copytree(os.path.join(ROOT, "tools/agbcc"), os.path.join(where, "tools/agbcc"))
    jobs = str(os.cpu_count() or 2)
    print("building the base ROM -- this takes a few minutes")
    subprocess.run(["make", "-C", where, "-j" + jobs], check=True)
    got = sha1(rom)
    if got != BASE_SHA1:
        raise SystemExit("built base is %s, expected %s" % (got, BASE_SHA1))
    return rom


def find_patch(explicit):
    if explicit:
        return explicit
    local = [f for f in os.listdir(ROOT) if f.endswith(".bps")]
    if local:
        print("using %s" % local[0])
        return os.path.join(ROOT, local[0])
    print("fetching the patch from the latest release")
    with urllib.request.urlopen(RELEASE_API) as r:
        release = json.load(r)
    for asset in release.get("assets", []):
        if asset["name"].endswith(".bps"):
            dest = os.path.join(ROOT, asset["name"])
            urllib.request.urlretrieve(asset["browser_download_url"], dest)
            print("got %s (%s)" % (asset["name"], release.get("tag_name", "?")))
            return dest
    raise SystemExit("the latest release has no .bps attached -- pass one with --patch")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", nargs="?", help="a FireRed rev 0 ROM (sha1 %s)" % BASE_SHA1)
    ap.add_argument("--build-base", action="store_true",
                    help="build that ROM from source instead of supplying one")
    ap.add_argument("--patch", help="a .bps to apply (default: the latest release's)")
    ap.add_argument("-o", "--out", default=os.path.join(ROOT, "pokefirered-heb.gba"))
    args = ap.parse_args()

    if args.base:
        got = sha1(args.base)
        if got != BASE_SHA1:
            raise SystemExit(
                "%s is sha1 %s.\nThis patch applies to FireRed rev 0, sha1 %s.\n"
                "Run with --build-base to build that from source instead."
                % (args.base, got, BASE_SHA1))
        base = args.base
    elif args.build_base:
        base = build_base(os.path.join(ROOT, os.pardir, "pokefirered-base"))
    else:
        ap.error("give a FireRed rev 0 ROM, or --build-base to build one")

    out = bps.apply(open(base, "rb").read(), open(find_patch(args.patch), "rb").read())
    with open(args.out, "wb") as f:
        f.write(out)
    print("\n%s\n%s  %d bytes" % (args.out, sha1(args.out), len(out)))
    print("Checked: the patch verified the base it was given and its own result.")


if __name__ == "__main__":
    main()
