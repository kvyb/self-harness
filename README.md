# Self-Harness

Self-Harness is a portable skill for improving agent harnesses with live simulated users.

Use it inside the repo you want to test. Codex, Claude Code, Hermes, or another host agent reads the codebase, figures out what the harness is for, asks you to confirm the target audience, runs realistic AI users through the real harness, mines the traces, and proposes code changes.

It is not a standalone optimizer app. It does not train a model. The skill guides the host agent; helper scripts only keep the `.self-harness/` artifacts tidy.

Based on [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498), using the paper loop:

```text
Weakness Mining -> Harness Proposal -> Proposal Validation
```

## Why this exists

Agent harnesses usually fail in messy situations: vague users, impatient users, skeptical buyers, missing context, tool mistakes, memory gaps, bad handoffs, weak recovery after an error.

Most teams notice these failures one at a time. Self-Harness turns them into a repeatable loop:

- simulate representative end users against the real harness
- capture transcripts, tool calls, logs, traces, and judge results
- cluster failures by `phi(trace) = (terminal_cause, causal_status, agent_mechanism)`
- propose small prompt, tool, runtime, memory, routing, or eval changes
- validate approved changes on held-in and held-out simulations

## How to use it

Invoke the skill from inside a target harness repo:

```text
Use $self-harness to evaluate this agent harness with live simulated users and propose improvements.
```

The host agent should inspect the repo itself. No generic Python script decides what the harness is for.

If you want to use the helper scripts directly:

```bash
/path/to/self-harness/bin/self-harness init
# host agent inspects the repo and writes .self-harness/intent.json
# owner confirms .self-harness/audience-confirmation.md
/path/to/self-harness/bin/self-harness confirm-audience --by owner
/path/to/self-harness/bin/self-harness create-sim-clusters
```

## What happens in the target repo

Self-Harness writes run artifacts under `.self-harness/`:

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

The skill should not edit the target harness until the owner accepts a proposal. After approval, the host agent applies the change and reruns comparable held-in and held-out simulations. A proposal counts as validated only if no split regresses and at least one improves.

## Repository description

Portable skill for improving agent harnesses with live simulated users, trace mining, and Self-Harness proposal validation.
