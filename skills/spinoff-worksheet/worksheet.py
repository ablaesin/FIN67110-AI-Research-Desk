#!/usr/bin/env python3
"""Create the Lab 07 worksheet. Calculations are code only; one model call writes judgment."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import desk  # noqa: E402
from google import genai  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
import market_data  # noqa: E402

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
    return f"{item.get('form', '10-K')} {item['accession']}; XBRL {item['tag']}, period {item['period_end']}"


def information_statement_facts(text: str) -> dict[str, str]:
    """Extract only explicitly stated financing facts from a saved Form 10 exhibit."""
    debt = re.search(r"aggregate principal amount of \$(\d+(?:\.\d+)?) billion", text, re.I)
    cash = re.search(r"used \$(\d+(?:\.\d+)?) billion of the net proceeds.*?cash distribution to", text, re.I | re.S)
    exchange = re.search(r"distributed \$(\d+(?:\.\d+)?) billion of Exchange Notes", text, re.I)
    cash_flow = re.search(
        r"CASH FLOWS FROM OPERATING ACTIVITIES:.*?Net income\s*\$?\s*([\d,]+).*?Depreciation\s+([\d,]+).*?Amortization\s+([\d,]+).*?Capital expenditures\s*\(?([\d,]+)\)?",
        text, re.I | re.S,
    )
    shares = re.search(r"issuance of approximately\s*([\d,]+)\s*shares", text, re.I)
    return {
        "debt": f"${debt.group(1)} billion senior unsecured notes" if debt else "not known",
        "cash_to_parent": f"${cash.group(1)} billion cash distribution to the parent" if cash else "not known",
        "exchange_notes": f"${exchange.group(1)} billion exchange notes to the parent" if exchange else "not known",
        "restriction": ("intellectual-property and trademark license agreements with the parent limit product and service development and commercialization"
                        if "Restrictions under our intellectual property license and trademark license agreements" in text else "not known"),
        "historic_net_income": float(cash_flow.group(1).replace(",", "")) * 1_000_000 if cash_flow else None,
        "historic_depreciation": float(cash_flow.group(2).replace(",", "")) * 1_000_000 if cash_flow else None,
        "historic_amortization": float(cash_flow.group(3).replace(",", "")) * 1_000_000 if cash_flow else None,
        "historic_capex": float(cash_flow.group(4).replace(",", "")) * 1_000_000 if cash_flow else None,
        "historic_shares": float(shares.group(1).replace(",", "")) if shares else None,
    }


def form4_purchases(cik: str, after: date, filings_dir: Path) -> list[str]:
    """Save and read post-distribution Form 4s; keep only open-market code P trades."""
    session = desk.sec_session()
    data = desk.get_json(session, f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")["filings"]["recent"]
    purchases = []
    for index, form in enumerate(data["form"]):
        if form != "4" or date.fromisoformat(data["filingDate"][index]) < after:
            continue
        accession = data["accessionNumber"][index]
        name = data["primaryDocument"][index].split("/")[-1]
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{name}"
        try:
            raw = desk.get_text(session, url)
            (filings_dir / f"form4-{accession}.xml").write_text(raw, encoding="utf-8")
            root = ET.fromstring(raw)
        except (OSError, ET.ParseError):
            continue
        owner = root.findtext(".//reportingOwnerId/rptOwnerName", default="unnamed owner")
        for item in root.findall(".//nonDerivativeTransaction"):
            if item.findtext(".//transactionCode") != "P":
                continue
            trade_date = item.findtext(".//transactionDate/value", default="not known")
            shares = item.findtext(".//transactionShares/value", default="not known")
            price = item.findtext(".//transactionPricePerShare/value", default="not known")
            purchases.append(f"{owner}: {shares} shares at ${price} on {trade_date}; Form 4 {accession}")
    return purchases


def build(run_dir: Path, no_model: bool, market_file: Path | None = None) -> Path:
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
    info_text = (run_filings / "form10_information_statement.txt").read_text(encoding="utf-8", errors="ignore") if (run_filings / "form10_information_statement.txt").exists() else ""
    info = information_statement_facts(info_text) if reg else {}
    purchases = []
    if reg and reg.get("cik") and reg.get("distribution_date"):
        try:
            purchases = form4_purchases(reg["cik"], datetime.strptime(reg["distribution_date"], "%B %d, %Y").date(), run_filings)
        except SystemExit:
            purchases = []

    def claim(key: str, label: str) -> str:
        item = numbers.get(key)
        if not item:
            return f"{label}: not known"
        label_type = "historic" if item.get("form") in {"10-K", "10-12B", "10-12B/A", "10"} else "reported after spin"
        return f"{label}: {money(float(item['value']))}; {label_type}; {source_line(item)} [claim: annual_numbers.{key}]"

    net = numbers.get("net_income")
    capex = numbers.get("capital_expenditures")
    depreciation_item = numbers.get("depreciation_and_amortization")
    depreciation = float(depreciation_item["value"]) if depreciation_item else None
    # The project method requires after-tax operating income.  Net income is a
    # different measure, so do not substitute it merely because it is available.
    after_tax_operating_income = None
    owner_cash_flow = None
    shares_item = numbers.get("diluted_weighted_average_shares")
    shares = float(shares_item["value"]) if shares_item and float(shares_item["value"]) > 0 else None
    historic_owner_cash_flow = None
    annual_owner_cash_flow = None
    annual_shares = shares if owner_cash_flow == annual_owner_cash_flow else info.get("historic_shares")
    values = valuation(annual_owner_cash_flow, annual_shares)
    price_line = "price: not computed" if not price else (
        f"price: ${float(price['value']):.2f} on {price['date']}; {price['source']} [price]"
    )
    ocf_line = ("owner cash flow: not computed; the method requires after-tax operating income, "
                "and net income is not substituted for that measure.")
    if values is None:
        value_lines = ["low case: not computed", "middle case: not computed", "price against low case: not computed"]
    else:
        value_lines = [
            f"low case: ${values['low']:.2f} per share; 0% growth; 10% required return; 0% terminal growth [method: low_return=10%]",
            f"middle case: ${values['middle']:.2f} per share; 3% growth for five years; 9% required return; 2% terminal growth [method: middle_return=9%]",
            f"price against low case: {(float(price['value']) / values['low'] - 1) * 100:.2f}%" if price else "price against low case: not computed",
        ]
    if info:
        evidence["information_statement"] = info
    evidence["worksheet_calculations"] = {
        "historic_owner_cash_flow": historic_owner_cash_flow,
        "low_case_per_share": values["low"] if values else None,
        "middle_case_per_share": values["middle"] if values else None,
        "price_against_low_case": (float(price["value"]) / values["low"] - 1) if values and price else None,
    }
    liquidity_value = market_data.median_dollar_volume(market_file, ticker) if market_file else None
    liquidity = (liquidity_value, str(market_file)) if liquidity_value is not None else None
    if liquidity:
        evidence["market_data"] = {
            "median_daily_dollar_volume": liquidity[0],
            "source": market_file.name,
            "method": "median(daily value traded)",
        }
    (run_dir / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
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
    release_view = "view: not computed; an annual owner-cash-flow value is not available."
    if values and price:
        direction = "more than price" if values["middle"] > float(price["value"]) else "less than price"
        release_view = (f"view: {direction}; middle case ${values['middle']:.2f} against price ${float(price['value']):.2f}; "
                        "Form 10 information statement, Combined Statements of Cash Flows")
    lines = [
        f"# {ticker} worksheet", "", f"Run: {run_dir.name}", f"Method: {METHOD.relative_to(ROOT)}", "",
        "## Spinoff facts", f"parent: {facts['parent']}; {spinoff}", f"distribution ratio: {facts['ratio']}; {spinoff}",
        "distribution dates: not applicable" if not reg else f"distribution dates: {reg.get('record_date', 'not known')}; {reg.get('distribution_date', 'not known')}",
        "debt raised and cash to parent: not applicable" if not reg else f"debt raised: {info['debt']}; cash to parent: {info['cash_to_parent']}; exchange notes: {info['exchange_notes']}; Form 10 information statement, Description of Material Indebtedness",
        "parent liabilities and restrictions: not applicable" if not reg else f"parent restrictions: {info['restriction']}; Form 10 information statement, Risk Factors",
        "Form 4 purchases, code P only: not applicable" if not reg else ("Form 4 purchases, code P only: " + "; ".join(purchases) if purchases else "Form 4 purchases, code P only: not known"), "",
        "## Filing facts", claim("net_income", "net income"), claim("capital_expenditures", "capital expenditures"),
        claim("liabilities", "liabilities"), claim("cash_from_operations", "cash from operations"),
        claim("depreciation_and_amortization", "depreciation and amortization"), claim("diluted_weighted_average_shares", "diluted weighted-average shares"), "",
        "## Owner cash flow and value", ocf_line,
        (f"historical owner cash flow: {money(historic_owner_cash_flow)} = {money(info['historic_net_income'])} + {money(info['historic_depreciation'] + info['historic_amortization'])} - {money(info['historic_capex'])}; historic; Form 10 information statement, Combined Statements of Cash Flows" if historic_owner_cash_flow is not None else "historical owner cash flow: not known"),
        *value_lines, price_line, "",
        "## Liquidity",
        (f"median daily dollar volume: {money(liquidity[0])}; source: {liquidity[1]} [liquidity: median(daily value traded)]\n"
         f"purchase size: {'allowed' if 10000 <= liquidity[0] * 0.10 else 'not determined'}; $10,000 project limit against 10% of median daily dollar volume"
         if liquidity else "median daily dollar volume: not known; purchase size: not determined; supply an official LSEG close-and-value-traded export with --market-file."), "",
        "## Judgment", judgment, "", "## Release view", release_view,
        f"conviction: {conviction}; worksheet-method conviction rule.", "", "## Not known",
        "- after-tax operating income",
        *( ["- depreciation and amortization"] if depreciation is None else []),
        *( ["- reliable share count for valuation"] if shares is None else []),
        *( ["- median daily dollar volume"] if liquidity is None else []),
        *( ["- Form 4 open-market purchases"] if reg and not purchases else []), "",
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
    parser.add_argument("--market-file", type=Path, help="Official LSEG CSV or XLSX with Date, Close, and Daily Value Traded; kept outside the repository.")
    args = parser.parse_args()
    print(build(args.run.resolve(), args.no_model, args.market_file))


if __name__ == "__main__":
    main()
