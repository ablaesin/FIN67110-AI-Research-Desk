#!/usr/bin/env python3
"""Print one immutable-scoring row for each saved live run."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def view(report: str) -> str:
    match = re.search(r"^view:\s*(.+)$", report, re.M | re.I)
    return match.group(1).strip() if match else "not computed"


def closes(path: Path | None) -> dict[str, list[tuple[str, float]]]:
    result: dict[str, list[tuple[str, float]]] = {}
    if not path: return result
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            fields = {str(key).strip().lower(): str(value or "").strip() for key, value in row.items() if key}
            try: result.setdefault(fields["ticker"].upper(), []).append((fields["date"], float(fields["close"])))
            except (KeyError, ValueError): continue
    return {ticker: sorted(rows) for ticker, rows in result.items()}


def reaction(evidence: dict, ticker: str, prices: dict[str, list[tuple[str, float]]]) -> str:
    before = evidence.get("price", {}).get("value"); date = evidence.get("price", {}).get("date")
    if before is None or not date: return "not available"
    after = next((close for close_date, close in prices.get(ticker, []) if close_date > date), None)
    return f"{(after / float(before) - 1) * 100:.2f}%" if after is not None else "not available"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path, help="Folder that contains saved live runs")
    parser.add_argument("--closes-csv", type=Path, help="Official close CSV used only to fill newly available reactions.")
    args = parser.parse_args()
    prices = closes(args.closes_csv)
    rows = []
    folders = sorted(path for path in args.folder.iterdir() if path.is_dir()) if args.folder.exists() else []
    for run in folders:
        facts = run / "evidence.json"
        report = run / "final_report.md"
        if not report.exists(): report = run / "verified_report.md"
        if not facts.exists() or not report.exists(): continue
        evidence = json.loads(facts.read_text(encoding="utf-8"))
        direction = view(report.read_text(encoding="utf-8"))
        filing_time = evidence.get("release_time", "not recorded")
        ticker = evidence.get("ticker", run.name.split("-")[0]).upper()
        move = reaction(evidence, ticker, prices)
        direction_word = "up" if move != "not available" and float(move.rstrip("%")) > 0 else "down" if move != "not available" else "not computed"
        expected = "up" if "more than price" in direction.lower() else "down" if "less than price" in direction.lower() else "not computed"
        agree = "agree" if expected == direction_word and expected != "not computed" else "disagree" if expected != "not computed" and move != "not available" else "not scored"
        rows.append((ticker, filing_time, "not recorded", direction, move, agree, "after"))
    print("| ticker | filing time | view time | direction | reaction | agree | timing |")
    print("|---|---|---|---|---|---|---|")
    for row in rows: print("| " + " | ".join(row) + " |")
    scored = [row for row in rows if row[5] in {"agree", "disagree"} and row[6] != "after"]
    print(f"\nAgreements: {sum(row[5] == 'agree' for row in scored)} / {len(scored)} scored runs. Rows marked `after`, views `not computed`, and unavailable reactions are excluded.")


if __name__ == "__main__":
    main()
