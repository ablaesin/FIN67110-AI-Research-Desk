#!/usr/bin/env python3
"""EDGAR-first spinoff seeker for FIN 67110 Lab 06.

The program discovers Form 10 and Form 10-12B registrants in SEC full indexes,
records only facts it finds in a filing, and reports unknown facts as blank.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
OUTPUT = HERE / "output"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        raise SystemExit("Missing .env. Add SEC_USER_AGENT before making EDGAR requests.")
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def session() -> requests.Session:
    agent = os.environ.get("SEC_USER_AGENT", "")
    if not agent:
        raise SystemExit("SEC_USER_AGENT is required. The seeker will not make an anonymous EDGAR request.")
    client = requests.Session()
    client.headers.update({"User-Agent": agent, "Accept-Encoding": "gzip, deflate"})
    return client


def get(client: requests.Session, url: str) -> str:
    response = client.get(url, timeout=45)
    response.raise_for_status()
    time.sleep(0.12)  # below EDGAR's 10 requests/second limit
    return response.text


def text(markup: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", markup)).strip()


def quarters(start: date, end: date) -> list[tuple[int, int]]:
    answer: list[tuple[int, int]] = []
    cursor = date(start.year, ((start.month - 1) // 3) * 3 + 1, 1)
    while cursor <= end:
        item = (cursor.year, (cursor.month - 1) // 3 + 1)
        if item not in answer:
            answer.append(item)
        cursor = date(cursor.year + (cursor.month == 10), 1 if cursor.month == 10 else cursor.month + 3, 1)
    return answer


def index_candidates(index: str, start: date) -> list[dict[str, str]]:
    candidates = []
    for row in index.splitlines():
        bits = row.split("|")
        if len(bits) != 5 or bits[2] not in {"10-12B", "10-12B/A", "10"}:
            continue
        filing_date = date.fromisoformat(bits[3])
        if filing_date >= start:
            candidates.append({"cik": bits[0].zfill(10), "name": bits[1], "form": bits[2], "filed": bits[3], "path": bits[4]})
    return candidates


def filing_url(candidate: dict[str, str]) -> str:
    return "https://www.sec.gov/Archives/" + candidate["path"]


def source(url: str, section: str) -> dict[str, str]:
    return {"filing": url, "section": section}


def first_match(patterns: list[str], body: str) -> str:
    for pattern in patterns:
        found = re.search(pattern, body, re.I)
        if found:
            return re.sub(r"\s+", " ", found.group(1)).strip(" .;:")
    return ""


def find_facts(body: str, url: str) -> dict[str, Any]:
    parent = first_match([
        r"(?:our|the) parent company,?\s+([^,.]{2,100})[,.;]",
        r"distribution by\s+([^,.]{2,100})[,.;]",
        r"([^,.]{2,100})\s+will distribute all of the shares",
    ], body)
    ratio = first_match([r"(?:distribution|distributed)\s+(?:ratio|of)\s+([^.;]{3,80}(?:share|shares)[^.;]{0,80})"], body)
    record_date = first_match([r"record date (?:will be|is|of)?\s*(.{0,80}?)(?:[.;]|\s+and\s+the distribution)"], body)
    distribution_date = first_match([r"distribution date (?:will be|is|of)?\s*(.{0,80}?)(?:[.;]|\s+we expect)"], body)
    # Dates without a clear label stay blank; the report must not infer them.
    result: dict[str, Any] = {"parent": parent, "distribution_ratio": ratio,
                              "record_date": record_date, "distribution_date": distribution_date,
                              "ticker": "", "sources": {}}
    for field, value in list(result.items()):
        if field not in {"sources", "ticker"} and value:
            result["sources"][field] = source(url, "Information Statement")
    return result


def exclusion_reason(body: str) -> str:
    low = body.lower()
    def stated_as(term: str) -> bool:
        """Return true only for an affirmative description, not 'not an investment company'."""
        for match in re.finditer(re.escape(term), low):
            before = low[max(0, match.start() - 90):match.start()]
            if re.search(r"\b(?:not|no)\s+(?:an?\s+)?$", before):
                continue
            if re.search(r"\b(?:is|are|was|were|as|a|an|the)\s+(?:registered\s+)?$", before):
                return True
        return False
    if any(stated_as(term) for term in ("investment company", "closed-end fund", "mutual fund")):
        return "fund registrant"
    if any(stated_as(term) for term in ("shell company", "blank check company")):
        return "shell company"
    if "information statement" not in low:
        return "Form 10 has no information statement"
    return ""


def date_from_fact(value: str) -> date | None:
    patterns = [r"\b(20\d{2}-\d{2}-\d{2})\b", r"\b([A-Z][a-z]+ \d{1,2}, 20\d{2})\b"]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            try:
                return date.fromisoformat(match.group(1)) if "-" in match.group(1) else datetime.strptime(match.group(1), "%B %d, %Y").date()
            except ValueError:
                pass
    return None


def score(row: dict[str, Any], factors: dict[str, Any], today: date) -> tuple[int | None, list[str], str]:
    distributed = date_from_fact(row.get("distribution_date", ""))
    if not distributed:
        return None, [], "missing distribution date"
    if today > distributed.fromordinal(distributed.toordinal() + int(factors["window_days"])):
        return None, [], "past its window"
    points, details = 0, []
    for factor in factors["factors"]:
        weight = factor.get("weight")
        field = factor.get("field")
        if not isinstance(weight, (int, float)) or not field or not row.get(field):
            return None, details, f"missing factor data: {factor.get('name', 'unnamed')}"
        if weight == 0:
            continue
        # Numeric fields can be compared. Textual factors require a user-written scorer.
        try:
            value = float(row[field])
        except (TypeError, ValueError):
            return None, details, f"factor is not numeric: {factor.get('name', 'unnamed')}"
        awarded = int(weight) if (factor.get("direction") == "higher" and value > 0) or (factor.get("direction") == "lower" and value < 0) else 0
        points += awarded
        details.append(f"{factor['name']} {awarded}")
    return points, details, ""


def render(rows: list[dict[str, Any]], run_date: date, index_date: str, factors: dict[str, Any]) -> str:
    lines = [f"Run date: {run_date} | price date: see each row | index date: {index_date}", "", "# Spinoff screen", ""]
    ranked, watch, dropped, unranked = [], [], [], []
    for row in rows:
        if row.get("dropped"):
            dropped.append(row); continue
        if not row.get("distribution_date"):
            watch.append(row); continue
        points, details, reason = score(row, factors, run_date)
        row["points"], row["factor_points"], row["unranked_reason"] = points, details, reason
        (ranked if points is not None else unranked).append(row)
    for row in sorted(ranked, key=lambda item: item["points"], reverse=True):
        lines.append(f"{row['name']} | {row.get('parent') or 'blank'} | distributed {row['distribution_date']} | points {row['points']}: {', '.join(row['factor_points'])}")
    if not ranked: lines.append("No ranked names. Complete the hand-written factors file or preserve missing facts as unranked.")
    lines += ["", "# Watch list"]
    lines += [f"{row['name']} | registered | {row['filing_url']}" for row in watch] or ["None"]
    lines += ["", "# Unranked"]
    lines += [f"{row['name']} | {row['unranked_reason']}" for row in unranked] or ["None"]
    lines += ["", "# Dropped"]
    lines += [f"{row['name']} | {row['dropped']} | {row['filing_url']}" for row in dropped] or ["None"]
    lines += ["", "# Limits", "Facts that EDGAR filings did not show remain blank. The seeker does not estimate them.", "", "screens, not recommendations"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Find U.S. spinoffs from EDGAR Form 10 filings.")
    parser.add_argument("start_date", type=date.fromisoformat, help="YYYY-MM-DD")
    parser.add_argument("--end-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--factors", type=Path, default=HERE / "factors.json")
    args = parser.parse_args()
    if not args.factors.exists():
        raise SystemExit(f"Missing {args.factors}. Copy factors.template.json and write it by hand before running.")
    factors = json.loads(args.factors.read_text(encoding="utf-8"))
    load_env(); client = session(); rows: list[dict[str, Any]] = []
    for year, quarter in quarters(args.start_date, args.end_date):
        url = f"https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{quarter}/master.idx"
        try:
            candidates = index_candidates(get(client, url), args.start_date)
        except requests.HTTPError as error:
            print(f"Index unavailable: {url}: {error}", file=sys.stderr); continue
        for candidate in candidates:
            url = filing_url(candidate)
            try:
                body = text(get(client, url))
            except requests.RequestException as error:
                rows.append({**candidate, "filing_url": url, "dropped": f"filing unreadable: {error}"}); continue
            facts = find_facts(body, url)
            reason = exclusion_reason(body)
            # A registrant with no distribution evidence is not called a spinoff.
            if not reason and not (facts["parent"] or facts["distribution_date"] or facts["distribution_ratio"]):
                reason = "no parent distribution found in this filing"
            rows.append({**candidate, **facts, "filing_url": url, "dropped": reason})
    OUTPUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUTPUT / f"registry-{stamp}.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    report = render(rows, args.end_date, args.end_date.isoformat(), factors)
    report_path = OUTPUT / f"screen-{stamp}.md"; report_path.write_text(report, encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
