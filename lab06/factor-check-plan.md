# Factor Check — Pre-Registered Plan

Status: selected Nov. 10, 2026 as the team's Week 4 owned feature. This is a factor check,
not a claim that the factors predict returns.

## Question

For completed U.S. corporate spinoffs found from EDGAR, do the five Chapter 3 factors in
`skills/spinoff-seeker/factors.json` sort candidates differently from an equal-weight screen with
no factors?

## Frozen rules before results

- Universe: U.S. corporate spinoffs with an EDGAR information statement that shows the parent,
  distribution date, and new-company ticker or identifier.
- Screen window: first official close after distribution through day 180.
- Factors: small relative to parent, weak first-week return, few analysts, insider purchases, and
  small absolute size. Each has weight 1 as saved in `factors.json`.
- Missing material facts: leave the company unranked. Do not impute a value.
- Prices: LSEG Workspace or WRDS daily regular closes only. Keep raw exports outside this
  repository and record vendor, ticker, and dates in the output.
- Outcome: total return from the first official close after distribution to day 180, with the
  price-series treatment stated. This first check does not establish causation.

## Output required

For each included company, save filing links, raw factor inputs, score, first-close date and
price, day-180 date and price, and missing-data notes. Report the number included, number left
unranked, average outcome by score group, and every deviation from this plan.

The initial factors are a hypothesis from Greenblatt (1997), Chapter 3, and Klarman (1991),
Chapter 10. They are not validated until this check is completed and reviewed.
