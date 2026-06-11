# Simulation Design

Simulations must act like real end users, customers, contacts, operators, or owners of the harness. They are not evaluators.

## Required Steps

1. Infer audience from repo docs and product behavior.
2. Create ideal audience portraits.
3. Ask owner to confirm audience qualification before running simulations.
4. Create representative clusters across behavior axes.
5. Run held-in and held-out cases through the real harness.

## Behavior Axes

- role and buying/user intent
- patience
- trust
- domain knowledge
- emotional pressure
- adversarial pressure
- ambiguity tolerance
- memory dependency
- tool/workflow dependency
- escalation pattern

## Default Budget

- quick: 3 clusters, 3 cases each, max 6 turns
- standard: 6 clusters, 4 held-in and 2 held-out cases each, max 8 turns
- exploratory: 10+ clusters only with explicit cost/time cap

Always cap turns, wall time, retries, concurrency, total cost, and trace size.

