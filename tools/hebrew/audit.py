# -*- coding: utf-8 -*-
"""Check every Hebrew string against the window that actually prints it.

    python3 tools/hebrew/audit.py

Reports four classes of defect the build cannot catch:

  * lines whose left edge falls outside the dialogue box
  * lines that clip once a player name or {STR_VAR_n} is substituted
  * item descriptions wider than their pane
  * text blocks with no $ terminator, which run on into the next label

Exits non-zero if anything is found, so it can gate a commit.
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as T
import substitutions

ROOT = T.ROOT
LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)::", re.M)
STRING = re.compile(r'^\s*\.string\s+"(.*)"\s*$')
HELP_FILE = os.path.join("data", "text", "help_system.inc")


def _script_files():
    for dirpath, _, names in os.walk(os.path.join(ROOT, "data")):
        if ".git" in dirpath:
            continue
        for name in sorted(names):
            if name.endswith((".inc", ".s")):
                yield os.path.join(dirpath, name)


def collect():
    """label -> [(relpath, lineno, raw string), ...]"""
    blocks, label = {}, None
    for path in _script_files():
        rel = os.path.relpath(path, ROOT)
        for lineno, line in enumerate(io.open(path, encoding="utf-8").read().split("\n"), 1):
            m = LABEL.match(line)
            if m:
                label = m.group(1)
                blocks.setdefault(label, [])
                continue
            s = STRING.match(line)
            if s and label:
                blocks[label].append((rel, lineno, s.group(1)))
    return blocks


# Script commands whose first argument is text for the overworld dialogue box.
# giveitem_msg and friends are easy to miss: they wrap msgreceiveditem, so the
# text goes to the same 26-tile window as a plain msgbox but the word "msgbox"
# never appears. braillemessage is deliberately absent -- it uses its own font.
DIALOGUE_COMMANDS = ("msgbox", "message", "giveitem_msg", "msgreceiveditem",
                     "giveitem_msg_animated", "finditem_msg")


def msgbox_labels():
    """Labels printed by a script into the overworld dialogue box."""
    used = set()
    pattern = re.compile(r"\s*(?:%s)\s+([A-Za-z_][A-Za-z0-9_]*)"
                         % "|".join(DIALOGUE_COMMANDS))
    for path in _script_files():
        for line in io.open(path, encoding="utf-8"):
            m = pattern.match(line)
            if m:
                used.add(m.group(1))
    return used


def lines_of(raw):
    for seg in re.split(r"\\n|\\l|\\p", raw.replace("$", "")):
        if seg.strip():
            yield seg


def check_dialogue(blocks, msg):
    """Lines in the 26-tile box, measured with and without substitutions.

    The second pass fills each {STR_VAR_n} with the widest thing that site can
    actually produce -- see substitutions.py -- because a species name, a
    nickname and an item name differ by 20px and measuring them all as the same
    thing either condemns good lines or passes clipping ones.
    """
    static, substituted = [], []
    for label, entries in blocks.items():
        if label not in msg:
            continue
        for rel, lineno, raw in entries:
            for seg in lines_of(raw):
                o = T.overhang(seg)
                if o is not None and o > 0:
                    static.append((o, rel, lineno, seg))
                    continue
                if "{" in seg:
                    filled, _ = substitutions.fill(seg, label, sys.modules[__name__])
                    o = T.overhang(filled)
                    if o is not None and o > 0:
                        substituted.append((o, rel, lineno, seg))
    return sorted(static, reverse=True), sorted(substituted, reverse=True)


def check_help(blocks):
    """The help system's own renderer and its 208px panel."""
    bad = []
    for label, entries in blocks.items():
        for rel, lineno, raw in entries:
            if rel != HELP_FILE:
                continue
            for seg in lines_of(raw):
                w = T.help_width(seg)
                if w is not None and w > 208:
                    bad.append((w - 208, rel, lineno, seg))
    return sorted(bad, reverse=True)


def check_move_descriptions():
    """Move descriptions go to two windows: the summary screen's move panel
    (src/pokemon_summary_screen.c prints them at x=107) and the move relearner's
    15-tile window. The summary panel is the tighter of the two -- measured on
    screen at about 121px usable, so a line fits when total - first <= 113."""
    path = os.path.join(ROOT, "src/move_descriptions.c")
    if not os.path.exists(path):
        return []
    text = io.open(path, encoding="utf-8").read()
    defn = re.compile(r'\b(gMoveDescription_[A-Za-z_0-9]*)\s*\[\s*\]\s*=\s*_\("((?:[^"\\]|\\.)*)"\)')
    bad = []
    for m in defn.finditer(text):
        for seg in re.split(r"\\n", m.group(2).replace("$", "")):
            if not seg.strip():
                continue
            o = T.overhang(seg, pen=107)
            if o is not None and o > 0:
                bad.append((o, m.group(1).replace("gMoveDescription_", ""), seg))
    return sorted(bad, reverse=True)


def check_items():
    path = os.path.join(ROOT, "src/data/items.json")
    if not os.path.exists(path):
        return []
    doc = json.load(io.open(path, encoding="utf-8"))
    items = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    bad = []
    for item in items:
        # The Hebrew text lives under the keys the English original used --
        # "english" and "description_english" -- because jsonproc emits those.
        # Reading a "description" key silently measures nothing.
        for seg in lines_of(item.get("description_english") or item.get("description") or ""):
            o = T.overhang(seg, pen=T.PEN_ITEM_DESC)
            if o is not None and o > 0:
                bad.append((o, item.get("english") or item.get("name", "?"), seg))
    return sorted(bad, reverse=True)


def check_terminators(blocks, msg):
    """A block with no $ anywhere never ends; the printer reads on into the
    bytes the assembler laid down after it, i.e. the next label's text."""
    bad = []
    for label, entries in blocks.items():
        if entries and not any("$" in raw for _, _, raw in entries):
            rel, lineno, _ = entries[0]
            bad.append((rel, lineno, label, label in msg))
    return sorted(bad)


def main():
    blocks, msg = collect(), msgbox_labels()
    static, subst = check_dialogue(blocks, msg)
    helps, items = check_help(blocks), check_items()
    unterminated = check_terminators(blocks, msg)
    problems = 0

    def section(title, rows, fmt):
        nonlocal problems
        print("%-52s %s" % (title, len(rows) if rows else "clean"))
        problems += len(rows)
        for row in rows[:20]:
            print("   " + fmt(row))
        if len(rows) > 20:
            print("   ... and %d more" % (len(rows) - 20))

    section("dialogue lines outside the 26-tile box", static,
            lambda r: "+%dpx %s:%d  %s" % r)
    section("dialogue lines that clip with a name filled in", subst,
            lambda r: "+%dpx %s:%d  %s" % r)
    section("help-system lines outside the 208px panel", helps,
            lambda r: "+%dpx %s:%d  %s" % r)
    section("item descriptions outside their pane", items,
            lambda r: "+%dpx %s  %s" % r)
    section("move descriptions outside the summary panel", check_move_descriptions(),
            lambda r: "+%dpx %s  %s" % r)
    section("text blocks with no $ terminator", unterminated,
            lambda r: "%s:%d  %s%s" % (r[0], r[1], r[2], "" if r[3] else "  (not via msgbox)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
