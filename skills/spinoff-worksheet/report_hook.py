#!/usr/bin/env python3
"""Refuse a final report when a numeric claim is absent from saved evidence or filings."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import worksheet_hook  # noqa: E402


NUMBER = re.compile(r"(?<![A-Za-z0-9])(?:\d+(?:\.\d+)?%|(?:-?\$|\$-?)?\d[\d,]*(?:\.\d+)?)(?![A-Za-z0-9])")


def numeric_forms(value: object) -> set[float]:
    try:
        raw = float(value)
    except (TypeError, ValueError):
        return set()
    return {raw, raw / 1_000, raw / 1_000_000, raw / 1_000_000_000, raw * 100,
            raw * 1_000, raw * 1_000_000, raw * 1_000_000_000}


def parsed(token: str) -> float:
    percent = token.endswith("%")
    value = float(token.rstrip("%").replace("$", "").replace(",", ""))
    return value / 100 if percent else value


def support_values(run: Path) -> set[float]:
    evidence = json.loads((run / "evidence.json").read_text(encoding="utf-8"))
    supported: set[float] = set()

    def collect(value: object) -> None:
        if isinstance(value, dict):
            for child in value.values(): collect(child)
        elif isinstance(value, list):
            for child in value: collect(child)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            supported.update(numeric_forms(value))

    # This includes the subject's figures, code-calculated ratios, and peer figures.
    # All three are saved in evidence.json before any report is generated.
    collect(evidence)
    annual = evidence.get("annual_numbers", {})
    owner_cash_flow_inputs = (
        annual.get("net_income", {}).get("value"),
        annual.get("depreciation_and_amortization", {}).get("value"),
        annual.get("capital_expenditures", {}).get("value"),
    )
    if all(isinstance(value, (int, float)) for value in owner_cash_flow_inputs):
        net_income, depreciation, capex = owner_cash_flow_inputs
        supported.update(numeric_forms(net_income + depreciation - capex))
    if evidence.get("price", {}).get("value") is not None: supported.update(numeric_forms(evidence["price"]["value"]))
    for filing in (run / "filings").glob("*.txt"):
        for token in NUMBER.findall(filing.read_text(encoding="utf-8")):
            supported.update(numeric_forms(parsed(token)))
    return supported


def identifier(line: str, token: str) -> bool:
    start = line.find(token); before = line[max(0, start - 24):start].lower()
    return bool(re.fullmatch(r"20\d{2}", token) or re.fullmatch(r"\d{10}-\d{2}-\d{6}", token)
                or any(word in before for word in ("accession", "form ", "item ", "q3", "fy", "line ", "run:")))


def close_enough(value: float, candidates: set[float]) -> bool:
    return any(abs(value - candidate) <= max(0.005, abs(candidate) * 0.0005) for candidate in candidates)


def verify(report: Path) -> None:
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
    supported = support_values(report.parent)
    for line_no, line in enumerate(text.splitlines(), 1):
        for token in NUMBER.findall(line):
            if not identifier(line, token) and not close_enough(parsed(token), supported):
                raise SystemExit(f"refused: line {line_no}, {token} is not in saved evidence, a saved filing, or a printed calculation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    verify(args.report.resolve())


if __name__ == "__main__":
    main()
