---
name: spinoff-seeker
description: Find and rank U.S. corporate spinoffs from SEC EDGAR. Use when the user asks for a spinoff screen, a spinoff registry, or an EDGAR-based spinoff report.
---

# Spinoff seeker

Run the tests before every change:

```bash
.venv/bin/python skills/spinoff-seeker/tests.py
```

Run the seeker with a start date. The SEC User-Agent must be in the repository's `.env` file.

```bash
.venv/bin/python skills/spinoff-seeker/seeker.py 2025-11-10
```

The skill reads only SEC EDGAR for filing facts. It does not estimate a missing fact. A filing
reference is saved beside every established fact. Complete `factors.json` yourself before you
rely on a rank. `ticker` is optional: without it, the candidate stays unranked rather than using
an uncertain ticker.

The output is in `skills/spinoff-seeker/output/`. Do not treat its screen as a recommendation.

The closes reader uses an LSEG or WRDS CSV export stored outside the repository. It needs columns
`ticker,date,close`; the `close` must be the official daily close, not an adjusted close.

```bash
.venv/bin/python skills/spinoff-seeker/closes_reader.py TICKER YYYY-MM-DD --csv /path/outside/repo/closes.csv
```
