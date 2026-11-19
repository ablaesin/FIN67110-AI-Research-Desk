Filings read: latest_10k 0001769628-26-000104; latest_10q 0001769628-26-000465; earnings_release 0001769628-26-000461

CRWV — filings: 10-K 0001769628-26-000104; 10-Q 0001769628-26-000465; earnings release 8-K 0001769628-26-000461

## Code verifier marks
| Claim | Mark | Correction and source |
|---|---|---|
| diluted EPS | Correct | — |
| revenue | Correct | — |
| operating income was | Correct | — |
| net income | Correct | — |

## Model semantic marks
| Claim / Metric | Reported Value | Evaluated Period | Status | Correction / Supporting Evidence |
| :--- | :--- | :--- | :--- | :--- |
| Revenue | $5.13 billion | FY 2025 (ending 2025-12-31) | Correct | `RevenueFromContractWithCustomerExcludingAssessedTax`: 5,131,000,000 |
| Operating Income | $-0.05 billion | FY 2025 (ending 2025-12-31) | Correct | `OperatingIncomeLoss`: -46,000,000 (rounds to -0.05 billion) |
| Net Income | $-1.17 billion | FY 2025 (ending 2025-12-31) | Correct | `NetIncomeLoss`: -1,167,000,000 (rounds to -1.17 billion) |
| Operating Margin | -0.90% | FY 2025 (ending 2025-12-31) | Correct | Calculated: -46,000,000 / 5,131,000,000 = -0.008965 (-0.90%) |
| Net Margin | -22.74% | FY 2025 (ending 2025-12-31) | Correct | Calculated: -1,167,000,000 / 5,131,000,000 = -0.227441 (-22.74%) |
| Cash from Operations | $3.06 billion | FY 2025 (ending 2025-12-31) | Correct | `NetCashProvidedByUsedInOperatingActivities`: 3,058,000,000 (rounds to 3.06 billion) |
| Capital Expenditures | $10.31 billion | FY 2025 (ending 2025-12-31) | Correct | `PaymentsToAcquirePropertyPlantAndEquipment`: 10,309,000,000 (rounds to 10.31 billion) |
| Close Price | $60.77 | 2026-11-10 | Correct | `saved_facts.price`: 60.77 on 2026-11-10 |
| Diluted EPS | -2.81 | FY 2025 (ending 2025-12-31) | Correct | `EarningsPerShareDiluted`: -2.81 |
| Price/EPS Calculation | -21.63 | FY 2025 | Correct | Calculated: 60.77 / -2.81 = -21.626 (rounds to -21.63) |
| VRT Operating Margin | 17.89% | FY 2025 (ending 2025-12-31) | Correct | VRT ratio `operating_income / revenue`: 0.178858 (17.89%) |
| DELL Operating Margin | 7.18% | FY 2026 (ending 2026-01-30) | Correct | DELL ratio `operating_income / revenue`: 0.071773 (7.18%) |
| EQIX Operating Margin | 20.05% | FY 2025 (ending 2025-12-31) | Correct | EQIX ratio `operating_income / revenue`: 0.200499 (20.05%) |

fallback

# CRWV Research Desk Report

Run time (UTC): 2026-11-19T13:45:51.445377+00:00

## Overview

This is a **fallback** report because the model provider was unavailable during the run. The desk read the latest 10-K, the latest Item 2.02 earnings release, and SEC company facts. The report makes no claim beyond that evidence.

## Market Positioning and Growth Outlook

The business-model and competitive-position narrative requires a later human review of the 10-K business and MD&A sections. The current evidence file preserves those source texts. The latest Item 2.02 release is: https://www.sec.gov/Archives/edgar/data/1769628/000176962826000461/crwv-20261110.htm.

## Valuation Insights

For the fiscal year ending 2025-12-31, revenue was $5.13 billion, operating income was $-0.05 billion, and net income was $-1.17 billion. Operating margin was -0.90% (operating_income / revenue); net margin was -22.74% (net_income / revenue); and free cash flow, calculated as cash from operations minus capital expenditures, was $3.06 billion minus $10.31 billion. The supplied close was $60.77 on 2026-11-10. Using diluted EPS of -2.81 from the same annual filing, the simple price/EPS calculation is -21.63.

Peer operating margins use each peer's latest annual SEC facts and the same formula: VRT: 17.89%; DELL: 7.18%; EQIX: 20.05%.

## Future Developments and Strategic Recommendations

The next review should compare the quarterly earnings-release figures and outlook with the annual facts before making a forward-looking claim. This fallback does not treat management statements as verified forecasts.

## Investment Recommendation

**Hold, provisional.** The filing evidence supports a source-backed financial snapshot, but this fallback does not contain a completed qualitative review or an audited valuation range. The deciding number for the next review is the operating margin: -0.90% (operating_income / revenue).


---

This is a learning exercise, not financial advice.

AI assistance: Google Gemini. Review the listed filing and price sources before relying on this report.

Any remaining errors are our own.

## Worksheet view
# CRWV worksheet

Run: crwv-20261119T134549Z
Method: lab06/worksheet-method.md

## Spinoff facts
parent: not applicable; not applicable
distribution ratio: not applicable; not applicable
distribution dates: not applicable
debt raised and cash to parent: not applicable
parent liabilities and restrictions: not applicable
Form 4 purchases, code P only: not applicable

## Filing facts
after-tax earnings: -$1,167,000,000; historic; 10-K 0001769628-26-000104; XBRL NetIncomeLoss, period 2025-12-31 [claim: annual_numbers.net_income]
capital expenditures: $10,309,000,000; historic; 10-K 0001769628-26-000104; XBRL PaymentsToAcquirePropertyPlantAndEquipment, period 2025-12-31 [claim: annual_numbers.capital_expenditures]
liabilities: $45,967,000,000; historic; 10-K 0001769628-26-000104; XBRL Liabilities, period 2025-12-31 [claim: annual_numbers.liabilities]
cash from operations: $3,058,000,000; historic; 10-K 0001769628-26-000104; XBRL NetCashProvidedByUsedInOperatingActivities, period 2025-12-31 [claim: annual_numbers.cash_from_operations]
depreciation and amortization: $2,454,000,000; historic; 10-K 0001769628-26-000104; XBRL DepreciationDepletionAndAmortization, period 2025-12-31 [claim: annual_numbers.depreciation_and_amortization]
diluted weighted-average shares: $436,000,000; historic; 10-K 0001769628-26-000104; XBRL WeightedAverageNumberOfDilutedSharesOutstanding, period 2025-12-31 [claim: annual_numbers.diluted_weighted_average_shares]

## Owner cash flow and value
owner cash flow for the reported period: -$9,022,000,000 = -$1,167,000,000 + $2,454,000,000 - $10,309,000,000 [computed: annual_numbers.net_income + depreciation - annual_numbers.capital_expenditures]
historical owner cash flow: not known
low case: not computed
middle case: not computed
price against low case: not computed
price: $60.77 on 2026-11-10; LSEG Workspace Price History export; CRWV.O close; last close before the 2026-11-10 16:05:53 Eastern filing [price]

## Liquidity
median daily dollar volume: $3,136,878,789; source: /Users/abrahamblaesing/Downloads/Price History_20261119_0839.xlsx [liquidity: median(daily value traded)]
purchase size: allowed; $10,000 project limit against 10% of median daily dollar volume

## Judgment
CRWV may not be that story because the owner cash flow is "-9022000000.0" and the values are "not provided", against a price of "60.77" on "2026-11-10". The facts are not enough to determine if the name is cheap due to missing values. 

The next filing fact that would change the view is the updated owner cash flow, values, and liquidity.

## Release view
view: not computed; an annual owner-cash-flow value is not available.
conviction: Low / no action; worksheet-method conviction rule.

## Not known
