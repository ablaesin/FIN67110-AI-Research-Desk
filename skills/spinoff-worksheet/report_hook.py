#!/usr/bin/env python3
"""Check the worksheet portion of a joined final report from the report text itself."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import worksheet_hook  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = args.report.resolve()
    text = report.read_text(encoding="utf-8")
    marker = "## Worksheet view\n"
    if marker not in text:
        raise SystemExit("refused: final report has no worksheet view")
    temporary = report.parent / ".hook-worksheet.md"
    temporary.write_text(text.split(marker, 1)[1], encoding="utf-8")
    try:
        worksheet_hook.verify(temporary)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
