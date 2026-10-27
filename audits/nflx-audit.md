# NFLX report audit — student marks required

Report audited: `runs/nflx-20261027T125640Z/report.md`  
Sources: [2025 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528026000034/nflx-20251231.htm); [Q3 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1065280/000106528026000291/nflx-20260930.htm); [Q3 2026 Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1065280/000106528026000290/ex991_q326.htm).

Audit completed against the named SEC filings. Marks use the course definitions: Correct, Wrong, Unsupported, Missing, or Not in filings.

Errors (Wrong + Unsupported): 0  
Missing: 0

| # | Claim | Report said | Filing says | Mark | Where |
|---|---|---|---|---|---|
| 1 | Total revenue, latest fiscal year | $45.183 billion | $45.183 billion | Correct | 2025 10-K income statement; XBRL `Revenues`, 2025-12-31 |
| 2 | Revenue growth versus prior year | 15.85% | ($45.183 billion ÷ $39.001 billion) − 1 = 15.85% | Correct | 2025 10-K income statement; XBRL `Revenues`, 2025 and 2024 |
| 3 | Operating income and operating margin | $13.327 billion; 29.49% | $13.327 billion; $13.327 billion ÷ $45.183 billion = 29.49% | Correct | 2025 10-K income statement; XBRL `OperatingIncomeLoss` and `Revenues` |
| 4 | Net income attributable to the company | $10.981 billion | $10.981 billion | Correct | 2025 10-K income statement; XBRL `NetIncomeLoss` |
| 5 | GAAP diluted EPS | $2.53 | $2.53 | Correct | 2025 10-K per-share data; XBRL `EarningsPerShareDiluted` |
| 6 | Return on average equity | 42.76% | $10.981 billion ÷ average of $26.615 billion and $24.744 billion = 42.76% | Correct | 2025 10-K balance sheet; XBRL `StockholdersEquity` |
| 7 | Debt to equity, including current debt | 54.34% | $14.463 billion ÷ $26.615 billion = 54.34% | Correct | 2025 10-K balance sheet; short- and long-term debt divided by equity |
| 8 | Free cash flow | $9.461 billion | $10.149 billion operating cash flow − $0.688 billion additions to property and equipment = $9.461 billion | Correct | 2025 10-K cash flow statement; XBRL cash-flow and capital-expenditure tags |
| 9 | Latest-quarter revenue | $12.874 billion | $12.874 billion | Correct | Q3 2026 Exhibit 99.1, summary results table |
| 10 | Latest-quarter revenue growth versus prior-year quarter | 11.8% | ($12.874 billion ÷ $11.510 billion) − 1 = 11.8% after rounding | Correct | Q3 2026 Exhibit 99.1, summary results table |
| 11 | Latest-quarter GAAP diluted EPS | $0.87 | $0.87 | Correct | Q3 2026 Exhibit 99.1, summary results table |
| — | Other stated quarterly and forecast figures | Q3 operating margin 34.6%; Q4 revenue $13.442 billion and margin 26.0%; 2026 revenue $51.1 billion and margin 31.5%; Q3 free cash flow $2.884 billion; 2026 free-cash-flow forecast $12.0 billion; repurchases 63.9 million shares for $4.8 billion; $22.3 billion authorization; $15.3 billion debt; $8.2 billion cash | The Exhibit 99.1 “Q3 Results and Forecast” and “Cash Flow and Capital Structure” sections state the same figures | Correct | Q3 2026 Exhibit 99.1 |
| — | Peer operating margins and P/E | DIS 18.59%; ROKU -0.12%; WMG 10.35%; P/E 27.15 | Each operating margin equals operating income ÷ revenue from that peer's latest annual SEC facts. $68.69 ÷ $2.53 = 27.15. | Correct | Saved `evidence.json`; peer company facts; supplied 2026-10-20 close |
| — | Five report parts present | All five present | Overview; Market Positioning and Growth Outlook; Valuation Insights; Future Developments and Strategic Recommendations; Investment Recommendation | Correct | Report headings |
| — | Recommendation names a stated number | Hold, provisional; operating margin 29.49% | The recommendation names the reported operating-margin figure and limits its claim | Correct | Investment Recommendation section |
