#!/usr/bin/env python3
"""Lab 08: fixed-order desk join. Models do not select parts or their order."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
RUNS = ROOT / "runs"
WORKSHEET = ROOT / "skills" / "spinoff-worksheet" / "worksheet.py"
HOOK = ROOT / "skills" / "spinoff-worksheet" / "worksheet_hook.py"
REPORT_HOOK = ROOT / "skills" / "spinoff-worksheet" / "report_hook.py"


def elapsed(name: str, start: float) -> None:
    print(f"{name}: {time.monotonic() - start:.2f} seconds")


def latest_saved(ticker: str) -> Path | None:
    choices = [path for path in RUNS.glob(f"{ticker.lower()}-*") if (path / "evidence.json").exists()]
    return max(choices, default=None, key=lambda path: path.stat().st_mtime)


def screen_ticker() -> str:
    files = sorted((ROOT / "skills" / "spinoff-seeker" / "output").glob("screen-*.md"), reverse=True)
    if not files: raise RuntimeError("screen failed: no seeker screen exists")
    body = files[0].read_text(encoding="utf-8")
    watch = re.search(r"# Watch list\n(.+?)(?:\n#|\Z)", body, re.S)
    if not watch or "None" in watch.group(1):
        raise RuntimeError("screen failed: the latest seeker screen has no ranked ticker; spinoff parts are not applicable")
    match = re.search(r"\(([A-Z]{1,6})\)|\|\s*([A-Z]{1,6})\s*\|", watch.group(1))
    if not match: raise RuntimeError("screen failed: the top screen name has no ticker")
    return next(value for value in match.groups() if value)


def final_report(run: Path) -> Path:
    evidence = json.loads((run / "evidence.json").read_text(encoding="utf-8"))
    names = []
    for key, source in evidence.get("sources", {}).items():
        if isinstance(source, dict) and source.get("accession"):
            names.append(f"{key} {source['accession']}")
    if (run / "filings" / "form10_information_statement.txt").exists(): names.append("Form 10 information statement saved with run")
    verified = (run / "verified_report.md").read_text(encoding="utf-8")
    worksheet = (run / "worksheet.md").read_text(encoding="utf-8")
    out = run / "final_report.md"
    out.write_text("Filings read: " + "; ".join(names) + "\n\n" + verified + "\n\n## Worksheet view\n" + worksheet, encoding="utf-8")
    return out


def replay(source: Path) -> Path:
    target = RUNS / f"{source.name}-replay-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    shutil.copytree(source, target)
    if not (target / "worksheet.md").exists():
        subprocess.run([sys.executable, str(WORKSHEET), str(target), "--no-model"], check=True)
    if not (target / "final_report.md").exists(): final_report(target)
    subprocess.run([sys.executable, str(HOOK), str(target / "worksheet.md")], check=True)
    subprocess.run([sys.executable, str(REPORT_HOOK), str(target / "final_report.md")], check=True)
    return target / "final_report.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?", help="Ticker, or screen for the top ranked seeker name")
    parser.add_argument("--peers")
    parser.add_argument("--price", type=float)
    parser.add_argument("--price-date")
    parser.add_argument("--price-source")
    parser.add_argument("--replay", type=Path, metavar="RUN", help="Rebuild saved output without network access.")
    parser.add_argument("--offline-worksheet", action="store_true", help="Test-only: do not call the worksheet model.")
    args = parser.parse_args()
    if args.replay:
        start = time.monotonic(); print("order: replay → worksheet hook → final-report hook")
        print(replay(args.replay.resolve())); elapsed("replay", start); return
    if not args.ticker: raise SystemExit("Provide TICKER or screen.")
    ticker = screen_ticker() if args.ticker.lower() == "screen" else args.ticker.upper()
    saved = latest_saved(ticker)
    if saved and not all((args.peers, args.price is not None, args.price_date, args.price_source)):
        evidence = json.loads((saved / "evidence.json").read_text(encoding="utf-8"))
        args.peers = args.peers or ",".join(evidence.get("peers", {}).keys())
        args.price = args.price if args.price is not None else evidence["price"]["value"]
        args.price_date = args.price_date or evidence["price"]["date"]
        args.price_source = args.price_source or evidence["price"]["source"]
    if not all((args.peers, args.price is not None, args.price_date, args.price_source)):
        raise SystemExit("A new ticker needs --peers, --price, --price-date, and --price-source. A saved run supplies these inputs automatically.")
    print("order: pick → agent team → worksheet → worksheet hook → final-report hook")
    before = set(RUNS.glob(f"{ticker.lower()}-*")); start = time.monotonic()
    command = [sys.executable, str(ROOT / "agent_team.py"), ticker, "--peers", args.peers, "--price", str(args.price), "--price-date", args.price_date, "--price-source", args.price_source]
    try:
        subprocess.run(command, check=True, cwd=ROOT)
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"agent team failed: {error}")
    created = sorted(set(RUNS.glob(f"{ticker.lower()}-*")) - before)
    if len(created) != 1: raise RuntimeError("agent team failed: it did not create exactly one run folder")
    run = created[0]; elapsed("agent team", start)
    start = time.monotonic()
    command = [sys.executable, str(WORKSHEET), str(run)] + (["--no-model"] if args.offline_worksheet else [])
    subprocess.run(command, check=True); elapsed("worksheet", start)
    start = time.monotonic(); subprocess.run([sys.executable, str(HOOK), str(run / "worksheet.md")], check=True); elapsed("worksheet hook", start)
    report = final_report(run)
    start = time.monotonic(); subprocess.run([sys.executable, str(REPORT_HOOK), str(report)], check=True); elapsed("final-report hook", start)
    print(report)


if __name__ == "__main__":
    main()
