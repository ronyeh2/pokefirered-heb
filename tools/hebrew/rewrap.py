# -*- coding: utf-8 -*-
"""Re-wrap dialogue pages that audit.py reports as clipping.

    python3 tools/hebrew/rewrap.py            # show what would change
    python3 tools/hebrew/rewrap.py --apply

Only blocks a script prints with msgbox/message are touched: everything else
goes to a window whose geometry is decided at the call site in C, so wrapping it
against the dialogue box's budget would be wrong.

Within a page the words are re-flowed greedily -- first line, \\n second line,
\\l for each line after that, which is how the engine scrolls. A page is left
exactly as it is if any of it cannot be measured ({FONT_*}, {PLAY_BGM}, keypad
icons), because guessing there would corrupt working text. Control codes that
carry space-separated arguments, such as {COLOR_HIGHLIGHT_SHADOW 13 14 15},
are kept whole.

This only moves line breaks. It never rewrites wording -- a line that no wrap
can fix is reported for a human to shorten.
"""
import io, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as T
import audit

BLOCK = re.compile(r'((?:^[ \t]*\.string[ \t]+"(?:[^"\\]|\\.)*"[ \t]*\n)+)', re.M)
STRING = re.compile(r'^([ \t]*)\.string[ \t]+"((?:[^"\\]|\\.)*)"[ \t]*$', re.M)
LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)::", re.M)


def owner(text, pos):
    seen = [m for m in LABEL.finditer(text) if m.start() < pos]
    return seen[-1].group(1) if seen else None


def measure(line):
    return T.overhang(line, placeholders=True)


def fits(line):
    o = measure(line)
    return o is not None and o <= 0


def tokens(line):
    """Split on spaces, keeping {...} groups whole."""
    out, buf, depth = [], "", 0
    for ch in line:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        if ch == " " and depth == 0:
            if buf:
                out.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def wrap(words):
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w) if cur else w
        if measure(cand) is None:
            return None
        if fits(cand) or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rebuild(page_lines):
    out = page_lines[0]
    if len(page_lines) > 1:
        out += r"\n" + page_lines[1]
    for extra in page_lines[2:]:
        out += r"\l" + extra
    return out


def process(path, msg, apply):
    text = io.open(path, encoding="utf-8").read()
    edits, stuck = [], []
    for block in BLOCK.finditer(text):
        if owner(text, block.start()) not in msg:
            continue
        parts = STRING.findall(block.group(1))
        if not parts:
            continue
        indent = parts[0][0]
        joined = "".join(p[1] for p in parts)
        terminated = joined.endswith("$")
        body = joined[:-1] if terminated else joined
        pages, touched = [], False
        for page in body.split(r"\p"):
            segs = re.split(r"\\n|\\l", page)
            measured = [measure(s.replace("$", "")) for s in segs]
            if any(m is None for m in measured):
                pages.append(page)
                continue
            if not any(m > 0 for m in measured):
                pages.append(page)
                continue
            new = wrap(tokens(" ".join(segs)))
            if not new or any(not fits(l) for l in new):
                stuck += [(m, s) for s, m in zip(segs, measured) if m > 0]
                pages.append(page)
                continue
            pages.append(rebuild(new))
            touched = True
        if not touched:
            continue
        joined = r"\p".join(pages) + ("$" if terminated else "")
        lines, buf = [], ""
        for piece in re.split(r"(\\n|\\l|\\p)", joined):
            buf += piece
            if piece in (r"\n", r"\l", r"\p"):
                lines.append(buf)
                buf = ""
        if buf:
            lines.append(buf)
        edits.append((block.start(), block.end(),
                      "".join('%s.string "%s"\n' % (indent, l) for l in lines)))
    if edits and apply:
        out, prev = [], 0
        for start, end, new in edits:
            out.append(text[prev:start])
            out.append(new)
            prev = end
        out.append(text[prev:])
        io.open(path, "w", encoding="utf-8").write("".join(out))
    return edits, stuck


def main():
    apply = "--apply" in sys.argv
    msg = audit.msgbox_labels()
    total, stuck = 0, []
    for path in audit._script_files():
        edits, s = process(path, msg, apply)
        stuck += s
        if edits:
            print("%2d block(s)  %s" % (len(edits), os.path.relpath(path, T.ROOT)))
            total += len(edits)
    print("%s %d block(s)" % ("re-wrapped" if apply else "would re-wrap", total))
    if stuck:
        print("\n%d line(s) no wrap can fix -- shorten the wording:" % len(set(stuck)))
        for over, line in sorted(set(stuck), reverse=True)[:15]:
            print("   +%dpx  %s" % (over, line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
