# -*- coding: utf-8 -*-
"""AddTextPrinter* sites with a literal x, checked against the RTL pen budget.

For a right-to-left print the pen budget IS x: the first glyph is blitted at x
and the pen then walks left, so a run needs (total - first) <= x pixels to its
left. That makes the left-edge check exact with no knowledge of the window.

Resolves three kinds of string argument:
  * a literal or a named const u8 [] = _("...")
  * an array of pointers indexed at runtime -- every element is measured
  * gStringVar4, back to the nearest StringExpandPlaceholders/StringCopy source
    in the same function (that is where the site's real text comes from)
"""
import io, os, re, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as T
ROOT = T.ROOT

SIGS = {"AddTextPrinterParameterized":  (3, 2),
        "AddTextPrinterParameterized3": (2, 6),
        "AddTextPrinterParameterized4": (2, 8),
        "AddTextPrinterParameterized5": (3, 2)}
CALL = re.compile(r"\b(AddTextPrinterParameterized[345]?)\s*\(")
LITERAL = re.compile(r'"((?:[^"\\]|\\.)*)"')
HEB = re.compile(r"[֐-׿]")


def blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", blank, s, flags=re.S)
    return re.sub(r"//[^\n]*", blank, s)


def split_args(text, start):
    depth, i, args, cur = 0, start, [], []
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
            if depth == 1:
                i += 1
                continue
        elif c == ")":
            depth -= 1
            if depth == 0:
                args.append("".join(cur).strip())
                return args
        elif c == "," and depth == 1:
            args.append("".join(cur).strip()); cur = []; i += 1; continue
        cur.append(c); i += 1
    return None


SRCS = sorted(set(glob.glob(os.path.join(ROOT, "src", "**", "*.c"), recursive=True)
                  + glob.glob(os.path.join(ROOT, "src", "**", "*.h"), recursive=True)
                  + glob.glob(os.path.join(ROOT, "include", "**", "*.h"), recursive=True)))
TEXTS = {p: strip_comments(io.open(p, encoding="utf-8", errors="replace").read()) for p in SRCS}

STRDEF = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*[A-Za-z0-9_]*\s*\]\s*=\s*"
                    r"(?:_\(\s*)?((?:\s*\"(?:[^\"\\]|\\.)*\"\s*)+)\)?", re.M)
# const u8 *const sFoo[] = { gTextA, gTextB };  and  [IDX] = gTextC,
ARRDEF = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[[^\];]*\]\s*(?:\[[^\];]*\]\s*)?=\s*\{(.*?)\n\}\s*;", re.S)

# Per-file first, global second: a static name like sMessages or sRecordsTexts
# exists in several files, and resolving it globally attributes one screen's
# strings to another screen's window.
STRINGS, ARRAYS = {}, {}
LOCAL_STRINGS, LOCAL_ARRAYS = {}, {}
for p, t in TEXTS.items():
    ls, la = {}, {}
    for m in STRDEF.finditer(t):
        parts = LITERAL.findall(m.group(2))
        if parts:
            ls[m.group(1)] = "".join(parts)
            STRINGS.setdefault(m.group(1), "".join(parts))
    for m in ARRDEF.finditer(t):
        body = m.group(2)
        names = re.findall(r"\b(g[A-Za-z0-9_]*Text[A-Za-z0-9_]*|gText_[A-Za-z0-9_]+|s[A-Za-z0-9_]*)\b", body)
        lits = LITERAL.findall(body)
        la[m.group(1)] = (names, lits)
        ARRAYS.setdefault(m.group(1), (names, lits))
    LOCAL_STRINGS[p], LOCAL_ARRAYS[p] = ls, la


def const_value(expr):
    expr = expr.strip()
    if re.fullmatch(r"-?\d+", expr):
        return int(expr)
    if re.fullmatch(r"0[xX][0-9a-fA-F]+", expr):
        return int(expr, 16)
    if re.fullmatch(r"[\d\s\*\+\-/xXa-fA-F()]+", expr) and re.search(r"\d", expr):
        try:
            return int(eval(expr, {"__builtins__": {}}, {}))
        except Exception:
            return None
    return None


def resolve(sarg, text, at, path):
    """-> list of (label, string) candidates this argument can hold."""
    out = []
    lit = LITERAL.findall(sarg)
    if lit and sarg.lstrip().startswith(("_(", '"')):
        return [("<literal>", "".join(lit))]
    strings = dict(STRINGS); strings.update(LOCAL_STRINGS.get(path, {}))
    arrays = dict(ARRAYS); arrays.update(LOCAL_ARRAYS.get(path, {}))
    ident = re.fullmatch(r"&?([A-Za-z_][A-Za-z0-9_]*)(?:\s*\[\s*\d+\s*\])?", sarg.strip())
    if ident and ident.group(1) in strings:
        return [(ident.group(1), strings[ident.group(1)])]
    # an array indexed at runtime: measure every element
    arr = re.match(r"&?([A-Za-z_][A-Za-z0-9_]*)\s*\[", sarg.strip())
    if arr and arr.group(1) in arrays:
        names, lits = arrays[arr.group(1)]
        for n in names:
            if n in strings:
                out.append(("%s[]->%s" % (arr.group(1), n), strings[n]))
        for i, s in enumerate(lits):
            out.append(("%s[%d]" % (arr.group(1), i), s))
        if out:
            return out
    # gStringVar4: whatever the nearest preceding expansion put in it
    if sarg.strip() == "gStringVar4":
        window = text[max(0, at - 4000):at]
        srcs = re.findall(r"String(?:ExpandPlaceholders|Copy)\s*\(\s*gStringVar4\s*,\s*([A-Za-z_][A-Za-z0-9_]*)", window)
        for n in reversed(srcs):
            if n in strings:
                return [("gStringVar4<-%s" % n, strings[n])]
    return out


def find():
    """-> ([(overhang, relpath, line, x, label, line_text)], unresolvable_sites)"""
    rows, unresolved = [], 0
    for path in sorted(glob.glob(os.path.join(ROOT, "src", "*.c"))):
        text = TEXTS[path]
        rel = os.path.relpath(path, ROOT)
        for m in CALL.finditer(text):
            xi, si = SIGS[m.group(1)]
            args = split_args(text, m.end() - 1)
            if not args or len(args) <= max(xi, si):
                continue
            x = const_value(args[xi])
            if x is None:
                continue
            cands = resolve(args[si], text, m.start(), path)
            if not cands:
                unresolved += 1
                if os.environ.get("SHOW_UNRESOLVED"):
                    print("UNRESOLVED %s:%d x=%s  %s"
                          % (rel, text[:m.start()].count("\n") + 1, x, args[si][:60]))
                continue
            line = text[:m.start()].count("\n") + 1
            for label, body in cands:
                if not HEB.search(body):
                    continue
                for seg in re.split(r"\\n|\\l|\\p", body.replace("$", "")):
                    if not seg.strip():
                        continue
                    o = T.overhang(seg, pen=x)
                    if o is not None and o > 0:
                        rows.append((o, rel, line, x, label, seg))
    seen, uniq = set(), []
    for r in sorted(rows, reverse=True):
        k = (r[1], r[2], r[5])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    return uniq, unresolved


if __name__ == "__main__":
    found, unresolved = find()
    for o, rel, line, x, label, seg in found:
        print("+%-4dpx  %-42s x=%-4d %-34s %s" % (o, "%s:%d" % (rel, line), x, label[:34], seg))
    print("\n%d overflowing lines at %d sites; %d sites still unresolvable"
          % (len(found), len({(r[1], r[2]) for r in found}), unresolved))
    sys.exit(1 if found else 0)
