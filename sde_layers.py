"""
SDE Capital Works layer matcher (READ-ONLY).

Fetches the feature-class names in the Capital Works group and fuzzy-matches a
Content Manager record TITLE to the best layer, e.g.

    "2026-27 Footpath Renewal Program"  ->  Footpath_Renewal_2026_27

Matching logic:
  * normalise both strings (lowercase, split on non-alphanumerics)
  * pull out a financial-year token if present (2026-27 / 2026_27 -> 2026_27)
  * score = keyword token overlap (Jaccard); if both have a year they must agree
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sde_connection as sde

CAPITAL_GROUP = "GSCC_Capital_Works"

# Words that add no matching value
STOP = {"program", "programme", "renewal", "renewals", "the", "of", "and",
        "to", "for", "10", "year", "years", "works", "work", "capital",
        "new", "construction", "construct", "design", "upgrade", "v2", "v1",
        "old", "test", "dbtest"}

_YEAR_RE = re.compile(r"(?<!\d)(20\d{2})[\-_/](\d{2})(?!\d)")


def short_name(full):
    """SDE.SDEADMIN.Footpath_Renewal_2026_27 -> Footpath_Renewal_2026_27"""
    return full.split(".")[-1]


def _year(text):
    m = _YEAR_RE.search(text)
    return f"{m.group(1)}_{m.group(2)}" if m else None


def tokens(text):
    parts = re.split(r"[^a-z0-9]+", text.lower())
    return {p for p in parts if p and p not in STOP and not p.isdigit()}


def get_capital_layers(conn=None):
    """Return list of short layer names in the Capital Works group."""
    own = conn is None
    if own:
        conn = sde.get_connection()
    cols, rows = sde.execute_query(conn, """
        SELECT child.name FROM sde.GDB_ITEMRELATIONSHIPS rel
        JOIN sde.GDB_ITEMS parent ON rel.originID=parent.uuid
        JOIN sde.GDB_ITEMS child  ON rel.destID=child.uuid
        WHERE parent.name LIKE ? ORDER BY child.name""", (f"%{CAPITAL_GROUP}%",))
    if own:
        conn.close()
    return [short_name(r[0]) for r in rows]


def best_match(title, layers):
    """Return (layer, score) best matching the title, or (None, 0)."""
    t_tokens = tokens(title)
    t_year = _year(title)
    best, best_score = None, 0.0
    for layer in layers:
        l_tokens = tokens(layer)
        l_year = _year(layer)
        if not t_tokens or not l_tokens:
            continue
        overlap = len(t_tokens & l_tokens)
        if overlap == 0:
            continue
        score = overlap / len(t_tokens | l_tokens)   # Jaccard
        if t_year and l_year:
            if t_year == l_year:
                score += 0.5
            else:
                score -= 0.3
        if score > best_score:
            best, best_score = layer, score
    return best, round(best_score, 3)


if __name__ == "__main__":
    layers = get_capital_layers()
    print(f"Capital Works layers: {len(layers)}")
    samples = [
        "2026-27 Footpath Renewal Program",
        "2026-27 Guard Railing on Road Bridges",
        "Gravel Road Re-Sheeting Renewal Program - 10 years - 2026-27 to 2035-36",
        "Sealed Road Renewal Program - 10 Years",
        "2027-28 Kerb Renewal",
        "Shared Path 2026-27",
    ]
    for t in samples:
        layer, score = best_match(t, layers)
        print(f"  {t!r:70} -> {layer}  ({score})")
