#!/usr/bin/env python3
"""Lab 07 output hook. It reads worksheet text, not a sidecar facts file."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def number(text: str) -> float:
    return float(text.replace("$", "").replace(",", ""))


def fail(line_no: int, message: str) -> None:
    print(f"refused: line {line_no}, {message}")
    raise SystemExit(1)


def verify(path: Path) -> None:
    facts_path = path.parent / "evidence.json"
    if not facts_path.exists():
        raise SystemExit(f"refused: evidence.json is missing beside {path}")
    evidence = json.loads(facts_path.read_text(encoding="utf-8"))
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        marker = re.search(r"\[claim: annual_numbers\.([a-z_]+)\]", line)
        if marker:
            key = marker.group(1)
            expected = evidence.get("annual_numbers", {}).get(key, {}).get("value")
            stated = re.search(r":\s*((?:-?\$|\$-?)[\d,]+(?:\.\d+)?)", line)
            if expected is None or not stated or abs(number(stated.group(1)) - float(expected)) > 0.005:
                fail(line_no, f"{stated.group(1) if stated else 'amount'} is not {key} in evidence.json")
        if "[price]" in line:
            stated = re.search(r"\$([\d,]+(?:\.\d+)?)", line)
            expected = evidence.get("price", {}).get("value")
            if expected is None or not stated or abs(float(stated.group(1)) - float(expected)) > 0.005:
                fail(line_no, f"{stated.group(0) if stated else 'price'} is not the saved reader price")
        if "[liquidity: median(daily value traded)]" in line:
            stated = re.search(r"\$([\d,]+(?:\.\d+)?)", line)
            expected = evidence.get("market_data", {}).get("median_daily_dollar_volume")
            if expected is None or not stated or abs(float(stated.group(1).replace(",", "")) - float(expected)) > 0.005:
                fail(line_no, f"{stated.group(0) if stated else 'liquidity'} is not the saved market-data median")
        if "[computed: annual_numbers.net_income + depreciation - annual_numbers.capital_expenditures]" in line:
            amounts = [number(value) for value in re.findall(r"-?\$[\d,]+(?:\.\d+)?", line)]
            net = float(evidence.get("annual_numbers", {}).get("net_income", {}).get("value", 0))
            depreciation = float(evidence.get("annual_numbers", {}).get("depreciation_and_amortization", {}).get("value", 0))
            capex = float(evidence.get("annual_numbers", {}).get("capital_expenditures", {}).get("value", 0))
            if len(amounts) != 4 or abs(amounts[0] - (net + depreciation - capex)) > 0.005:
                fail(line_no, "owner cash flow does not equal its printed filing inputs")
        if "[method: low_return=10%]" in line and "10%" not in line:
            fail(line_no, "the low-case rate does not match worksheet-method.md")
        if "[method: middle_return=9%]" in line and "9%" not in line:
            fail(line_no, "the middle-case rate does not match worksheet-method.md")
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("worksheet", type=Path)
    args = parser.parse_args()
    verify(args.worksheet.resolve())


if __name__ == "__main__":
    main()
