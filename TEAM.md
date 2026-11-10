# Team Ledger — Abraham Blaesing, Brody Oliver, Gabriel DePalma

This is the shared working plan for Lab 06. It is a plan, not a claim that work was done by a
member who has not done it.

## Start here

```bash
git pull origin main
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python skills/spinoff-seeker/tests.py
```

Each member creates a local `.env`. Never commit it and never send an API key in chat or GitHub.
`SEC_USER_AGENT` must contain that member's name and Purdue email for every EDGAR request.

## Lab 06 examples for the paired check

### Spinoff: Honeywell Aerospace Inc. (HONA)

- Parent: Honeywell.
- Form 10-12B/A information statement: <https://www.sec.gov/Archives/edgar/data/2089271/000162828026041399/exhibit991-10x12ba2.htm>
- The information statement says one Aerospace share for every two Honeywell shares held at the
  close of business on June 15, 2026. It says the distribution is at 12:01 a.m. New York City
  time on June 29, 2026, and the expected NASDAQ ticker is HONA.
- Check the filing itself before relying on any fact. The seeker must cite the filing and section,
  and must use the first official close after June 29, 2026, not a when-issued price.

### Non-spinoff: BioStem Technologies, Inc.

- Form 10-12B/A: <https://www.sec.gov/Archives/edgar/data/1658678/000121390026081252/ea0299134-1012ba1_biostem.htm>
- This filing does not contain an information statement that shows a parent distributing the
  business. The seeker must drop it with that reason and this filing beside it.

## This week's live record

- Target: TransDigm Group Incorporated (`TDG`). Its Nov. 10, 2026 8-K with Items 2.02 and 9.01
  was accepted by EDGAR at 6:32:12 AM Eastern. Its earnings release is Exhibit 99.1:
  <https://www.sec.gov/Archives/edgar/data/1260221/000126022126000073/tdg-20261110.htm>
- The last official close before that pre-market release was $1,218.85 on Nov. 9, 2026, from the
  LSEG Workspace `TDG.N` regular-close export.
- A verified report is saved locally in `runs/tdg-20261110T151542Z/verified_report.md`.
- Brightspace had no visible Live record location when this run was completed. No Brightspace
  upload is claimed. Keep the report and this row for Checkpoint 3.

| Ticker | Release filing | EDGAR Accepted time | Verified report | Brightspace upload |
|---|---|---|---|---|
| TDG | 8-K `0001260221-26-000073`, Exhibit 99.1 | Nov. 10, 2026, 6:32:12 AM Eastern | `runs/tdg-20261110T151542Z/verified_report.md` | No visible Live record location; not uploaded |

## Initial work owners

These are starting roles. The team can change them in a commit.

- Abraham: seeker code, official-close reader test, and live-report run/upload.
- Gabriel: check the Honeywell and BioStem filings against the two example statements above.
- Brody: review the factor file and the seeker report; recompute one factor's points after the
  seeker produces a ranked candidate.

## Current limits

The factor file is a chapter-based, equal-weight starting hypothesis. It is not validated. The
seeker must leave a name unranked when it lacks a required fact or official close. It must never
estimate a fact. Every report ends: `screens, not recommendations`.
