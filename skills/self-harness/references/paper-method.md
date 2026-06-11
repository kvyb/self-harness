# Paper method

Source: [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498).

## What the paper is trying to prove

Agent behavior is shaped by both the base model and the harness around it. The harness is the non-parametric execution scaffold: prompts, tools, state and memory rules, runtime control, recovery policies, verifier hooks, and output protocols.

The paper asks whether a fixed model can help improve its own harness using evidence from its own failed runs. The model weights stay fixed. The evaluator stays fixed. What changes is the harness.

The important claim is not "write a better prompt." The paper's goal is an auditable loop where recurring trace failures become small executable harness changes, and those changes only survive if regression tests pass.

## Core objects

```text
M = fixed model
h_t = current harness at round t
D_in = held-in simulation or task split
D_ho = held-out simulation or task split
E = fixed evaluator or verifier
tau = execution trace
```

Running `M` under `h_t` on a case produces an output and a trace. The evaluator maps that run to an outcome such as pass, fail, or unknown. Since the model and evaluator stay fixed, accepted behavior changes can be attributed to the harness edit rather than model replacement or evaluator drift.

## Loop

One round:

1. Evaluate current harness on held-in and held-out splits.
2. Build an evidence bundle from held-in failures.
3. Ask the same model, in proposer role, for `K` diverse candidate harness edits.
4. Apply each candidate as a harness variant.
5. Rerun held-in and held-out splits with the same model, evaluator, tools, budget, and environment.
6. Accept only candidates that improve at least one split and regress neither.
7. Log accepted and rejected candidates in the harness lineage.

In this skill, owner approval is inserted before step 4 because the target repo belongs to a human owner. Before approval, proposals are reports and suggested diffs only.

## Weakness Mining

Weakness Mining converts failed traces into structured evidence. It should not summarize failures as anecdotes.

For every failed held-in trace, assign:

```text
terminal_cause = final verifier-level rejection
causal_status = how the agent behavior contributed to the rejection
agent_mechanism = reusable behavior pattern exposed by the trace
```

Then cluster by exact signature:

```text
phi(trace) = (terminal_cause, causal_status, agent_mechanism)
```

This matters because two traces can fail with the same terminal cause but require different harness edits. Example: both may time out, but one times out because the agent loops on failed commands, while another times out because the harness never tells the agent when to stop exploration and write an artifact.

The evidence bundle should include:

- failure cluster ID
- support count
- representative trace IDs
- terminal cause
- causal status
- agent mechanism
- relevant transcript/tool/log excerpts
- passing behaviors that should be preserved
- editable surfaces that could plausibly affect the mechanism
- non-addressability reason when no narrow harness surface fits

## Harness Proposal

The proposer gets structured evidence, not an unbounded dump of logs.

A valid proposal:

- targets one primary failure mechanism
- maps to one or more declared editable harness surfaces
- is materially distinct from other proposals
- is small enough to inspect
- preserves unrelated harness behavior
- predicts observable behavior change
- names regression risks
- includes a rerun plan

Do not force every failure into a proposal. Mark a cluster non-addressable when it looks like model capability, missing product policy, missing data, unstable infrastructure, or a one-off case.

Good proposal surfaces:

- system prompt or task prompt
- tool selection or tool schema
- memory read/write policy
- runtime guardrail or loop breaker
- retry and recovery middleware
- artifact or output protocol
- evaluator or trace capture hook
- routing and handoff policy

Bad proposals:

- broad rewrites
- generic "be better" instructions
- domain-specific special cases without a recurring trace mechanism
- changes that only make the judge easier
- edits that use held-out evidence

## Proposal Validation

Validation is the acceptance gate. A proposal is not validated because it sounds plausible.

Compare baseline and candidate:

```text
held_in_delta = P_in(candidate) - P_in(baseline)
held_out_delta = P_ho(candidate) - P_ho(baseline)
```

Accept only when:

```text
held_in_delta >= 0
held_out_delta >= 0
max(held_in_delta, held_out_delta) > 0
```

Reject when:

- held-in improves but held-out regresses
- held-out improves but held-in regresses
- neither split improves
- evaluator, model, tools, budget, or environment changed between baseline and candidate
- candidate results are inconclusive and the run was not repeated enough to resolve stochasticity

## Adaptation to product harnesses

The paper uses benchmark tasks. This skill uses live simulations of realistic users, contacts, operators, owners, or developers.

Mapping:

```text
benchmark task -> simulated user case
task split -> held-in or held-out simulation suite
verifier -> deterministic checker, product rubric, LLM judge, or human-reviewed trace rubric
execution trace -> transcript, tool calls, logs, state evidence, observability trace IDs
harness edit -> prompt, tool, memory, runtime, routing, verifier, or orchestration change
```

The same invariant holds: do not tune on held-out cases, and do not call a change validated without rerunning comparable simulations.

## Why this is required

Most harness work fails because owners patch the last embarrassing transcript. That creates prompt bloat and hidden regressions.

Self-Harness forces the improvement path to be evidence based:

- simulated users create repeatable pressure
- traces show what actually happened
- failure signatures group reusable mechanisms
- proposals stay tied to editable harness surfaces
- held-out validation catches overfitting
- lineage records stop the team from forgetting which patches failed
