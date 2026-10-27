# FIN 67110 AI Research Desk

Purdue University — Mastering AI for Finance

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
   .venv/bin/python desk.py TICKER --peers PEER1,PEER2,PEER3 --price 123.45 --price-date YYYY-MM-DD
   ```

The report file begins with the filing accession numbers and run time. The matching
`evidence.json` preserves each XBRL tag, period, accession number, and calculation.

## Checkpoint 1 audit

Before submission, copy the course report-audit table into a Markdown file. Mark the
eleven core claims against the filings by hand, then audit every other Financial
Analyst number, the five-part template, and the recommendation. Do not use AI for
the audit marks.
