#!/usr/bin/env python3
"""Print one immutable-scoring row for each saved live run."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def view(report: str) -> str:
    match = re.search(r"^view:\s*(.+)$", report, re.M | re.I)
    return match.group(1).strip() if match else "not computed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path, help="Folder that contains saved live runs")
    args = parser.parse_args()
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
        rows.append((evidence.get("ticker", run.name.split("-")[0]).upper(), filing_time, "not recorded", direction, "not available", "not scored", "after"))
    print("| ticker | filing time | view time | direction | reaction | agree | timing |")
    print("|---|---|---|---|---|---|---|")
    for row in rows: print("| " + " | ".join(row) + " |")
    print(f"\nAgreements: 0 / 0 scored runs. Rows marked `after`, views `not computed`, and unavailable reactions are excluded.")


if __name__ == "__main__":
    main()
