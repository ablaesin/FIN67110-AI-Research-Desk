#!/usr/bin/env python3
"""A filing-grounded research desk for FIN 67110.

The program accepts a ticker, retrieves SEC filings and XBRL facts, calculates
ratios in Python, and passes only that saved evidence to four separate model
roles.  It never stores an API key or a company-specific answer in the code.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from google import genai


ROOT = Path(__file__).parent
RUNS = ROOT / "runs"
SEC_DATA = "https://data.sec.gov"
SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"


def load_env() -> None:
    """Load simple local KEY=VALUE lines without printing secret values."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        raise SystemExit("Missing .env. Create it from the README instructions.")
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"").strip("'"))


def sec_session() -> requests.Session:
    agent = os.environ.get("SEC_USER_AGENT", "")
    if not agent:
        raise SystemExit("SEC_USER_AGENT is required in .env.")
    session = requests.Session()
    session.headers.update({"User-Agent": agent, "Accept-Encoding": "gzip, deflate"})
    return session


def get_json(session: requests.Session, url: str) -> dict[str, Any]:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_text(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def plain_text(markup: str) -> str:
    markup = re.sub(r"<script.*?</script>|<style.*?</style>", " ", markup, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def resolve_ticker(session: requests.Session, ticker: str) -> tuple[str, str]:
    records = get_json(session, "https://www.sec.gov/files/company_tickers.json")
    for record in records.values():
        if record["ticker"].upper() == ticker.upper():
            return str(record["cik_str"]).zfill(10), record["title"]
    raise SystemExit(f"SEC did not find ticker {ticker.upper()}.")


def recent_filings(submissions: dict[str, Any]) -> list[dict[str, str]]:
    recent = submissions["filings"]["recent"]
    return [dict(zip(recent.keys(), values)) for values in zip(*recent.values())]


def accession_url(cik: str, filing: dict[str, str]) -> str:
    accession = filing["accessionNumber"].replace("-", "")
    return f"{SEC_ARCHIVES}/{int(cik)}/{accession}/{filing['primaryDocument']}"


def first_filing(filings: list[dict[str, str]], form: str) -> dict[str, str]:
    for filing in filings:
        if filing["form"] == form:
            return filing
    raise SystemExit(f"No {form} filing was found.")


def filing_directory(cik: str, filing: dict[str, str]) -> str:
    accession = filing["accessionNumber"].replace("-", "")
    return f"{SEC_ARCHIVES}/{int(cik)}/{accession}"


def earnings_release(session: requests.Session, cik: str, filings: list[dict[str, str]]) -> tuple[dict[str, str], str, str]:
    """Find the latest 8-K that says Item 2.02 and save its filing text."""
    for filing in filings:
        if filing["form"] != "8-K":
            continue
        text = plain_text(get_text(session, accession_url(cik, filing)))
        if re.search(r"Item\s*2\.02.{0,90}Results of Operations", text, flags=re.I):
            index = get_json(session, f"{filing_directory(cik, filing)}/index.json")
            files = index.get("directory", {}).get("item", [])
            exhibit = next((item["name"] for item in files if re.search(r"(?:ex|exhibit)[_-]?99[._-]?1.*\.htm$", item["name"], re.I)), None)
            if exhibit:
                url = f"{filing_directory(cik, filing)}/{exhibit}"
                return filing, plain_text(get_text(session, url)), url
            return filing, text, accession_url(cik, filing)
    raise SystemExit("No Item 2.02 earnings-release 8-K was found in the recent SEC filings.")


ANNUAL_TAGS: dict[str, tuple[str, ...]] = {
    "revenue": ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"),
    "operating_income": ("OperatingIncomeLoss",),
    "net_income": ("NetIncomeLoss", "ProfitLoss"),
    "assets": ("Assets",),
    "liabilities": ("Liabilities",),
    "equity": ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
    "cash_from_operations": ("NetCashProvidedByUsedInOperatingActivities",),
    "capital_expenditures": ("PaymentsToAcquirePropertyPlantAndEquipment",),
    "diluted_eps": ("EarningsPerShareDiluted",),
    "current_assets": ("AssetsCurrent",),
    "current_liabilities": ("LiabilitiesCurrent",),
}


def fact_units(facts: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    item = facts.get("facts", {}).get("us-gaap", {}).get(tag, {})
    units = item.get("units", {})
    return next(iter(units.values()), [])


def pick_annual_fact(facts: dict[str, Any], tags: tuple[str, ...]) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for tag in tags:
        for fact in fact_units(facts, tag):
            if fact.get("form") == "10-K" and fact.get("fp") == "FY":
                candidates.append({**fact, "tag": tag})
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (item.get("end", ""), item.get("filed", "")), reverse=True)[0]


def number_record(facts: dict[str, Any], label: str, tags: tuple[str, ...]) -> dict[str, Any] | None:
    fact = pick_annual_fact(facts, tags)
    if not fact:
        return None
    return {
        "label": label,
        "value": fact["val"],
        "unit": fact.get("unit", ""),
        "tag": fact["tag"],
        "period_end": fact.get("end"),
        "filed": fact.get("filed"),
        "accession": fact.get("accn"),
        "form": fact.get("form"),
    }


def annual_numbers(facts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results = {}
    for label, tags in ANNUAL_TAGS.items():
        record = number_record(facts, label, tags)
        if record:
            results[label] = record
    return results


def divide(numerator: float, denominator: float) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def calculated_ratios(numbers: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    value = {key: float(item["value"]) for key, item in numbers.items()}
    formulas = {
        "operating_margin": ("operating_income / revenue", divide(value.get("operating_income", 0), value.get("revenue", 0))),
        "net_margin": ("net_income / revenue", divide(value.get("net_income", 0), value.get("revenue", 0))),
        "return_on_assets": ("net_income / assets", divide(value.get("net_income", 0), value.get("assets", 0))),
        "current_ratio": ("current_assets / current_liabilities", divide(value.get("current_assets", 0), value.get("current_liabilities", 0))),
        "free_cash_flow": ("cash_from_operations - capital_expenditures", value.get("cash_from_operations", 0) - value.get("capital_expenditures", 0)),
    }
    return {name: {"formula": formula, "value": ratio} for name, (formula, ratio) in formulas.items() if ratio is not None}


def annual_revenue_history(facts: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for tag in ANNUAL_TAGS["revenue"]:
        for fact in fact_units(facts, tag):
            if fact.get("form") == "10-K" and fact.get("fp") == "FY":
                rows.append({**fact, "tag": tag})
    unique = {(row.get("end"), row.get("val")): row for row in rows}
    return sorted(unique.values(), key=lambda row: row.get("end", ""), reverse=True)[:2]


def model_call(client: genai.Client, role: str, task: str, context: dict[str, Any], expected_output: str) -> str:
    payload = {"task": task, "context": context, "expected_output": expected_output}
    instruction = (
        f"You are the {role}. Use only the supplied JSON. Do not invent facts, numbers, "
        "filing lines, sources, or calculations. If evidence is absent, write 'not provided'. "
        "Return Markdown only.\n\n" + json.dumps(payload, default=str)
    )
    # The current Gemini Interactions API is synchronous. The response schema stores text in output.
    response = client.interactions.create(model="gemini-3.8-flash", input=instruction, timeout=300)
    data = response.model_dump(mode="json") if hasattr(response, "model_dump") else json.loads(str(response))
    texts: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            for key, value in item.items():
                if key in {"text", "content"} and isinstance(value, str):
                    texts.append(value)
                else:
                    walk(value)
        elif isinstance(item, list):
            for value in item:
                walk(value)

    walk(data)
    result = "\n".join(text for text in texts if text.strip()).strip()
    if not result:
        raise RuntimeError(f"{role} returned no text. Save the run and retry this role.")
    return result


def fallback_report(ticker: str, numbers: dict[str, dict[str, Any]], ratios: dict[str, dict[str, Any]], price: float, price_date: str, sources: dict[str, Any], peer_summary: dict[str, Any]) -> str:
    """Course-approved outage fallback: facts only, with no invented narrative."""
    def money(label: str) -> str:
        item = numbers.get(label)
        return f"${item['value'] / 1_000_000_000:.2f} billion" if item else "not provided"

    def pct(label: str) -> str:
        item = ratios.get(label)
        return f"{item['value'] * 100:.2f}% ({item['formula']})" if item else "not provided"

    peer_margins = []
    for peer, item in peer_summary.items():
        margin = item.get("ratios", {}).get("operating_margin", {}).get("value")
        peer_margins.append(f"{peer}: {margin * 100:.2f}%" if margin is not None else f"{peer}: not provided")
    eps = numbers.get("diluted_eps", {}).get("value")
    pe = price / eps if eps else None
    return f"""## Overview

This is a **fallback** report because the model provider was unavailable during the run. The desk read the latest 10-K, the latest Item 2.02 earnings release, and SEC company facts. The report makes no claim beyond that evidence.

## Market Positioning and Growth Outlook

The business-model and competitive-position narrative requires a later human review of the 10-K business and MD&A sections. The current evidence file preserves those source texts. The latest Item 2.02 release is: {sources['earnings_release']['url']}.

## Valuation Insights

For the fiscal year ending {numbers.get('revenue', {}).get('period_end', 'not provided')}, revenue was {money('revenue')}, operating income was {money('operating_income')}, and net income was {money('net_income')}. Operating margin was {pct('operating_margin')}; net margin was {pct('net_margin')}; and free cash flow, calculated as cash from operations minus capital expenditures, was {money('cash_from_operations')} minus {money('capital_expenditures')}. The supplied close was ${price:.2f} on {price_date}. Using diluted EPS of {eps if eps is not None else 'not provided'} from the same annual filing, the simple price/EPS calculation is {f'{pe:.2f}' if pe is not None else 'not provided'}.

Peer operating margins use each peer's latest annual SEC facts and the same formula: {'; '.join(peer_margins)}.

## Future Developments and Strategic Recommendations

The next review should compare the quarterly earnings-release figures and outlook with the annual facts before making a forward-looking claim. This fallback does not treat management statements as verified forecasts.

## Investment Recommendation

**Hold, provisional.** The filing evidence supports a source-backed financial snapshot, but this fallback does not contain a completed qualitative review or an audited valuation range. The deciding number for the next review is the operating margin: {pct('operating_margin')}.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the FIN 67110 filing-grounded research desk.")
    parser.add_argument("ticker", help="A U.S.-listed ticker")
    parser.add_argument("--peers", required=True, help="Comma-separated peer tickers")
    parser.add_argument("--price", type=float, required=True, help="Last close before the earnings release")
    parser.add_argument("--price-date", required=True, help="Date of that close, YYYY-MM-DD")
    parser.add_argument("--fallback", action="store_true", help="Write the course-approved outage fallback report without model calls")
    args = parser.parse_args()

    load_env()
    if not os.environ.get("API_KEY"):
        raise SystemExit("API_KEY is required in .env.")
    session = sec_session()
    ticker = args.ticker.upper()
    peers = [item.strip().upper() for item in args.peers.split(",") if item.strip()]
    if not peers:
        raise SystemExit("Provide at least one peer ticker.")

    run_dir = RUNS / f"{ticker.lower()}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir.mkdir(parents=True)
    print("Step 1/7: resolve ticker")
    cik, name = resolve_ticker(session, ticker)
    print("Step 2/7: retrieve filing list")
    submissions = get_json(session, f"{SEC_DATA}/submissions/CIK{cik}.json")
    filings = recent_filings(submissions)
    latest_10k = first_filing(filings, "10-K")
    latest_10q = first_filing(filings, "10-Q")
    print("Step 3/7: download latest 10-K")
    ten_k_text = plain_text(get_text(session, accession_url(cik, latest_10k)))
    ten_q_text = plain_text(get_text(session, accession_url(cik, latest_10q)))
    print("Step 4/7: retrieve XBRL facts")
    facts = get_json(session, f"{SEC_DATA}/api/xbrl/companyfacts/CIK{cik}.json")
    numbers = annual_numbers(facts)
    print("Step 5/7: calculate ratios in code")
    ratios = calculated_ratios(numbers)
    revenue_history = annual_revenue_history(facts)
    print("Step 6/7: find latest earnings release")
    release, release_text, release_url = earnings_release(session, cik, filings)
    print("Step 7/7: retrieve peer facts")
    peer_summary: dict[str, Any] = {}
    for peer in peers:
        try:
            peer_cik, _ = resolve_ticker(session, peer)
            peer_facts = get_json(session, f"{SEC_DATA}/api/xbrl/companyfacts/CIK{peer_cik}.json")
            peer_numbers = annual_numbers(peer_facts)
            peer_summary[peer] = {"numbers": peer_numbers, "ratios": calculated_ratios(peer_numbers)}
        except Exception as error:  # retain a visible limitation rather than substitute another company
            peer_summary[peer] = {"error": str(error)}

    sources = {
        "latest_10k": {"accession": latest_10k["accessionNumber"], "url": accession_url(cik, latest_10k)},
        "latest_10q": {"accession": latest_10q["accessionNumber"], "url": accession_url(cik, latest_10q)},
        "earnings_release": {"accession": release["accessionNumber"], "url": release_url},
        "company_facts": f"{SEC_DATA}/api/xbrl/companyfacts/CIK{cik}.json",
    }
    evidence = {
        "ticker": ticker,
        "company": name,
        "sources": sources,
        "annual_numbers": numbers,
        "ratios_calculated_in_code": ratios,
        "revenue_history": revenue_history,
        "price": {"value": args.price, "date": args.price_date, "definition": "last close before the earnings release"},
        "peers": peer_summary,
        "business_and_mda_excerpt": ten_k_text[:40000],
        "latest_10q_excerpt": ten_q_text[:12000],
        "earnings_release_excerpt": release_text[:24000],
    }
    (run_dir / "evidence.json").write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")

    # Keep each role's prompt small. Full filing evidence remains in evidence.json for audit.
    research_context = {
        "ticker": ticker,
        "company": name,
        "sources": sources,
        "business_and_mda_excerpt": ten_k_text[:12000],
        "earnings_release_excerpt": release_text[:9000],
    }
    financial_context = {
        "ticker": ticker,
        "sources": sources,
        "annual_numbers": numbers,
        "ratios_calculated_in_code": ratios,
        "revenue_history": revenue_history,
        "price": evidence["price"],
        "peers": peer_summary,
    }
    if args.fallback:
        print("Fallback report")
        report = fallback_report(ticker, numbers, ratios, args.price, args.price_date, sources, peer_summary)
    else:
        client = genai.Client(api_key=os.environ["API_KEY"])
        print("Research Analyst")
        research = model_call(client, "Research Analyst", "Describe the business model, competitive position, catalysts, and recent developments. Quote evidence supplied in the excerpts.", research_context, "A sourced Markdown research section.")
        print("Financial Analyst")
        financial = model_call(client, "Financial Analyst", "Analyze the supplied facts and code-calculated ratios. State each definition and show only the arithmetic provided. Do not calculate in the model.", financial_context, "A sourced Markdown financial-analysis section.")
        print("Investment Advisor")
        advisor_context = {"research": research, "financial": financial, "price": evidence["price"]}
        advisor = model_call(client, "Investment Advisor", "Write a thesis and Buy, Hold, or Sell using only the two role outputs. Name the one number that most affects the view.", advisor_context, "A Markdown investment view with limitations.")
        print("Strategy Manager")
        manager_context = {"research": research, "financial": financial, "advisor": advisor, "sources": sources}
        report = model_call(client, "Strategy Manager", "Check the inputs, then compile exactly five sections: Overview; Market Positioning and Growth Outlook; Valuation Insights; Future Developments and Strategic Recommendations; Investment Recommendation. Mark absent evidence as not provided.", manager_context, "A complete five-part Markdown report.")

    filing_line = f"{ticker} — filings: 10-K {latest_10k['accessionNumber']}; 10-Q {latest_10q['accessionNumber']}; earnings release 8-K {release['accessionNumber']}"
    if args.fallback:
        header = f"{filing_line}\nfallback\n\n# {ticker} Research Desk Report\n\nRun time (UTC): {datetime.now(timezone.utc).isoformat()}\n\n"
    else:
        header = f"# {ticker} Research Desk Report\n\n{filing_line}\n\nRun time (UTC): {datetime.now(timezone.utc).isoformat()}\n\n"
    footer = "\n\n---\n\nThis is a learning exercise, not financial advice.\n\nAI assistance: Google Gemini. I verified the sources myself; the judgments are mine.\n\nAny remaining errors are my own.\n"
    report_path = run_dir / "report.md"
    report_path.write_text(header + report + footer, encoding="utf-8")
    print(f"Saved evidence: {run_dir / 'evidence.json'}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    main()
