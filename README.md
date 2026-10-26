# AI Lead Qualification & Scoring Pipeline

Turns a raw CRM/CSV export into ranked, explainable hot/warm/cold leads.

![tests](https://img.shields.io/badge/tests-unittest-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue)

## Architecture

```
CSV -> parse/validate -> dedupe (last row wins) -> features -> weighted score (0-100)
                                                            |-> notes qualifier (heuristic | Claude), clamped to +/-10
                                                            -> tier + reasons -> ranked CSV
```

## Quick start

```bash
# no required dependencies (standard library only)
PYTHONPATH=src python -m leadscore.cli data/sample_leads.csv out.csv        # add --llm to use Claude on notes
PYTHONPATH=src python -m unittest discover -s tests -v
```

Example output:

```
email,score,tier,reasons
priya@acmelogistics.com,91,hot,"notes adjustment +8 ... | requested a demo (+20) | buying window <= 30 days"
dana@midco.io,40,warm,notes adjustment +4: positive=['pilot']
lee@tiny.co,21,cold,
tom@gmail.com,0,cold,"free email domain (-10) | missing company (-5) | notes adjustment -10 ..."
```

## Key design decisions

- Deterministic score is the backbone; the LLM only reads free-text notes and can move the score by at most +/-10. A hallucination or a prompt injection inside `notes` therefore cannot flip a cold lead to hot.
- Every point is traceable: `breakdown` (per-feature) and `reasons` (human-readable) are returned with each score, so sales can dispute a ranking.
- Intent signals are capped (page views at 10, opens at 5) so refresh loops and bots do not dominate.
- Bad rows are collected in `report.rejected` with row numbers instead of crashing the batch.
- The Claude path falls back to the heuristic on any exception (no key, SDK missing, bad JSON, outage).

## Limitations (read before using)

- Weights and the hot/warm thresholds (70/35) are hand-set heuristics, NOT fitted to conversion data. Treat the tiers as a prioritisation aid until you calibrate against closed-won/lost outcomes.
- The Claude qualifier needs an API key and is not covered by unit tests (tests assert the fallback path).
- No CRM integration; input/output are CSV.

## Next steps

- Fit weights with logistic regression once you have >=500 labelled outcomes; compare AUC to the hand-set score.
- Add a /score FastAPI endpoint and a webhook for CRM pushes.
- Log model adjustments and audit them against actual outcomes.

See [docs/DESIGN.md](docs/DESIGN.md) for the module map and test strategy.
