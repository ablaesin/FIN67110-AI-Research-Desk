# FIN 67110 AI Research Desk

Purdue University — Mastering AI for Finance

## Team

Abraham Blaesing, Brody Oliver, and Gabriel DePalma.

## Run the desk

The desk reads SEC filings and XBRL data, calculates ratios in Python, then calls four
separate Gemini roles: Research Analyst, Financial Analyst, Investment Advisor, and
Strategy Manager. It writes its evidence and a five-part Markdown report in `runs/`.

1. Create a local `.env` file. Never commit it.

   ```text
   API_KEY=your_Google_AI_Studio_key
   SEC_USER_AGENT=Your Name your-purdue-email@purdue.edu
   ```

2. Create the local environment and install the official SDK.

   ```bash
   python -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

3. Run the desk with a ticker, comparable companies, and the last close before the
   earnings release. The price is supplied by the user because SEC filings do not
   contain a market close.

   ```bash
   .venv/bin/python desk.py TICKER --peers PEER1,PEER2,PEER3 --price 123.45 --price-date YYYY-MM-DD --price-source "LSEG Workspace export"
   ```

The report file begins with the filing accession numbers and run time. The matching
`evidence.json` preserves each XBRL tag, period, accession number, and calculation.

## Checkpoint 1 audit

Before submission, copy the course report-audit table into a Markdown file. Mark the
eleven core claims against the filings by hand, then audit every other Financial
Analyst number, the five-part template, and the recommendation. Do not use AI for
the audit marks.

## Checkpoint 2 — LangGraph agent team

Install the packages:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Run the fixed graph on the Lab 04 case:

```bash
.venv/bin/python agent_team.py COST --peers WMT,TGT,BJ --price 904.70 --price-date 2026-09-23 --price-source "LSEG Workspace export"
```

Verify one saved run only:

```bash
.venv/bin/python agent_team.py --verify-only runs/cost-YYYYMMDDTHHMMSSZ
```

Create the two verifier tests from a saved run:

```bash
.venv/bin/python agent_team.py --seed-eps-error runs/cost-YYYYMMDDTHHMMSSZ
.venv/bin/python agent_team.py --invented-growth-error runs/cost-YYYYMMDDTHHMMSSZ
```

The graph order is fixed in code:

```text
steps → Research Analyst → Financial Analyst → Investment Advisor → Strategy Manager → Verifier
```

Code decides the order, inputs, storage, and that the Verifier runs. Each model role decides only its analysis from its assigned state. Each run saves evidence, node inputs and outputs, report, and verified report in its own timestamped folder.

## Lab 06 — Spinoff seeker

The Lab 06 skill is in `skills/spinoff-seeker/`. Complete the factors file by hand, as the lab requires, then run:

```bash
cp skills/spinoff-seeker/factors.template.json skills/spinoff-seeker/factors.json
.venv/bin/python skills/spinoff-seeker/tests.py
.venv/bin/python skills/spinoff-seeker/seeker.py 2025-11-10
```

The seeker sends the required `SEC_USER_AGENT`, reads EDGAR full indexes and Form 10 filings, saves a dated registry and screen, and preserves unknown facts as blank. See its `SKILL.md` for its limits and close-reader command.
