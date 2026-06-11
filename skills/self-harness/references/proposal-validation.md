# Proposal Validation

Default state is propose-only. Owner approval is required before editing target harness code.

## Status Terms

- `proposed`: trace-grounded recommendation, no code changed.
- `implemented`: owner accepted and code was changed.
- `validated`: held-in/held-out rerun passed the paper non-regression gate.
- `not_validated`: code changed, but rerun failed or was inconclusive.
- `rejected`: owner declined or proposal was superseded.

## Validation Rule

Compare baseline harness and candidate harness with fixed model, evaluator, tools, budget, and environment.

```text
held_in_delta >= 0
held_out_delta >= 0
max(held_in_delta, held_out_delta) > 0
```

If the evaluator is stochastic, repeat and aggregate. Record all runs in `.self-harness/lineage.jsonl`.

