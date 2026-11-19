# Lab 09 — NVDA Three-Column Check

Partner-selected name: NVIDIA Corporation (`NVDA`). The parts-alone column is the verified
agent-team report plus the standalone worksheet. The joined column is `final_report.md`. The
filing check uses the saved 10-K, 10-Q, and Nov. 17, 2026 8-K, Exhibit 99.1. `Same` means the
parts-alone and joined columns do not differ. It does not mean the filing supports the claim.

| Parts alone | Joined desk final report | Filing check |
|---|---|---|
| **Revenue:** $215.938B | **Revenue:** $215.938B — same | 10-K `0001045810-26-000021`, Consolidated Statements of Income / XBRL `Revenues`: supported. |
| **Prior-year revenue:** $130.497B | **Prior-year revenue:** $130.497B — same | 10-K `0001045810-26-000021`, Consolidated Statements of Income: supported. |
| **Operating income:** $130.387B | **Operating income:** $130.387B — same | 10-K / XBRL `OperatingIncomeLoss`: supported. |
| **Net income:** $120.067B | **Net income:** $120.067B — same | 10-K / XBRL `NetIncomeLoss`: supported. |
| **Total assets:** $206.803B | **Total assets:** $206.803B — same | 10-K / XBRL `Assets`: supported. |
| **Total liabilities:** $49.510B | **Total liabilities:** $49.510B — same | 10-K / XBRL `Liabilities`: supported. |
| **Depreciation and amortization:** $2.843B | **Depreciation and amortization:** $2.843B — same | 10-K / XBRL `DepreciationDepletionAndAmortization`: supported. |
| **Operating margin:** 60.38% | **Operating margin:** 60.38% — same | Code calculation: $130.387B / $215.938B = 60.3817%; supported. |
| **Current ratio:** 3.91 | **Current ratio:** 3.91 — same | Code calculation: $125.605B / $32.163B = 3.9053; supported. |
| **Groq license agreement:** December 2025 | **Groq license agreement:** December 2025 — corrected | The 10-K says “In December 2025”; it does not give a day. |
| **Capital expenditures:** $138.735M, period 2012-01-29 | **Capital expenditures:** $138.735M, period 2012-01-29 | **Not comparable to FY 2026.** Evidence cites 10-K `0001045810-12-000013`, XBRL `PaymentsToAcquirePropertyPlantAndEquipment`. The worksheet does not use this stale fact in valuation. |
| **View:** not computed; after-tax operating income is unavailable | **View:** not computed — same | The worksheet method requires after-tax operating income. Net income is not used as a substitute. |
| **One number — official pre-filing close:** $150.96 on Nov. 17, 2026 | **Official pre-filing close:** $150.96 on Nov. 17, 2026 — same | LSEG Workspace `NVDA.O` Price History export. The earnings 8-K `0001045810-26-000088` was accepted at 4:20:51 PM Eastern, after the regular close. |

## Result

The join added the worksheet view, official close, liquidity result, and spinoff fields marked
not applicable. The table keeps the eleven checked financial claims and the required view and
one-number rows. The exact Groq date is corrected to December 2025. The stale capital-expenditure
fact remains recorded as a source problem, but the worksheet does not use it in a valuation.
