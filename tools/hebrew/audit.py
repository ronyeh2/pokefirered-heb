# -*- coding: utf-8 -*-
"""Check every Hebrew string against the window that actually prints it.

    python3 tools/hebrew/audit.py

Reports the classes of defect the build cannot catch:

  * lines whose left edge falls outside the dialogue box
  * lines that clip once a player name or {STR_VAR_n} is substituted
  * item descriptions wider than their pane
  * move descriptions wider than the summary screen's panel
  * battle text wider than the battle box
  * AddTextPrinter* call sites whose x cannot hold the string they print --
    an x of 0 or 2 is an upstream left inset that was never mirrored, and
    under RTL it leaves one glyph against the border and drops the rest
  * text blocks with no $ terminator, which run on into the next label

Number order is checked separately, by tools/hebrew/numbers.py: it needs a
checkout of the English pokefirered to compare against.

Exits non-zero if anything is found, so it can gate a commit.
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as T
import substitutions
import printers

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


def check_battle_box():
    """B_WIN_MSG is 28 tiles, so the battle box has 16px more than the
    overworld one -- and battle text is assembled from these strings."""
    path = os.path.join(ROOT, "src/battle_message.c")
    if not os.path.exists(path):
        return []
    text = io.open(path, encoding="utf-8").read()
    defn = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*\]\s*=\s*_\(((?:\s*"(?:[^"\\]|\\.)*"\s*)+)\)')
    lit = re.compile(r'"((?:[^"\\]|\\.)*)"')
    bad = []
    for m in defn.finditer(text):
        body = "".join(lit.findall(m.group(2)))
        for seg in lines_of(body):
            o = T.overhang(seg, pen=T.PEN_BATTLE_BOX)
            if o is not None and o > 0:
                bad.append((o, m.group(1), seg))
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


def move_name_pen():
    """The battle move list prints at sTextOnWindowsInfo_Normal[B_WIN_MOVE_NAME_1].x,
    which is where the first glyph lands and where the pen starts walking left.
    Read it from the source so a change to the slot width is picked up here."""
    g = io.open(os.path.join(ROOT, "include/constants/global.h"), encoding="utf-8").read()
    name_len = int(re.search(r"#define MOVE_NAME_LENGTH\s+(\d+)", g).group(1))
    b = io.open(os.path.join(ROOT, "src/battle_message.c"), encoding="utf-8").read()
    pad = int(re.search(r"\[B_WIN_MOVE_NAME_1\].*?\.x = 0 \+ MOVE_NAME_LENGTH \* 4 \+ (\d+)",
                        b, re.S).group(1))
    return name_len * 4 + pad


def check_move_names():
    """A move name wider than the slot does not smear -- currentX is a u8, so a
    clipped glyph wraps past zero and is blitted off-window. It just vanishes."""
    path = os.path.join(ROOT, "src/data/text/move_names.h")
    if not os.path.exists(path):
        return []
    pen = move_name_pen()
    text = io.open(path, encoding="utf-8").read()
    bad = []
    for mid, name in re.findall(r'\[(MOVE_\w+)\]\s*=\s*_\("([^"]*)"\)', text):
        o = T.overhang(name, pen=pen, font="small")
        if o is not None and o > 0:
            bad.append((o, mid, name))
    return sorted(bad, reverse=True)


def check_name_spacing():
    """A name is allowed to lose a space in its table -- the battle slot is 57px
    and prose has 200 -- but never the other way round. Prose written without a
    space the table keeps is just a typo, and it reads as one word in the box."""
    seps = "[ \u05be-]"
    names = []
    for rel in ("src/data/text/move_names.h", "src/data/text/abilities.h",
                "src/data/text/trainer_class_names.h"):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for key, val in re.findall(r'\[(\w+)\]\s*=\s*_\("([^"]*)"\)',
                                   io.open(path, encoding="utf-8").read()):
            if re.search(seps, val) and len(re.sub(seps, "", val)) >= 7:
                names.append((key, val))
    items_path = os.path.join(ROOT, "src/data/items.json")
    if os.path.exists(items_path):
        doc = json.load(io.open(items_path, encoding="utf-8"))
        for item in (doc["items"] if isinstance(doc, dict) and "items" in doc else doc):
            val = item.get("english") or ""
            if re.search(seps, val) and "{" not in val and len(re.sub(seps, "", val)) >= 7:
                names.append((item.get("itemId", "?"), val))
    # The same letters with the separators made optional, so only spacing differs.
    pats = [(key, val, re.compile("(?<![\u0590-\u05FF])(%s)(?![\u0590-\u05FF])" %
                                  ("%s*" % seps).join(re.escape(c)
                                                      for c in re.sub(seps, "", val))))
            for key, val in names]
    bad = []
    for rel in list(_script_files()) + ["src/move_descriptions.c", "src/strings.c"]:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for lineno, line in enumerate(io.open(path, encoding="utf-8",
                                              errors="replace"), 1):
            m = re.search(r'\.string "(.*)"|_\("(.*)"\)', line)
            if not m:
                continue
            body = m.group(1) or m.group(2) or ""
            for key, val, pat in pats:
                for found in pat.findall(body):
                    # Prose keeping a space the table dropped is fine and wanted.
                    if found != val and not re.search(seps, found):
                        bad.append((key, val, found, rel, lineno))
    return sorted(set(bad))


def check_empty_braces():
    """{} assembles to nothing. ReadBracketedConstants only errors on an unknown
    NAMED constant, so an empty one is silent -- which is how a TM number once
    went missing from a line that still built and still ran."""
    bad = []
    for path in _script_files():
        rel = os.path.relpath(path, ROOT)
        for lineno, line in enumerate(io.open(path, encoding="utf-8",
                                              errors="replace"), 1):
            if re.search(r'\.string\s+"[^"]*\{\}', line):
                bad.append((rel, lineno, line.strip()[:60]))
    return sorted(bad)


# Fields that are handed a runtime buffer, so printers.py cannot see what goes
# in them. Each entry says which table fills the buffer, and the pen is read
# from the call rather than copied, so moving the field moves the check.
_BUFFER_FIELDS = [
    ("summary: species name", "src/pokemon_summary_screen.c",
     r"speciesNameStrBuf", "src/data/text/species_names.h"),
    ("summary: item name", "src/pokemon_summary_screen.c",
     r"itemNameStrBuf", "items"),
    ("summary: move name", "src/pokemon_summary_screen.c",
     r"moveNameStrBufs\[i\]", "src/data/text/move_names.h"),
    ("summary: ability name", "src/pokemon_summary_screen.c",
     r"abilityNameStrBuf", "src/data/text/abilities.h"),
]


def _names_of(source):
    if source == "items":
        path = os.path.join(ROOT, "src/data/items.json")
        if not os.path.exists(path):
            return []
        doc = json.load(io.open(path, encoding="utf-8"))
        rows = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
        return [(i.get("itemId", "?"), i.get("english") or "") for i in rows]
    path = os.path.join(ROOT, source)
    if not os.path.exists(path):
        return []
    return re.findall(r'\[(\w+)\]\s*=\s*_\("([^"]*)"\)',
                      io.open(path, encoding="utf-8").read())


def check_name_fields():
    """A name printed from a buffer still has to fit the field it lands in."""
    bad = []
    for label, rel, buf, source in _BUFFER_FIELDS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding="utf-8").read()
        # This file keeps the pre-RTL calls around, commented out, with the old
        # x still in them. Measuring one of those measures nothing.
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r"//[^\n]*", "", text)
        m = re.search(r"^\s*AddTextPrinterParameterized3\([^;]*?,\s*FONT_(\w+),"
                      r"\s*(\d+)[^;]*?%s[^;]*?\);" % buf, text, re.M | re.S)
        if not m:
            bad.append((0, label, "no call site found"))
            continue
        font = "small" if m.group(1) == "SMALL" else "normal"
        pen = int(m.group(2))
        for key, name in _names_of(source):
            o = T.overhang(name, pen=pen, font=font)
            if o is not None and o > 0:
                bad.append((o, "%s (pen %d)" % (label, pen), "%s %s" % (key, name)))
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
    section("battle text outside the battle box", check_battle_box(),
            lambda r: "+%dpx %s  %s" % r)
    section("move names wider than the battle slot (%dpx)" % move_name_pen(),
            check_move_names(), lambda r: "+%dpx %s  %s" % r)
    section("prose missing a space the name table keeps", check_name_spacing(),
            lambda r: "%s  %s vs %s  %s:%d" % r)
    section("names too wide for the field they print into", check_name_fields(),
            lambda r: "+%dpx %s  %s" % r)
    section("strings carrying an empty {} (emits nothing)", check_empty_braces(),
            lambda r: "%s:%d  %s" % r)
    printer_rows, unresolved = printers.find()
    section("printer call sites whose x cannot hold the string", printer_rows,
            lambda r: "+%dpx %s:%d  x=%d  %s  %s" % r)
    print("%-52s %d (runtime buffers)" % ("   printer sites with an unresolvable string", unresolved))
    section("text blocks with no $ terminator", unterminated,
            lambda r: "%s:%d  %s%s" % (r[0], r[1], r[2], "" if r[3] else "  (not via msgbox)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
