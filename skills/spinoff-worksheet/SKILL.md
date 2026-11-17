---
name: spinoff-worksheet
description: Build a filing-grounded spinoff worksheet from a saved FIN 67110 agent-team run.
---

# Spinoff worksheet

Run this skill only after the agent team has saved a run. It reads the run's `evidence.json`
and saved filing text. It never asks a model to calculate a number.

```bash
.venv/bin/python skills/spinoff-worksheet/worksheet.py runs/ampx-YYYYMMDDTHHMMSSZ
```

The output is `worksheet.md` in the same run folder. Each financial fact has a machine-readable
claim marker on the same line. The hook reads the worksheet itself and checks those markers:

```bash
.venv/bin/python skills/spinoff-worksheet/worksheet_hook.py runs/ampx-YYYYMMDDTHHMMSSZ/worksheet.md
```

The worksheet adds a dated copy to `worksheets/` in the run folder. If the ticker is in the
seeker registry, it saves the registry filing with the run before it reads it. If the ticker is
not in that registry, all spinoff-only fields say `not applicable`.

Use `--no-model` only for an offline test. The normal command makes one model call for the
judgment. The model receives worksheet facts only; code calculates all values and adds liquidity
after the call.
