---
name: self-harness
description: >
  Use when improving, evaluating, or stress-testing an agent harness. Guides the host agent to
  inspect the target repo, identify and confirm the real end-user audience, run live AI user/contact/operator
  simulations through the real harness, mine traces using the Self-Harness paper method, propose
  code changes, and validate owner-approved changes. Works across Claude Code, Codex, Hermes, and
  other coding agents.
---

# Self-Harness

Use this skill inside the target repo that owns the agent harness.

Self-Harness is a harness improvement workflow based on [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498). The paper treats the model as fixed and improves the non-parametric harness around it: prompts, tool policy, memory/state rules, runtime control, recovery behavior, verifier hooks, and other execution scaffolding.

This skill adapts that method for arbitrary product harnesses. The host agent studies the repo, creates simulated end users, runs those users through the real harness, mines trace failures, proposes narrow harness edits, and validates approved changes with held-in and held-out simulations.

Do not turn this into a standalone optimizer. Do not use a generic discovery script to decide what the harness is for. The host agent must reason from repo evidence and owner answers.

## End goal

Produce a trace-grounded improvement report and, if the owner approves, a validated harness change.

The run is successful when `.self-harness/report.md` can answer:

- what the harness is meant to do
- who the harness must serve
- which live simulation clusters were run
- which failures repeated across traces
- which failure mechanisms map to editable harness surfaces
- what code changes are proposed
- whether approved changes improved held-in or held-out behavior without regression

Before owner approval, the output is proposal-only. After owner approval, code changes may be applied and validated.

## Paper method

The paper loop has three stages:

1. Weakness Mining: run the current harness, collect execution traces, and cluster failed held-in traces by `phi(trace) = (terminal_cause, causal_status, agent_mechanism)`.
2. Harness Proposal: generate diverse, minimal candidate edits tied to one recurring failure mechanism and one declared editable surface.
3. Proposal Validation: evaluate candidate harnesses on held-in and held-out splits. Accept only if neither split regresses and at least one improves.

The invariants matter:

- model, evaluator, tools, budget, environment, and task split stay fixed within one validation round
- held-out cases stay hidden from proposal reasoning
- accepted changes alter the harness, not model weights
- every accepted/rejected proposal is logged so the harness lineage remains auditable

Read `references/paper-method.md` when you need the full operational interpretation.

## Run directory

Create all work products in the target repo under `.self-harness/`.

Common artifacts:

```text
.self-harness/
  intent.json
  audience-confirmation.md
  owner-confirmation.json
  simulation-suite.json
  held-in-suite.json
  held-out-suite.json
  traces.jsonl
  evidence-bundle.json
  proposals.md
  proposals.json
  validation.json
  lineage.jsonl
  report.md
```

## Required workflow

1. Inspect repo docs, code, tests, evals, routes, CLI commands, workers, env examples, observability config, and existing traces before asking questions.
2. Author `.self-harness/intent.json` from evidence. Include purpose, value, audiences, audience portraits, hard failures, entrypoints, observability sources, editable surfaces, confidence, and unresolved questions.
3. If the purpose, value, or hard cases are unclear, ask exactly:
   - What is this harness intended for?
   - What value should it deliver?
   - What difficulties or failures should it solve?
4. Create realistic audience portraits. Include role, hidden goal, context, pressure style, sophistication, patience, domain knowledge, ambiguity, memory dependency, tool dependency, and escalation behavior.
5. Write `.self-harness/audience-confirmation.md` and ask the owner to confirm or correct the audience qualification before running live simulations.
6. After owner confirmation, write `.self-harness/owner-confirmation.json`.
7. Build simulation clusters and split them into held-in and held-out cases.
8. Run live simulations through the real harness entrypoint when possible: API, CLI, browser, webhook, worker, local app, or existing eval runner.
9. Capture simulator turns, agent replies, tool calls, logs, state/memory evidence, retrieval evidence, trace IDs, verifier inputs, verifier outputs, and runtime failures.
10. Normalize traces to `.self-harness/traces.jsonl`.
11. Mine weakness clusters from failed held-in traces and write `.self-harness/evidence-bundle.json`.
12. Propose logical code changes in `.self-harness/proposals.md` and `.self-harness/proposals.json`.
13. If the owner accepts a proposal, apply the change, rerun comparable held-in and held-out simulations, write `.self-harness/validation.json`, and notify the owner with accept/reject verdict.

## Intent discovery rules

The host agent owns discovery. Use repo evidence first:

- README, docs, ADRs, product specs, user stories
- prompts, system messages, routing policies, tool definitions
- API routes, CLI commands, webhook handlers, workers, browser flows
- existing tests, evals, fixtures, golden transcripts, judge prompts
- observability config such as Langfuse, Braintrust, Phoenix, OpenTelemetry, local JSONL, or app logs
- issues, PR notes, comments, runbooks, launch checklists

If docs and code conflict, record the conflict in `intent.json` and ask the owner only for the parts that block simulation design.

Do not hardcode a domain. A sales agent, coding agent, dating agent, support agent, medical intake bot, voice workflow, browser automation harness, and internal operator tool should all use the same method.

## Simulation rules

Simulations are mandatory. Existing observability traces can supplement evidence, but they do not replace live end-user simulation.

The simulator is not the judge. The simulator acts like a real user/contact/operator and only sees its persona, goal, context, and allowed behavior. The judge sees the success rubric and trace evidence.

Create behavior clusters, not one generic test user. Vary:

- role and goal
- domain knowledge
- trust and skepticism
- patience
- emotional or business pressure
- ambiguity and missing information
- memory continuity needs
- tool or external state dependency
- adversarial pressure
- escalation or handoff pattern

Each case needs a hidden user intent, expected outcome, failure checks, max turns, wall-clock timeout, and trace capture plan. Use bounded cost, bounded retries, and bounded concurrency.

## Weakness mining rules

Mine failed held-in traces only. Do not use held-out failures to generate proposals.

For each failed trace, assign:

- `terminal_cause`: what the verifier or real outcome ultimately rejected
- `causal_status`: whether the agent behavior was direct, contributing, ambiguous, or non-causal
- `agent_mechanism`: the reusable behavior pattern exposed by the trace

Cluster by exact signature:

```text
phi(trace) = (terminal_cause, causal_status, agent_mechanism)
```

The point is to avoid anecdote chasing. A useful cluster is not "this one user was unhappy." A useful cluster is "under low-trust, high-knowledge users, the agent gives unsupported commitments after tool failure, causing verifier failure on state evidence."

## Proposal rules

A proposal must be narrow, evidence-tied, and addressable.

Each proposal must name:

- target failure cluster
- representative trace IDs
- editable surface
- exact code or prompt surface to change
- expected behavior change
- regression risk
- validation plan
- held-in and held-out splits to rerun

Reject or mark non-addressable when the failure looks like model capability, missing product decision, missing data, unstable external dependency, or a one-off task rather than a harness mechanism.

Avoid generic prompt bloat. The paper's useful edits were concrete harness changes such as artifact-first workflow rules, schema-aware tool handling, loop breaking, retry discipline, persistent runtime state, and recovery middleware. Use that standard: a proposed edit should change observable execution behavior.

## Validation rules

Before validation, freeze:

- model and model settings
- evaluator or judge prompt
- tool set and tool versions
- budget, timeout, retry, and concurrency limits
- environment and seed when available
- held-in and held-out case definitions

Compare baseline harness and candidate harness:

```text
held_in_delta >= 0
held_out_delta >= 0
max(held_in_delta, held_out_delta) > 0
```

If any split regresses, reject. If neither split improves, reject. If results are stochastic, repeat with the same protocol and aggregate before deciding.

Never call a proposal validated before rerunning the candidate harness.

## Helper tools

If this repo is available locally, helper tools can scaffold artifacts:

```bash
python3 /path/to/self-harness/tools/self_harness/cli.py init
# host agent inspects the repo and writes .self-harness/intent.json
python3 /path/to/self-harness/tools/self_harness/cli.py confirm-audience --by owner
python3 /path/to/self-harness/tools/self_harness/cli.py create-sim-clusters
python3 /path/to/self-harness/tools/self_harness/cli.py cluster-failures
python3 /path/to/self-harness/tools/self_harness/cli.py propose-harness-edits
```

Scripts may scaffold templates, normalize traces, cluster evidence, and record validation. They do not replace repo understanding.

## References

- `references/paper-method.md`: operational reading of the paper.
- `references/simulation-design.md`: how to create realistic user clusters.
- `references/contracts.md`: artifact schemas.
- `references/proposal-validation.md`: validation and owner approval rules.
- `references/connector-adapters.md`: trace-store adapters.
