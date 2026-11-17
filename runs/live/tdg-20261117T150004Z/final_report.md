Filings read: latest_10k 0001260221-26-000077; latest_10q 0001260221-26-000053; earnings_release 0001260221-26-000073

TDG — filings: 10-K 0001260221-26-000077; 10-Q 0001260221-26-000053; earnings release 8-K 0001260221-26-000073

## Code verifier marks
| Claim | Mark | Correction and source |
|---|---|---|
| revenue | Wrong | 10557000000 (XBRL `Revenues`, period 2026-09-30) |
| net income | Wrong | 2107000000 (XBRL `NetIncomeLoss`, period 2026-09-30) |

## Model semantic marks
| Claim | Status | Evidence |
| :--- | :--- | :--- |
| Net sales of $10,557,000,000 for fiscal year 2026 | Correct | `annual_numbers.revenue` |
| 20% increase in net sales from prior year | Correct | 10-K, p. 20: "Fiscal 2026 net sales increased 20%... to $10,557 million from $8,831 million" |
| Fourth-quarter EBITDA As Defined margin of 53.0% | Correct | `EX-99.1` (Earnings Release), Table 2 |
| Organic expansion reached 14% in the fourth quarter | Correct | `EX-99.1` (Earnings Release), "Quarter-to-Date Results" |
| $1.07 billion purchase of Prince & Izant on September 28, 2026 | Correct | `EX-99.1` (Earnings Release), "Acquisition Activity" |
| Operating Margin: 45.57% | Correct | `ratios_calculated_in_code.operating_margin` |
| Free Cash Flow: $1,913,000,000 | Correct | `ratios_calculated_in_code.free_cash_flow` |
| Negative stockholders' equity of $10,000,000,000 | Correct | `annual_numbers.equity` |
| Total liabilities of $37,921,000,000 | Correct | `annual_numbers.liabilities` |
| Current ratio of 2.90 | Correct | `ratios_calculated_in_code.current_ratio` |
| Issuance of $3.0 billion in 6.75% Senior Secured Notes maturing in 2035 | Correct | `EX-99.1` (Earnings Release), "Financing Activity" |
| Repurchase of $1.8 billion of existing 6.75% Senior Secured Notes due 2028 | Correct | `EX-99.1` (Earnings Release), "Financing Activity" |
| $943 million returned to shareholders in Q4 | Correct | `EX-99.1` (Earnings Release), "Share Repurchase Activity" |
| Repurchase of 820,000 shares at average price of $1,150 | Correct | `EX-99.1` (Earnings Release), "Share Repurchase Activity" |


# Overview

TransDigm Group Incorporated (NYSE: TDG) is a leading global designer, producer, and supplier of highly engineered aircraft components for commercial and defense aerospace markets. In the fiscal year ended September 30, 2026, the company reported net sales of $10,557,000,000 (`us-gaap:Revenues`), representing a 20% increase from the prior year. The company's business model relies on proprietary aerospace components with high cost-of-failure applications.

# Market Positioning and Growth Outlook

TransDigm maintains strong competitive positioning, evidenced by a fourth-quarter EBITDA As Defined margin of 53.0% (`EX-99.1`). Growth is supported by both organic expansion—which reached 14% in the fourth quarter—and strategic acquisitions, such as the $1.07 billion purchase of Prince & Izant (“P&I”) on September 28, 2026 (`EX-99.1`). While the company shows strong top-line performance, future outlook is subject to potential risks, including unexpected deceleration in aerospace end markets or margin compression resulting from integration costs.

# Valuation Insights

As of the latest reporting, the company's stock price is $1,218.85. Financial metrics reflect a high-valuation profile:
* **Operating Margin:** 45.57% (`us-gaap:OperatingIncomeLoss` / `us-gaap:Revenues`).
* **Free Cash Flow:** $1,913,000,000 (calculated as $2,187,000,000 in net cash from operations minus $274,000,000 in capital expenditures).
* **Capital Structure:** The company reports negative stockholders' equity of $10,000,000,000 (`us-gaap:StockholdersEquity`) against total liabilities of $37,921,000,000.
* **Liquidity:** A current ratio of 2.90 (calculated from $7,652,000,000 in current assets and $2,638,000,000 in current liabilities) indicates sufficient short-term liquidity despite the leveraged balance sheet.

# Future Developments and Strategic Recommendations

TransDigm continues to utilize debt-funded capital allocation strategies. Recent activities include:
* **Debt Refinancing:** Issuance of $3.0 billion in 6.75% Senior Secured Notes maturing in 2035 to repurchase $1.8 billion of existing 6.75% Senior Secured Notes due 2028 (`EX-99.1`).
* **Capital Return:** $943 million returned to shareholders in Q4 through the repurchase of 820,000 shares at an average price of $1,150 per share (`EX-99.1`).
* **Recommendation:** Monitor the impact of the $3 billion in new notes on future net income and cash flow, as debt service costs remain a primary risk to long-term solvency.

# Investment Recommendation

**Recommendation:** Hold.

The investment case for TransDigm is characterized by a conflict between robust operational efficiency and financial risk. While the company demonstrates exceptional profit margins and strong revenue growth, its capital structure is highly leveraged, evidenced by $10 billion in negative stockholders' equity. Investors are advised to weigh the high profitability and pricing power against the inherent risks associated with a debt-heavy balance sheet.

## Worksheet view
# TDG worksheet

Run: tdg-20261117T150004Z
Method: lab06/worksheet-method.md

## Spinoff facts
parent: not applicable; not applicable
distribution ratio: not applicable; not applicable
distribution dates: not applicable
debt raised and cash to parent: not applicable
parent liabilities and restrictions: not applicable
Form 4 purchases, code P only: not applicable

## Filing facts
after-tax earnings: $2,107,000,000; historic; 10-K 0001260221-26-000077; XBRL NetIncomeLoss, period 2026-09-30 [claim: annual_numbers.net_income]
capital expenditures: $274,000,000; historic; 10-K 0001260221-26-000077; XBRL PaymentsToAcquirePropertyPlantAndEquipment, period 2026-09-30 [claim: annual_numbers.capital_expenditures]
liabilities: $37,921,000,000; historic; 10-K 0001260221-26-000077; XBRL Liabilities, period 2026-09-30 [claim: annual_numbers.liabilities]
cash from operations: $2,187,000,000; historic; 10-K 0001260221-26-000077; XBRL NetCashProvidedByUsedInOperatingActivities, period 2026-09-30 [claim: annual_numbers.cash_from_operations]
depreciation and amortization: $445,000,000; historic; 10-K 0001260221-26-000077; XBRL DepreciationDepletionAndAmortization, period 2026-09-30 [claim: annual_numbers.depreciation_and_amortization]
diluted weighted-average shares: $57,600,000; historic; 10-K 0001260221-26-000077; XBRL WeightedAverageNumberOfDilutedSharesOutstanding, period 2026-09-30 [claim: annual_numbers.diluted_weighted_average_shares]

## Owner cash flow and value
owner cash flow for the reported period: $2,278,000,000 = $2,107,000,000 + $445,000,000 - $274,000,000 [computed: annual_numbers.net_income + depreciation - annual_numbers.capital_expenditures]
historical owner cash flow: not known
low case: $395.49 per share; 0% growth; 10% required return; 0% terminal growth [method: low_return=10%]
middle case: $601.59 per share; 3% growth for five years; 9% required return; 2% terminal growth [method: middle_return=9%]
price against low case: 208.19%
price: $1218.85 on 2026-11-09; LSEG Workspace TDG.N regular-close export; last close before the Nov. 10, 2026 pre-market release [price]

## Liquidity
median daily dollar volume: not known; purchase size: not determined; supply an official LSEG close-and-value-traded export with --market-file.

## Judgment
Based on the supplied worksheet facts, the valuation models show a middle value of 601.59 and a low value of 395.49, which are both below the provided price of 1218.85. However, the facts are not enough to support the cheapness story because liquidity is not provided and the owner cash flow of 2,278,000,000.0 is not reconciled against the high price. 

The next filing fact that would change the view is liquidity.

## Release view
view: less than price; middle case $601.59 against price $1218.85; Form 10 information statement, Combined Statements of Cash Flows
conviction: Medium; worksheet-method conviction rule.

## Not known
- median daily dollar volume
