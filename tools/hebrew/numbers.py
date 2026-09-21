# -*- coding: utf-8 -*-
"""Check (or fix) the digit order of number literals in Hebrew text.

    python3 tools/hebrew/numbers.py            # report
    python3 tools/hebrew/numbers.py --fix      # rewrite the offenders in place

The renderer draws a string glyph by glyph from right to left, so the source's
first character ends up furthest right: a number has to be written backwards to
read correctly on screen, and "052 steps" is what puts "250 steps" in the box.
Numbers built at runtime are already handled -- ConvertIntToDecimalStringN ends
in a strrev -- so only literals in the text are at risk, and nothing about a
literal on its own says which way round it is.

pret/pokefirered has the same strings, matched by identifier or by label, with
the numbers the right way round. So: pull the digit runs out of both, line them
up, and any Hebrew run that still equals its English counterpart (and is not a
palindrome) was never reversed and renders backwards.

Point --english at a pokefirered checkout:

    git clone --depth 1 --filter=blob:none --sparse https://github.com/pret/pokefirered /tmp/pokefirered-en
    git -C /tmp/pokefirered-en sparse-checkout set src data
"""
import io, os, re, sys, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EN_DEFAULT = "/tmp/pokefirered-en"

HEB = re.compile(r"[֐-׿]")
RUN = re.compile(r"[0-9][0-9,]*[0-9]|[0-9]")
BRACE = re.compile(r"\{[^}]*\}")
CDEF = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*[A-Za-z0-9_]*\s*\]\s*=\s*_\(\s*((?:\s*"(?:[^"\\]|\\.)*"\s*)+)\)')
LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)::")


def runs(s):
    """Digit runs outside {...}; control codes carry hex operands of their own."""
    return RUN.findall(BRACE.sub(" ", s))


def _c_defs(root):
    out = {}
    for path in sorted(glob.glob(os.path.join(root, "src", "**", "*.c"), recursive=True)
                       + glob.glob(os.path.join(root, "src", "**", "*.h"), recursive=True)):
        text = re.sub(r"/\*.*?\*/", "", io.open(path, encoding="utf-8", errors="replace").read(), flags=re.S)
        for m in CDEF.finditer(text):
            out.setdefault(m.group(1), ("".join(LIT.findall(m.group(2))), path,
                                        text[:m.start()].count("\n") + 1))
    return out


def _inc_defs(root):
    out = {}
    for path in sorted(glob.glob(os.path.join(root, "data", "**", "*.inc"), recursive=True)
                       + glob.glob(os.path.join(root, "data", "**", "*.s"), recursive=True)):
        label, buf, start = None, [], 0
        for i, line in enumerate(io.open(path, encoding="utf-8", errors="replace"), 1):
            m = LABEL.match(line)
            if m:
                if label:
                    out.setdefault(label, ("".join(buf), path, start))
                label, buf, start = m.group(1), [], i
                continue
            s = re.match(r'^\s*\.string\s+"(.*)"\s*$', line.rstrip("\n"))
            if s and label:
                buf.append(s.group(1))
        if label:
            out.setdefault(label, ("".join(buf), path, start))
    return out


def _items(root):
    path = os.path.join(root, "src/data/items.json")
    doc = json.load(io.open(path, encoding="utf-8"))
    lst = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    out = {}
    for i, it in enumerate(lst):
        for key in ("english", "description_english"):
            out["item%d.%s" % (i, key)] = (it.get(key) or "", path, i)
    return out


def decisions(heb, en):
    """name -> set of run indices that are still in English order."""
    out = {}
    for name, (hs, _, _) in heb.items():
        if not HEB.search(hs) or name not in en:
            continue
        hr, er = runs(hs), runs(en[name][0])
        if len(hr) != len(er):
            continue        # the sentence was rewritten; a positional match would be guesswork
        flagged = {i for i, (a, b) in enumerate(zip(hr, er))
                   if len(a) > 1 and a != a[::-1] and a == b}
        if flagged:
            out[name] = flagged
    return out


def rewrite(s, flagged, counter):
    """Reverse the flagged runs of s, continuing the label's run numbering."""
    out, i = [], 0
    for m in re.finditer(r"\{[^}]*\}|[0-9][0-9,]*[0-9]|[0-9]", s):
        out.append(s[i:m.start()])
        tok = m.group(0)
        if tok.startswith("{"):
            out.append(tok)
        else:
            out.append(tok[::-1] if counter[0] in flagged else tok)
            counter[0] += 1
        i = m.end()
    out.append(s[i:])
    return "".join(out)


def fix_c_and_inc(defs, dec, fix):
    touched = {}
    for name, flagged in sorted(dec.items()):
        body, path, line = defs[name]
        print("%-44s %-38s %s" % ("%s:%d" % (os.path.relpath(path, ROOT), line), name[:38],
                                  " ".join(sorted({runs(body)[i] for i in flagged}))))
        if not fix:
            continue
        text = touched.get(path) or io.open(path, encoding="utf-8").read()
        counter = [0]
        if path.endswith((".inc", ".s")):
            lines, inside, new = text.split("\n"), False, []
            for ln in lines:
                m = LABEL.match(ln)
                if m:
                    inside = (m.group(1) == name)
                    new.append(ln)
                    continue
                s = re.match(r'^(\s*\.string\s+")(.*)("\s*)$', ln)
                if inside and s:
                    new.append(s.group(1) + rewrite(s.group(2), flagged, counter) + s.group(3))
                else:
                    new.append(ln)
            text = "\n".join(new)
        else:
            m = CDEF.search(text, 0)
            while m and m.group(1) != name:
                m = CDEF.search(text, m.end())
            if not m:
                sys.exit("lost the definition of %s in %s" % (name, path))
            block = m.group(2)
            new_block = re.sub(r'"((?:[^"\\]|\\.)*)"',
                               lambda lm: '"%s"' % rewrite(lm.group(1), flagged, counter), block)
            text = text[:m.start(2)] + new_block + text[m.end(2):]
        touched[path] = text
    for path, text in touched.items():
        io.open(path, "w", encoding="utf-8").write(text)
    return len(dec)


def fix_items(defs, dec, fix):
    """Rewrite by file offset, not by search-and-replace: the TM names differ
    only in their two digits, so replacing the first match of "TM 01" would
    find the "TM 10" written a moment earlier and undo it."""
    path = os.path.join(ROOT, "src/data/items.json")
    raw = io.open(path, encoding="utf-8").read()
    slots = {}
    seen = {"english": 0, "description_english": 0}
    for m in re.finditer(r'"(english|description_english)"\s*:\s*("(?:[^"\\]|\\.)*")', raw):
        key = m.group(1)
        slots["item%d.%s" % (seen[key], key)] = (m.start(2), m.end(2))
        seen[key] += 1

    edits = []
    for name, flagged in sorted(dec.items()):
        old = defs[name][0]
        new = rewrite(old, flagged, [0])
        label = defs.get(name.rsplit(".", 1)[0] + ".english", ("?",))[0]
        print("%-44s %-38s %s -> %s" % ("src/data/items.json", label[:38],
                                        " ".join(sorted({runs(old)[i] for i in flagged})),
                                        " ".join(sorted({runs(new)[i] for i in flagged}))))
        if fix:
            if name not in slots:
                sys.exit("cannot locate %s in items.json" % name)
            start, end = slots[name]
            edits.append((start, end, json.dumps(new, ensure_ascii=False)))

    for start, end, text in sorted(edits, reverse=True):
        raw = raw[:start] + text + raw[end:]
    if fix and edits:
        io.open(path, "w", encoding="utf-8").write(raw)
    return len(dec)


def main():
    fix = "--fix" in sys.argv
    en_root = EN_DEFAULT
    if "--english" in sys.argv:
        en_root = sys.argv[sys.argv.index("--english") + 1]
    if not os.path.isdir(os.path.join(en_root, "src")):
        raise SystemExit("no English checkout at %s -- see this file's docstring" % en_root)

    n = 0
    for loader in (_c_defs, _inc_defs):
        heb, en = loader(ROOT), loader(en_root)
        n += fix_c_and_inc(heb, decisions(heb, en), fix)
    heb, en = _items(ROOT), _items(en_root)
    n += fix_items(heb, decisions(heb, en), fix)
    print("\n%d string%s with a number still in English order" % (n, "" if n == 1 else "s"))
    return 1 if n and not fix else 0


if __name__ == "__main__":
    sys.exit(main())
