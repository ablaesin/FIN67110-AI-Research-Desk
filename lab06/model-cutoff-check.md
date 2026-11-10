# Model Cutoff Check — TDG Live Release

Date performed: Nov. 10, 2026

## Fresh no-tool prompt

Model: `gemini-flash-lite-latest`.

Prompt:

> Without using search, browsing, files, or other tools, answer only from your training: What net
> sales did TransDigm Group report for fiscal year 2026 in its earnings release dated November 10,
> 2026? If you do not know, say "I do not know."

Response:

> I do not know.

## Interpretation

The question refers to a release filed on Nov. 10, 2026. The response did not supply the number.
This is consistent with the model not having that release in its training, but it does not prove a
specific knowledge cutoff.

Google's Gemini API model list identifies the model family but does not state a training-data
cutoff on the consulted page. Record the provider result as **not disclosed**, not as a date.

- Provider page consulted: <https://ai.google.dev/gemini-api/docs/models>
- Release checked: TransDigm 8-K, accession `0001260221-26-000073`, Exhibit 99.1,
  <https://www.sec.gov/Archives/edgar/data/1260221/000126022126000073/tdg-20261110.htm>

This test used no tools in the model request. The release itself was not supplied to the model.
