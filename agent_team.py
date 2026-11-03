#!/usr/bin/env python3
"""FIN 67110 agent team: a fixed LangGraph workflow with an always-on verifier."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

from google import genai
from langgraph.graph import END, START, StateGraph

import desk

ROOT = Path(__file__).parent
RUNS = ROOT / "runs"
ROLES = ROOT / "roles"
SECTION_NAMES = ["Overview", "Market Positioning and Growth Outlook", "Valuation Insights", "Future Developments and Strategic Recommendations", "Investment Recommendation"]


class TeamState(TypedDict, total=False):
    run_dir: str
    ticker: str
    evidence: dict[str, Any]
    research: str
    financial: str
    advisor: str
    report: str
    verified_report: str


def save_node(run_dir: Path, name: str, payload: dict[str, Any]) -> None:
    (run_dir / "nodes").mkdir(exist_ok=True)
    (run_dir / "nodes" / f"{name}.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def role_text(name: str) -> str:
    path = ROLES / f"{name}.md"
    if not path.exists():
        raise SystemExit(f"Missing {path}. Write this persona yourself before a full team run.")
    return path.read_text(encoding="utf-8")


def node_steps(state: TeamState) -> dict[str, Any]:
    print("steps")
    run_dir = Path(state["run_dir"])
    evidence = state["evidence"]
    save_node(run_dir, "steps", {"input": {"ticker": state["ticker"]}, "output": evidence})
    return {}


def call_node(name: str, output_key: str, task: str, context_keys: list[str], expected: str):
    def run(state: TeamState) -> dict[str, Any]:
        print(name.replace("_", " "))
        run_dir = Path(state["run_dir"])
        context = {key: state[key] for key in context_keys}
        if name in {"research_analyst", "financial_analyst"}:
            evidence = state["evidence"]
            if name == "research_analyst":
                context["evidence"] = {"sources": evidence["sources"], "business_and_mda_excerpt": evidence["business_and_mda_excerpt"],
                                       "latest_10q_excerpt": evidence["latest_10q_excerpt"], "earnings_release_excerpt": evidence["earnings_release_excerpt"],
                                       "annual_numbers": evidence["annual_numbers"], "ratios_calculated_in_code": evidence["ratios_calculated_in_code"]}
            else:
                context["evidence"] = {"sources": evidence["sources"], "annual_numbers": evidence["annual_numbers"],
                                       "ratios_calculated_in_code": evidence["ratios_calculated_in_code"], "revenue_history": evidence["revenue_history"],
                                       "price": evidence["price"], "peers": evidence["peers"]}
        elif name == "investment_advisor":
            context["price"] = state["evidence"]["price"]
            context["peer_comparison"] = state["evidence"]["peers"]
        elif name == "strategy_manager":
            context["sources"] = state["evidence"]["sources"]
        payload = {"task": task, "context": context, "expected_output": expected}
        output = desk.model_call(genai.Client(api_key=__import__("os").environ["API_KEY"]), name.replace("_", " ").title(), task, context, expected, role_text(name))
        if name == "strategy_manager":
            missing = [section for section in SECTION_NAMES if section.lower() not in output.lower()]
            if missing:
                section_role = {"Overview": ("research", "research_analyst"),
                                "Market Positioning and Growth Outlook": ("research", "research_analyst"),
                                "Valuation Insights": ("financial", "financial_analyst"),
                                "Future Developments and Strategic Recommendations": ("advisor", "investment_advisor"),
                                "Investment Recommendation": ("advisor", "investment_advisor")}
                state_key, retry_role = section_role[missing[0]]
                retry_context = {"previous_output": state[state_key], "evidence": state["evidence"]}
                context[state_key] = desk.model_call(genai.Client(api_key=os.environ["API_KEY"]), retry_role.replace("_", " ").title(),
                                                       f"Return only the missing report part: {missing[0]}. This is the role's single permitted retry.",
                                                       retry_context, "A sourced Markdown section.", role_text(retry_role))
                retry_task = task + ". Recompile after the fixed role output. The first draft omitted: " + "; ".join(missing) + "."
                output = desk.model_call(genai.Client(api_key=os.environ["API_KEY"]), "Strategy Manager", retry_task, context, expected, role_text(name))
                if [section for section in SECTION_NAMES if section.lower() not in output.lower()]:
                    raise RuntimeError("Strategy Manager used its one retry and still omitted a required section.")
        if output_key == "report":
            sources = state["evidence"]["sources"]
            output = (f"{state['ticker']} — filings: 10-K {sources['latest_10k']['accession']}; "
                      f"10-Q {sources['latest_10q']['accession']}; earnings release 8-K "
                      f"{sources['earnings_release']['accession']}\n\n" + output)
        save_node(run_dir, name, {"input": payload, "output": output})
        return {output_key: output}
    return run


def number_forms(value: Any) -> set[str]:
    value = float(value)
    forms = {str(value), f"{value:.2f}", f"${value:.2f}", f"${value / 1_000_000_000:.3f} billion", f"${value / 1_000_000_000:.2f} billion"}
    if value.is_integer():
        forms.update({f"{value:,.0f}", f"${value:,.0f}"})
    return forms


def verifier_marks(report: str, evidence: dict[str, Any]) -> list[dict[str, str]]:
    marks: list[dict[str, str]] = []
    labels = {"diluted_eps": ("diluted EPS", "diluted earnings per share"), "revenue": ("revenue",),
              "operating_income": ("operating income was", "operating income of"), "net_income": ("net income",)}
    lower = report.lower()
    for key, aliases in labels.items():
        item = evidence.get("annual_numbers", {}).get(key)
        if key == "diluted_eps":
            matches = re.findall(r"\$([0-9]+(?:\.[0-9]{2})?)\s+per diluted share", evidence.get("earnings_release_excerpt", ""), re.I)
            if matches:
                item = {"value": max(map(float, matches)), "tag": "earnings-release per-share line", "period_end": "latest earnings release"}
        if not item or not any(alias.lower() in lower for alias in aliases):
            continue
        forms = number_forms(item["value"])
        positions = [match.start() for alias in aliases for match in re.finditer(re.escape(alias.lower()), lower)]
        correct = any(form.lower() in lower[position:position + 220] for position in positions for form in forms)
        source = f"XBRL `{item['tag']}`, period {item['period_end']}"
        marks.append({"claim": aliases[0], "mark": "Correct" if correct else "Wrong", "correction": "" if correct else f"{item['value']} ({source})"})
    for stated, current, prior in re.findall(r"Revenue growth was ([0-9]+(?:\.[0-9]+)?)%, using revenue of \$([0-9,]+) and \$([0-9,]+)", report, re.I):
        computed = (float(current.replace(",", "")) / float(prior.replace(",", "")) - 1) * 100
        if abs(float(stated) - computed) > 0.05:
            marks.append({"claim": "revenue-growth ratio", "mark": "Wrong", "correction": f"{computed:.2f}% from the quoted inputs"})
    if not marks:
        marks.append({"claim": "sourced numbers", "mark": "Unsupported", "correction": "No recognizable sourced number was found."})
    return marks


def node_verifier(state: TeamState) -> dict[str, Any]:
    print("verifier")
    run_dir, report, evidence = Path(state["run_dir"]), state["report"], state["evidence"]
    marks = verifier_marks(report, evidence)
    desk.load_env()
    semantic_check = desk.model_call(
        genai.Client(api_key=os.environ["API_KEY"]), "Verifier",
        "Check the cited factual claims only. Do not assess the Investment Recommendation thesis.",
        {"compiled_report": report, "saved_filing_evidence": evidence},
        "A Markdown table that marks every sourced numeric claim Correct, Wrong, or Unsupported, with a correction and source for each Wrong or Unsupported claim.", role_text("verifier"))
    rows = "\n".join(f"| {m['claim']} | {m['mark']} | {m['correction'] or '—'} |" for m in marks)
    first, *rest = report.splitlines()
    verified = "\n".join([first, "", "## Code verifier marks", "| Claim | Mark | Correction and source |", "|---|---|---|", rows, "", "## Model semantic marks", semantic_check, "", *rest])
    (run_dir / "verified_report.md").write_text(verified, encoding="utf-8")
    save_node(run_dir, "verifier", {"input": {"report": report, "facts": evidence.get("annual_numbers", {})}, "output": {"code_marks": marks, "semantic_check": semantic_check}})
    return {"verified_report": verified}


def build_graph():
    graph = StateGraph(TeamState)
    graph.add_node("steps", node_steps)
    graph.add_node("research_analyst", call_node("research_analyst", "research", "Write the research section from supplied filing evidence.", [], "A sourced Markdown research section."))
    graph.add_node("financial_analyst", call_node("financial_analyst", "financial", "Analyze supplied facts and code ratios only.", [], "A sourced Markdown financial section."))
    graph.add_node("investment_advisor", call_node("investment_advisor", "advisor", "Write the thesis using the two analyst outputs only.", ["research", "financial"], "A Markdown investment view."))
    graph.add_node("strategy_manager", call_node("strategy_manager", "report", "Compile exactly these five sections: " + "; ".join(SECTION_NAMES), ["research", "financial", "advisor"], "A five-part report."))
    graph.add_node("verifier", node_verifier)
    graph.add_edge(START, "steps"); graph.add_edge("steps", "research_analyst"); graph.add_edge("research_analyst", "financial_analyst")
    graph.add_edge("financial_analyst", "investment_advisor"); graph.add_edge("investment_advisor", "strategy_manager"); graph.add_edge("strategy_manager", "verifier"); graph.add_edge("verifier", END)
    return graph.compile()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", nargs="?")
    parser.add_argument("--peers")
    parser.add_argument("--price", type=float)
    parser.add_argument("--price-date")
    parser.add_argument("--verify-only", type=Path)
    parser.add_argument("--seed-eps-error", type=Path, metavar="RUN", help="Copy RUN, raise diluted EPS by $1, then verify the copy.")
    parser.add_argument("--invented-growth-error", type=Path, metavar="RUN", help="Copy RUN, add a growth claim four points too high, then verify the copy.")
    args = parser.parse_args()
    if args.verify_only:
        folder = args.verify_only
        report = (folder / "report.md").read_text(encoding="utf-8")
        evidence = json.loads((folder / "evidence.json").read_text(encoding="utf-8"))
        node_verifier({"run_dir": str(folder), "report": report, "evidence": evidence})
        print(folder / "verified_report.md")
        return
    if args.seed_eps_error:
        original = args.seed_eps_error
        evidence = json.loads((original / "evidence.json").read_text(encoding="utf-8"))
        report = (original / "report.md").read_text(encoding="utf-8")
        match = re.search(r"\$([0-9]+(?:\.[0-9]{2})?)\s+per diluted share", report, re.I)
        if not match:
            raise RuntimeError("The report did not contain a diluted-EPS per-share line to seed.")
        eps = float(match.group(1))
        seeded = original.parent / f"{original.name}-seeded-eps-error-{datetime.now(timezone.utc).strftime('%H%M%S')}"
        if seeded.exists():
            raise SystemExit(f"Seeded run already exists: {seeded}")
        shutil.copytree(original, seeded, ignore=shutil.ignore_patterns("verified_report.md"))
        report_path = seeded / "report.md"
        changed = report.replace(f"${eps:.2f}", f"${eps + 1:.2f}")
        if changed == report:
            raise RuntimeError("The report did not contain the diluted-EPS figure to seed.")
        report_path.write_text(changed, encoding="utf-8")
        node_verifier({"run_dir": str(seeded), "report": changed, "evidence": evidence})
        print(seeded / "verified_report.md")
        return
    if args.invented_growth_error:
        original = args.invented_growth_error
        evidence = json.loads((original / "evidence.json").read_text(encoding="utf-8"))
        revenue = float(evidence["annual_numbers"]["revenue"]["value"])
        prior = float(evidence["revenue_history"][1]["val"])
        true_growth = (revenue / prior - 1) * 100
        seeded = original.parent / f"{original.name}-invented-growth-error-{datetime.now(timezone.utc).strftime('%H%M%S')}"
        shutil.copytree(original, seeded, ignore=shutil.ignore_patterns("verified_report.md"))
        report_path = seeded / "report.md"
        report = report_path.read_text(encoding="utf-8")
        report += f"\n\nInvented test claim: Revenue growth was {true_growth + 4:.2f}%, using revenue of ${revenue:,.0f} and ${prior:,.0f}.\n"
        report_path.write_text(report, encoding="utf-8")
        node_verifier({"run_dir": str(seeded), "report": report, "evidence": evidence})
        print(seeded / "verified_report.md")
        return
    if not args.ticker or not args.peers or args.price is None or not args.price_date:
        raise SystemExit("Provide TICKER --peers PEER1,PEER2 --price PRICE --price-date YYYY-MM-DD.")
    # Reuse the audited seven code steps to collect and save SEC evidence. The fallback mode makes
    # no model calls; the LangGraph below is the only agent workflow used for the final report.
    desk.load_env()
    before = set(RUNS.glob(f"{args.ticker.lower()}-*"))
    subprocess.run([sys.executable, str(ROOT / "desk.py"), args.ticker, "--peers", args.peers,
                    "--price", str(args.price), "--price-date", args.price_date, "--fallback"],
                   check=True, cwd=ROOT)
    created = sorted(set(RUNS.glob(f"{args.ticker.lower()}-*")) - before)
    if len(created) != 1:
        raise RuntimeError("The evidence steps did not create exactly one run folder.")
    run_dir = created[0]
    evidence = json.loads((run_dir / "evidence.json").read_text(encoding="utf-8"))
    result = build_graph().invoke({"run_dir": str(run_dir), "ticker": args.ticker.upper(), "evidence": evidence})
    (run_dir / "report.md").write_text(result["report"], encoding="utf-8")
    print(run_dir / "verified_report.md")


if __name__ == "__main__":
    main()
