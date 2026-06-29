"""
SDE layer match - CLI used by FME PythonCaller #4.

Reads a CSV of titles, fetches Capital Works layers from SDE (read-only),
and writes a CSV mapping each unique title to its best-match layer + score.

Usage:
    python sde_layer_match.py <titles.csv> <out.csv> [title_column]

titles.csv must have a column with the record title (default column: "title").
out.csv columns: title, sde_layer, match_score
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sde_layers import get_capital_layers, best_match


def main():
    if len(sys.argv) < 3:
        print("Usage: sde_layer_match.py <titles.csv> <out.csv> [title_column]")
        return 2
    in_csv, out_csv = sys.argv[1], sys.argv[2]
    title_col = sys.argv[3] if len(sys.argv) > 3 else "title"

    titles = []
    seen = set()
    with open(in_csv, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            t = (row.get(title_col) or "").strip()
            if t and t not in seen:
                seen.add(t)
                titles.append(t)

    layers = get_capital_layers()
    print(f"Capital Works layers: {len(layers)}  Unique titles: {len(titles)}")

    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["title", "sde_layer", "match_score"])
        for t in titles:
            layer, score = best_match(t, layers)
            w.writerow([t, layer or "", score])
    print(f"Wrote {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
