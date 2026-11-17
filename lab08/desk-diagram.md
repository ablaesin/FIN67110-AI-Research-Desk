# One Desk Diagram

Digital diagram for the team review. It is not presented as a hand drawing.

```mermaid
flowchart LR
  A[one_desk.py command] --> B{ticker or screen}
  B -->|screen| C[spinoff-seeker output]
  B -->|ticker| D[fixed ticker]
  C --> D
  D --> E[agent_team.py]
  E --> F[runs/ticker-timestamp/evidence.json]
  E --> G[verified_report.md]
  F --> H[spinoff-worksheet]
  H --> I[worksheet.md]
  I --> J[worksheet_hook.py]
  G --> K[final_report.md]
  I --> K
  K --> L[report_hook.py]
  L --> M[Lab 05 local page]
```

Fixed order: seeker only for `screen`, pick, agent team, worksheet, worksheet hook,
final report, final-report hook. A model chooses none of these steps.

Files are `evidence.json`, `verified_report.md`, `worksheet.md`, and `final_report.md`.
Calls are the arrows that start a script or a model role.
