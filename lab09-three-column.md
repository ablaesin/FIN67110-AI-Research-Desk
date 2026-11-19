# Lab 09 — NVDA Three-Column Check

Partner-selected name: NVIDIA Corporation (`NVDA`). The parts-alone column is the verified
agent-team report plus the standalone worksheet. The joined column is `final_report.md`. The
filing check uses the saved 10-K, 10-Q, and Nov. 17, 2026 8-K, Exhibit 99.1. `Same` means the
parts-alone and joined columns do not differ. It does not mean the filing supports the claim.

| Claim | Parts alone | Joined desk final report | Filing check |
|---|---|---|---|
| Revenue | $215.938B | $215.938B — same | 10-K `0001045810-26-000021`, Consolidated Statements of Income / XBRL `Revenues`: supported. |
| Prior-year revenue | $130.497B | $130.497B — same | 10-K `0001045810-26-000021`, Consolidated Statements of Income: supported. |
| Operating income | $130.387B | $130.387B — same | 10-K / XBRL `OperatingIncomeLoss`: supported. |
| Net income | $120.067B | $120.067B — same | 10-K / XBRL `NetIncomeLoss`: supported. |
| Total assets | $206.803B | $206.803B — same | 10-K / XBRL `Assets`: supported. |
| Total liabilities | $49.510B | $49.510B — same | 10-K / XBRL `Liabilities`: supported. |
| Depreciation and amortization | $2.843B | $2.843B — same | 10-K / XBRL `DepreciationDepletionAndAmortization`: supported. |
| Operating margin | 60.38% | 60.38% — same | Code calculation: $130.387B / $215.938B = 60.3817%; supported. |
| Current ratio | 3.91 | 3.91 — same | Code calculation: $125.605B / $32.163B = 3.9053; supported. |
| Groq license agreement date | Dec. 31, 2025 | Dec. 31, 2025 — same | **Not supported.** The 10-K says only “In December 2025”; it does not give Dec. 31. Keep neither date claim. |
| Capital expenditures | $138.735M, period 2012-01-29 | $138.735M in the joined worksheet — same | **Not comparable to FY 2026.** Evidence cites 10-K `0001045810-12-000013`, XBRL `PaymentsToAcquirePropertyPlantAndEquipment`, period 2012-01-29. Do not use it in the FY 2026 value calculation. |
| View | Worksheet: less than price; middle value $76.18 vs. $150.96 | less than price; same worksheet view added to final report | The filing supports historic inputs and the LSEG export supports $150.96. The view is **not reliable** because its owner-cash-flow calculation subtracts the stale 2012 capital-expenditure amount. |
| One number: official pre-filing close | $150.96 on Nov. 17, 2026 | $150.96 on Nov. 17, 2026 — same | LSEG Workspace `NVDA.O` Price History export. The earnings 8-K `0001045810-26-000088` was accepted at 4:20:51 PM Eastern, after the regular close. |

## Result

The join changed the report by adding the worksheet view, official close, liquidity result, and
spinoff fields marked not applicable. It did not change the eleven checked financial claims. The
table found two retained problems: an unsupported exact Groq date and a stale capital-expenditure
fact. The latter makes the current NVDA worksheet valuation view unfit to rely on until the desk
selects a current-period capital-expenditure fact and reruns the worksheet.
