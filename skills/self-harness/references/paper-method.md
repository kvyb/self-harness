# Paper Method

Source: [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498).

## Invariants

- Fixed model, evaluator, environment, tool budget, and task split during one optimization round.
- Held-in traces feed weakness mining.
- Held-out traces are hidden from proposer and used only for regression validation.
- Weakness Mining clusters failed traces by verifier-grounded signature:

```text
phi(trace) = (terminal_cause, causal_status, agent_mechanism)
```

- Harness Proposal creates diverse, minimal candidate edits tied to one failure mechanism and one declared editable surface.
- Before proposing, mark each cluster addressable only when a declared editable surface can plausibly change the failing mechanism without a broad rewrite.
- Proposal Validation accepts only non-regressive improvements:

```text
held_in_delta >= 0
held_out_delta >= 0
max(held_in_delta, held_out_delta) > 0
```

If stochastic, repeat and aggregate.

## Skill Adaptation

This skill does not mutate the target repo by default. Before owner approval, candidates are `proposed`. After code changes are applied and rerun, candidates can be `validated` only if the paper gate passes.
