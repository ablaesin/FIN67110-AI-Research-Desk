#!/usr/bin/env python3
"""Create the Lab 07 worksheet. Calculations are code only; one model call writes judgment."""
from __future__ import annotations

import argparse
import csv
import statistics
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import desk  # noqa: E402
from google import genai  # noqa: E402

METHOD = ROOT / "lab06" / "worksheet-method.md"
REGISTRY = ROOT / "skills" / "spinoff-seeker" / "output"
PERSONA = ROOT / "roles" / "worksheet_investor.md"


def money(value: float) -> str:
    return f"-${abs(value):,.0f}" if value < 0 else f"${value:,.0f}"


def registry_item(ticker: str) -> dict | None:
    for path in sorted(REGISTRY.glob("registry-*.json"), reverse=True):
        for item in json.loads(path.read_text(encoding="utf-8")):
            if item.get("ticker", "").upper() == ticker.upper() and not item.get("dropped"):
                return item
    return None


def valuation(owner_cash_flow: float | None, shares: float | None) -> dict[str, float] | None:
    if owner_cash_flow is None or owner_cash_flow <= 0 or not shares:
        return None
    low = owner_cash_flow / 0.10 / shares
    # Five years at 3%, then 2% perpetuity, discounted at 9%.
    present = sum(owner_cash_flow * 1.03**year / 1.09**year for year in range(1, 6))
    terminal = owner_cash_flow * 1.03**5 * 1.02 / (0.09 - 0.02)
    mid = (present + terminal / 1.09**5) / shares
    return {"low": low, "middle": mid}


def source_line(item: dict) -> str:
    return f"10-K {item['accession']}; XBRL {item['tag']}, period {item['period_end']}"


def median_dollar_volume(csv_path: Path | None, ticker: str) -> tuple[float, str] | None:
    """Read vendor close and volume columns without saving the vendor file in the repository."""
    if not csv_path:
        return None
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = csv.DictReader(handle)
        values = []
        for row in rows:
            fields = {str(key).strip().lower(): str(value or "").strip() for key, value in row.items() if key}
            try:
                if fields["ticker"].upper() == ticker.upper():
                    values.append(float(fields["close"]) * float(fields["volume"]))
            except (KeyError, ValueError):
                continue
    return (statistics.median(values), str(csv_path)) if values else None


def build(run_dir: Path, no_model: bool, closes_csv: Path | None = None) -> Path:
    evidence = json.loads((run_dir / "evidence.json").read_text(encoding="utf-8"))
    ticker = evidence["ticker"].upper()
    numbers = evidence.get("annual_numbers", {})
    price = evidence.get("price", {})
    reg = registry_item(ticker)
    spinoff = "not applicable" if not reg else "reported"
    run_filings = run_dir / "filings"
    run_filings.mkdir(exist_ok=True)
    if reg and reg.get("filing_url"):
        desk.load_env()
        target = run_filings / "form10_information_statement.txt"
        if not target.exists():
            target.write_text(desk.plain_text(desk.get_text(desk.sec_session(), reg["filing_url"])), encoding="utf-8")

    def claim(key: str, label: str) -> str:
        item = numbers.get(key)
        if not item:
            return f"{label}: not known"
        return f"{label}: {money(float(item['value']))}; historic; {source_line(item)} [claim: annual_numbers.{key}]"

    net = numbers.get("net_income")
    capex = numbers.get("capital_expenditures")
    depreciation_item = numbers.get("depreciation_and_amortization")
    depreciation = float(depreciation_item["value"]) if depreciation_item else None
    owner_cash_flow = None
    if net and capex and depreciation is not None:
        owner_cash_flow = float(net["value"]) + depreciation - float(capex["value"])
    shares_item = numbers.get("diluted_weighted_average_shares")
    shares = float(shares_item["value"]) if shares_item and float(shares_item["value"]) > 0 else None
    values = valuation(owner_cash_flow, shares)
    price_line = "price: not computed" if not price else (
        f"price: ${float(price['value']):.2f} on {price['date']}; {price['source']} [price]"
    )
    if owner_cash_flow is None:
        ocf_line = "owner cash flow: not computed; after-tax earnings + depreciation and amortization - capital expenditures; depreciation and amortization not known"
    else:
        ocf_line = (f"owner cash flow: {money(owner_cash_flow)} = {money(float(net['value']))} + {money(depreciation)} - {money(float(capex['value']))} "
                    "[computed: annual_numbers.net_income + depreciation - annual_numbers.capital_expenditures]")
    if values is None:
        value_lines = ["low case: not computed", "middle case: not computed", "price against low case: not computed"]
    else:
        value_lines = [
            f"low case: ${values['low']:.2f} per share; 0% growth; 10% required return; 0% terminal growth [method: low_return=10%]",
            f"middle case: ${values['middle']:.2f} per share; 3% growth for five years; 9% required return; 2% terminal growth [method: middle_return=9%]",
            f"price against low case: {(float(price['value']) / values['low'] - 1) * 100:.2f}%" if price else "price against low case: not computed",
        ]
    liquidity = median_dollar_volume(closes_csv, ticker)
    facts = {
        "ticker": ticker, "spinoff": spinoff, "parent": reg.get("parent") if reg else "not applicable",
        "ratio": reg.get("distribution_ratio") if reg else "not applicable", "price": price,
        "owner_cash_flow": owner_cash_flow, "values": values, "liquidity": liquidity[0] if liquidity else None,
    }
    if no_model:
        judgment = "Offline test: no model call. Filing facts do not support a judgment."
    else:
        desk.load_env()
        judgment = desk.model_call(
            genai.Client(api_key=__import__("os").environ["API_KEY"]),
            "Worksheet Investor", "Write the worksheet judgment from these facts only.", facts,
            "A short judgment that ends with what in the next filing would change the view.",
            PERSONA.read_text(encoding="utf-8"),
        )
    conviction = "Low / no action" if not values or not price else "Medium"
    lines = [
        f"# {ticker} worksheet", "", f"Run: {run_dir.name}", f"Method: {METHOD.relative_to(ROOT)}", "",
        "## Spinoff facts", f"parent: {facts['parent']}; {spinoff}", f"distribution ratio: {facts['ratio']}; {spinoff}",
        "distribution dates: not applicable" if not reg else f"distribution dates: {reg.get('record_date', 'not known')}; {reg.get('distribution_date', 'not known')}",
        "debt raised and cash to parent: not applicable" if not reg else "debt raised and cash to parent: not known",
        "parent liabilities and restrictions: not applicable" if not reg else "parent liabilities and restrictions: not known",
        "Form 4 purchases, code P only: not applicable" if not reg else "Form 4 purchases, code P only: not known", "",
        "## Filing facts", claim("net_income", "after-tax earnings"), claim("capital_expenditures", "capital expenditures"),
        claim("liabilities", "liabilities"), claim("cash_from_operations", "cash from operations"),
        claim("depreciation_and_amortization", "depreciation and amortization"), claim("diluted_weighted_average_shares", "diluted weighted-average shares"), "",
        "## Owner cash flow and value", ocf_line, *value_lines, price_line, "",
        "## Liquidity",
        (f"median daily dollar volume: {money(liquidity[0])}; source: {liquidity[1]} [liquidity: median(close * volume)]\n"
         f"purchase size: {'allowed' if 10000 <= liquidity[0] * 0.10 else 'not determined'}; $10,000 project limit against 10% of median daily dollar volume"
         if liquidity else "median daily dollar volume: not known; purchase size: not determined; supply an official close-and-volume CSV with --closes-csv."), "",
        "## Judgment", judgment, "", "## Release view", "view: not computed; the owner-cash-flow value is not computed.",
        f"conviction: {conviction}; worksheet-method conviction rule.", "", "## Not known",
        "- depreciation and amortization", "- reliable share count for valuation", "- median daily dollar volume", "- Form 4 open-market purchases", "",
    ]
    output = run_dir / "worksheet.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    dated = run_dir / "worksheets"
    dated.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shutil.copy2(output, dated / f"worksheet-{stamp}.md")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--closes-csv", type=Path, help="Official vendor CSV with ticker,date,close,volume; kept outside the repository.")
    args = parser.parse_args()
    print(build(args.run.resolve(), args.no_model, args.closes_csv))


if __name__ == "__main__":
    main()
