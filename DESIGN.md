# Design notes: AI Lead Qualification & Scoring Pipeline

## Module map (`src/leadscore/`)

- `cli.py`
- `features.py`
- `llm.py`
- `models.py`
- `pipeline.py`
- `scoring.py`

## Test strategy

- Tests use only `unittest` (run with `python -m unittest` or `pytest`). Each test asserts a behaviour, with known-answer cases where a closed form exists, not just that code runs.
- Paths that need external services (LLM API, webcam) are isolated behind small interfaces and are NOT covered by the unit tests; each README says so.

## Failure modes considered

- Deterministic score is the backbone; the LLM only reads free-text notes and can move the score by at most +/-10. A hallucination or a prompt injection inside `notes` therefore cannot flip a cold lead to hot.
- Every point is traceable: `breakdown` (per-feature) and `reasons` (human-readable) are returned with each score, so sales can dispute a ranking.
- Intent signals are capped (page views at 10, opens at 5) so refresh loops and bots do not dominate.

## Known gaps

- Weights and the hot/warm thresholds (70/35) are hand-set heuristics, NOT fitted to conversion data. Treat the tiers as a prioritisation aid until you calibrate against closed-won/lost outcomes.
- The Claude qualifier needs an API key and is not covered by unit tests (tests assert the fallback path).
- No CRM integration; input/output are CSV.
