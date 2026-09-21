# -*- coding: utf-8 -*-
"""What can actually land in a {STR_VAR_n} at each place it is used.

A line holding {STR_VAR_1} cannot be measured without knowing what goes in it,
and the answer differs per site: a species name is at most 60px, a nickname 70,
an item name 81, a fishing record about 50, a level counter 12. Measuring every
site against the widest of those wrongly condemns lines that are fine; measuring
against the narrowest ships lines that clip the moment someone has a long
nickname.

So the source is traced. Scripts say what they buffer, and `call`ed subroutines
are followed, which covers most sites. The rest are filled by C -- the day care,
the fishing-record houses, the fan club -- and those are listed in OVERRIDE,
each one read out of the code that writes it.

{PLAYER} and {RIVAL} are budgeted at 7 glyphs of the widest Hebrew letter, 49px.
That really is the worst case: PLAYER_NAME_LENGTH is 7, and although the naming
keyboard also offers lowercase Latin, every Latin glyph is 6px flat with no
wide-letter padding, so 7 Hebrew wide letters beat them.
"""
import io
import json
import os
import re

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as T

NICK = "ש" * 10                 # POKEMON_NAME_LENGTH
SIZE = "9" * 6 + ".9"           # FormatMonSizeRecord: digits, '.', one decimal
PLAYER = "ש" * 7                # PLAYER_NAME_LENGTH

# Vars written by C rather than by a script command, resolved by reading the
# code that writes them (src/daycare.c, src/pokemon_size_record.c).
OVERRIDE = {
    "DayCare_Text_YourMonHasGrownXLevels": {"STR_VAR_1": NICK, "STR_VAR_2": "99"},
    "DayCare_Text_OweMeXForMonsReturn":    {"STR_VAR_1": NICK, "STR_VAR_2": "99999"},
    "DayCare_Text_WellRaiseYourMon":       {"STR_VAR_1": NICK},
    "DayCare_Text_TookBackMon":            {"STR_VAR_1": NICK},
    "DayCare_Text_YourMonIsDoingFine":     {"STR_VAR_1": NICK},
    "DayCare_Text_ItWillCostX":            {"STR_VAR_1": NICK, "STR_VAR_2": "99999"},
    "Route5_PokemonDayCare_Text_MonGrewToLevel": {"STR_VAR_2": "99"},
    "SixIsland_WaterPath_House1_Text_ItsXInchesSameAsBefore":      {"STR_VAR_2": SIZE},
    "SixIsland_WaterPath_House1_Text_ItsXInchesYInchesWasBiggest": {"STR_VAR_2": SIZE, "STR_VAR_3": SIZE},
    "SixIsland_WaterPath_House1_Text_ItsXInchesDeserveReward":     {"STR_VAR_2": SIZE},
    "SixIsland_WaterPath_House1_Text_BiggestHeracrossIsXInches":   {"STR_VAR_3": SIZE},
    "Route12_FishingHouse_Text_HmmXInchesDoesntMeasureUp":         {"STR_VAR_2": SIZE, "STR_VAR_3": SIZE},
    "Route12_FishingHouse_Text_WhoaXInchesTakeThis":               {"STR_VAR_2": SIZE},
    "Route12_FishingHouse_Text_HuhXInchesSameSizeAsLast":          {"STR_VAR_2": SIZE},
    "Route12_FishingHouse_Text_MostGiganticMagikarpXInches":       {"STR_VAR_3": SIZE},
}

BUFFER = re.compile(r"^\s*(buffer[a-z]+)\s+(STR_VAR_[123])")
DIALOGUE = None          # filled in lazily from audit.DIALOGUE_COMMANDS
CALLS = re.compile(r"^\s*(?:call|goto)\s+([A-Za-z_][A-Za-z0-9_]*)")
LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)::")


def _widest(strings):
    best = (0, "")
    for s in strings:
        w = T.width(s)
        if w and w > best[0]:
            best = (w, s)
    return best[1]


def _names(path):
    return re.findall(r'_\("([^"]*)"\)', io.open(path, encoding="utf-8").read())


def _categories():
    root = T.ROOT
    species = _widest(_names(os.path.join(root, "src/data/text/species_names.h")))
    move = _widest(_names(os.path.join(root, "src/data/text/move_names.h")))
    doc = json.load(io.open(os.path.join(root, "src/data/items.json"), encoding="utf-8"))
    items = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    item = _widest([i.get("english", "") for i in items])
    return {"bufferspeciesname": species, "bufferleadmonspeciesname": species,
            "bufferpartymonnick": NICK, "bufferitemname": item,
            "bufferitemnameplural": item, "buffermovename": move,
            "buffermovetolearn": move, "buffernumberstring": "9" * 7,
            "bufferboxname": "ש" * 8, "bufferdecorationname": "ש" * 12,
            "bufferstdstring": "ש" * 12}


CATEGORY = None
_SOURCES = None


def _script_bodies(script_files):
    bodies, cur = {}, None
    for path in script_files:
        for line in io.open(path, encoding="utf-8").read().split("\n"):
            m = LABEL.match(line)
            if m:
                cur = m.group(1)
                bodies[cur] = []
                continue
            if cur is not None:
                bodies[cur].append(line)
    return bodies


def _vars_of(bodies, label, depth=0, seen=None):
    if seen is None:
        seen = set()
    if label in seen or depth > 2:
        return {}
    seen.add(label)
    found = {}
    for line in bodies.get(label, []):
        b = BUFFER.match(line)
        if b:
            found.setdefault(b.group(2), b.group(1))
        c = CALLS.match(line)
        if c:
            for k, v in _vars_of(bodies, c.group(1), depth + 1, seen).items():
                found.setdefault(k, v)
    return found


def sources(audit):
    """text label -> {STR_VAR_n: buffer command that fills it}"""
    global _SOURCES, CATEGORY
    if _SOURCES is not None:
        return _SOURCES
    CATEGORY = _categories()
    bodies = _script_bodies(list(audit._script_files()))
    pattern = re.compile(r"\s*(?:%s)\s+([A-Za-z_][A-Za-z0-9_]*)"
                         % "|".join(audit.DIALOGUE_COMMANDS))
    out = {}
    for label, lines in bodies.items():
        for line in lines:
            m = pattern.match(line)
            if m:
                d = out.setdefault(m.group(1), {})
                for k, v in _vars_of(bodies, label).items():
                    d.setdefault(k, v)
    _SOURCES = out
    return out


def fill(segment, label, audit):
    """segment with placeholders replaced by the widest thing that can appear.

    Returns (filled, unresolved) -- unresolved names the vars whose source could
    not be traced, which fall back to the widest substitution of all.
    """
    src = sources(audit).get(label, {})
    over = OVERRIDE.get(label, {})
    out = re.sub(r"\{(PLAYER|RIVAL)\}", PLAYER, segment)
    unresolved = []
    for var in ("STR_VAR_1", "STR_VAR_2", "STR_VAR_3"):
        token = "{%s}" % var
        if token not in out:
            continue
        if var in over:
            out = out.replace(token, over[var])
            continue
        cat = src.get(var)
        if cat in CATEGORY:
            out = out.replace(token, CATEGORY[cat])
        else:
            out = out.replace(token, CATEGORY["bufferitemname"])
            unresolved.append(var)
    return out, unresolved
