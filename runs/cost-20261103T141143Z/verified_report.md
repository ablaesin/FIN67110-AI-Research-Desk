COST — filings: 10-K 0000909832-26-000093; 10-Q 0000909832-26-000051; earnings release 8-K 0000909832-26-000084

## Code verifier marks
| Claim | Mark | Correction and source |
|---|---|---|
| revenue | Correct | — |
| operating income was | Correct | — |
| net income | Correct | — |

## Model semantic marks
| Claim / Metric | Reported Value | Source / Filing | Evaluation | Correction / Note |
|---|---|---|---|---|
| Total Revenue (FY 2026) | $303,154,000,000 | Form 10-K / Earnings Release | **Correct** | Matches `RevenueFromContractWithCustomerExcludingAssessedTax` and total revenue for 52 weeks ended August 30, 2026. |
| Prior Period Revenue (FY 2025) | $275,235,000,000 | Form 10-K / Earnings Release | **Correct** | Matches 52 weeks ended August 31, 2025 total revenue. |
| Net Sales (FY 2026) | $297.2 billion ($297,247,000,000) | Earnings Release / Form 10-K | **Correct** | Matches net sales for the fiscal year ended August 30, 2026. |
| Prior Period Net Sales (FY 2025) | $269.9 billion ($269,912,000,000) | Earnings Release / Form 10-K | **Correct** | Matches net sales for the fiscal year ended August 31, 2025. |
| Net Income (FY 2026) | $9,226,000,000 | Form 10-K / Earnings Release | **Correct** | Matches `NetIncomeLoss` for FY 2026. |
| Prior Period Net Income (FY 2025) | $8,099,000,000 | Earnings Release | **Correct** | Matches net income for the fiscal year ended August 31, 2025. |
| Operating Income (FY 2026) | $11,685,000,000 | Form 10-K / Earnings Release | **Correct** | Matches `OperatingIncomeLoss` for FY 2026. |
| Warehouse Count | 939 locations | Form 10-K / Earnings Release | **Correct** | Matches warehouse count as of August 30, 2026. |
| Digitally-enabled comparable sales growth | 20.9% | Earnings Release | **Correct** | Matches 52-week digitally-enabled comparable sales growth. |
| Operating Margin | 3.85% | Calculated (`OperatingIncomeLoss` / Revenue) | **Correct** | Matches calculated value ($11,685M / $303,154M ≈ 3.85%). |
| Peer Operating Margin (BJ's) | 3.81% | BJ's 10-K | **Correct** | Matches BJ's calculated operating margin ($816,604K / $21,457,274K ≈ 3.81%). |
| Peer Operating Margin (Walmart) | 4.18% | Walmart 10-K | **Correct** | Matches Walmart's calculated operating margin ($29,825M / $713,163M ≈ 4.18%). |
| Stock Price | $904.70 as of September 23, 2026 | Advisor / Price data | **Correct** | Matches saved price evidence date and value. |
| Operating Cash Flow | $15,817,000,000 | Form 10-K | **Wrong** | Filing shows Net Cash Provided by Operating Activities is **$15,825,000,000** for the 52 weeks ended August 30, 2026. |
| Capital Expenditures | $6,435,000,000 | Form 10-K | **Correct** | Matches Additions to property and equipment (`PaymentsToAcquirePropertyPlantAndEquipment`). |
| Free Cash Flow | $9,382,000,000 | Calculated ($15,817M - $6,435M) | **Wrong** | Based on the correct operating cash flow of $15,825M minus $6,435M, FCF is **$9,390,000,000** (note: code calculated free cash flow is $9,382,000,000 using $15,817M which appears to be a minor discrepancy in the base input, but verified filing figure is $15,825M). |
| Total Assets | $89,045,000,000 | Form 10-K | **Correct** | Matches `Assets` as of August 30, 2026. |
| Total Liabilities | $53,242,000,000 | Form 10-K | **Correct** | Matches `Liabilities` as of August 30, 2026. |
| Stockholders' Equity | $35,803,000,000 | Form 10-K | **Correct** | Matches `StockholdersEquity` as of August 30, 2026. |
| Current Ratio | 1.06 | Calculated (`AssetsCurrent` / `LiabilitiesCurrent`) | **Correct** | Matches calculated ratio ($46,582M / $43,952M ≈ 1.0598). |
| Current Assets | $46,582,000,000 | Form 10-K | **Correct** | Matches `AssetsCurrent` as of August 30, 2026. |
| Current Liabilities | $43,952,000,000 | Form 10-K | **Correct** | Matches `LiabilitiesCurrent` as of August 30, 2026. |


## Overview

Costco Wholesale Corporation operates membership warehouses and e-commerce sites, with 939 warehouses across various geographies, including the United States, Puerto Rico, Canada, Mexico, Japan, the United Kingdom, Korea, Australia, Taiwan, China, Spain, France, Sweden, Iceland, and New Zealand (`cost:warehouse`, latest 10-K / earnings release). The company generates revenue primarily through two main streams: selling high volumes of goods at low prices to members and collecting membership fees.

For the 52-week fiscal year ended August 30, 2026, Costco reported total revenue of $303,154,000,000 (`RevenueFromContractWithCustomerExcludingAssessedTax`, Form 10-K), representing a 10.14% year-over-year increase compared to $275,235,000,000 in the prior period ending August 31, 2025. Net sales for the fiscal year increased 10.1 percent to $297.2 billion from $269.9 billion in the prior year (earnings release). Net income for the fiscal year ended August 30, 2026, was $9,226,000,000 (`NetIncomeLoss`, Form 10-K), compared to $8,099,000,000 in the previous year (earnings release). Operating income for FY 2026 was reported at $11,685,000,000 (`OperatingIncomeLoss`, Form 10-K). Additionally, the fourth quarter of fiscal 2026 was positively impacted by a non-recurring benefit of $0.15 per diluted share from IEEPA tariff refunds received in the quarter, less partial reinvestment of those refunds in increased member values (earnings release).

## Market Positioning and Growth Outlook

Costco competes in the wholesale and retail membership warehouse industry. Its market position is supported by high member loyalty, a dominant global warehouse footprint of 939 locations (`cost:warehouse`, latest 10-K / earnings release), and robust comparable sales growth across U.S., Canada, and international segments, earning a Competitive Position score of 5 / 5. Top-line expansion is further underscored by a 20.9% increase in digitally-enabled comparable sales for the fiscal year (earnings release). 

Performance is heavily influenced by consumer and small business spending patterns, domestic and international economic conditions (including exchange rates and inflation or deflation), competition, rising operating costs such as employee wages and health-care costs, and geopolitical conditions like tariffs (earnings release). Costco's operating margin sits at 3.85% (Operating Income of $11,685,000,000 on Revenue of $303,154,000,000; `OperatingIncomeLoss` / `RevenueFromContractWithCustomerExcludingAssessedTax`), which is typical for the wholesale/retail peer group (e.g., BJ's at 3.81%, Walmart at 4.18%), reflecting thin margins inherent to the business model.

## Valuation Insights

Specific valuation multiples and a detailed P/E calculation are not provided in the source files. However, the supplied stock price is $904.70 as of September 23, 2026 (advisor). The valuation incorporates high expectations following robust fiscal year results, and Costco's valuation score is recorded as not provided / 5 due to the absence of specific valuation multiples in the sources (stock price: $904.70 on 2026-09-23; earnings period: FY 2026 ended August 30, 2026; filing line / XBRL tag: not provided). Slower earnings growth or margin compression from rising operational and wage costs could make the current share price less attractive.

## Future Developments and Strategic Recommendations

Potential upside catalysts include continued top-line expansion through digitally-enabled comparable sales and potential upside from member value reinvestments or tariff refund benefits. Key measures to monitor include comparable sales growth and membership renewal rates to determine whether top-line momentum remains structural or faces macro-driven deceleration. A major change in revenue growth or operating performance in the next filing—such as a sharp deceleration in comparable sales, margin compression driven by rising operational and wage costs, or a reversal in membership renewal rates—could alter the overall assessment. 

## Investment Recommendation

**Recommendation:** Hold (advisor)

**Main Reasons, Potential Benefits, and Risks:**
- **Main Reasons:** Consistent double-digit net sales growth, high member loyalty, dominant global warehouse expansion (939 locations; `cost:warehouse`, latest 10-K / earnings release), and superior free cash flow generation of $9,382,000,000, derived from operating cash flow of $15,817,000,000 (`NetCashProvidedByUsedInOperatingActivities`, Form 10-K) minus capital expenditures of $6,435,000,000 (`PaymentsToAcquirePropertyPlantAndEquipment`, financial).
- **Potential Benefits:** Continued top-line expansion through digitally-enabled comparable sales and potential upside from member value reinvestments or tariff refund benefits.
- **Risks:** Thin operating margins (3.85%), vulnerability to macroeconomic shifts, inflation, rising employee wages, and a demanding valuation at the $904.70 stock price level (advisor). Financial stability is supported by total assets of $89,045,000,000 versus total liabilities of $53,242,000,000, stockholders' equity of $35,803,000,000 (`StockholdersEquity`), and a current ratio of 1.06 based on current assets of $46,582,000,000 (`AssetsCurrent`) and current liabilities of $43,952,000,000 (`LiabilitiesCurrent`, financial).