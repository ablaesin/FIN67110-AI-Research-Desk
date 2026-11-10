#!/usr/bin/env python3
"""Read official daily closes from an LSEG or WRDS export kept outside this repository.

The export must have `ticker`, `date`, and `close` columns. The code sends only the
single selected close onward; it never copies the raw vendor export into the repository.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


def normal_row(row: dict[str, str]) -> tuple[str, date, float] | None:
    """Accept lower- or upper-case vendor export headings, but no adjusted-close field."""
    fields = {key.strip().lower(): (value or "").strip() for key, value in row.items() if key}
    try:
        return fields["ticker"].upper(), date.fromisoformat(fields["date"]), float(fields["close"])
    except (KeyError, ValueError):
        return None


def closes_between(csv_path: Path, ticker: str, start: date, end: date) -> list[tuple[date, float]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = [normal_row(row) for row in csv.DictReader(handle)]
    usable = [row for row in rows if row and row[0] == ticker.upper() and start <= row[1] <= end]
    return [(row[1], row[2]) for row in sorted(usable, key=lambda item: item[1])]


def close_cutoff_date(before: date | datetime) -> date:
    """A daily close exists at 4:00 PM Eastern; a pre-close filing uses the prior close."""
    if isinstance(before, datetime):
        eastern = before.astimezone(ZoneInfo("America/New_York")) if before.tzinfo else before.replace(tzinfo=ZoneInfo("America/New_York"))
        return eastern.date() if eastern.time() >= time(16, 0) else eastern.date() - timedelta(days=1)
    return before


def last_close(csv_path: Path, ticker: str, before: date | datetime) -> tuple[date, float] | None:
    usable = closes_between(csv_path, ticker, date(1900, 1, 1), close_cutoff_date(before))
    if not usable:
        return None
    return usable[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the last official close on or before a date.")
    parser.add_argument("ticker")
    parser.add_argument("before", help="YYYY-MM-DD, or an ISO filing time such as 2026-11-10T11:32:12Z")
    parser.add_argument("--csv", required=True, type=Path, help="Path to an LSEG or WRDS export outside this repository")
    args = parser.parse_args()
    before = datetime.fromisoformat(args.before.replace("Z", "+00:00")) if "T" in args.before else date.fromisoformat(args.before)
    result = last_close(args.csv, args.ticker, before)
    if not result:
        raise SystemExit("No close was returned. Do not substitute a price.")
    price_date, close = result
    print(f"{args.ticker.upper()} | {close:.2f} | {price_date.isoformat()} | source: {args.csv}")


if __name__ == "__main__":
    main()
