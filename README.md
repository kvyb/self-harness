# Self-Harness Skill

Self-Harness is a portable agent skill for improving agent harnesses with live simulated users and trace-grounded proposals.

Invoke it inside any repo with Claude Code, Codex, Hermes, or another coding agent. The host agent, not a hardcoded discovery script, inspects the harness, identifies who it serves, confirms that audience with the owner, runs representative AI end users through the real harness, mines the traces, and proposes concrete code changes.

The workflow is based on the paper [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498). It applies the paper's loop to real product harnesses: **Weakness Mining -> Harness Proposal -> Proposal Validation**.

## What It Solves

Agent harness owners usually know the symptom: the agent feels brittle, generic, forgetful, overconfident, slow, or bad under real user pressure. The hard part is proving why.

Self-Harness gives you a repeatable way to:

- reason from the repo about what the harness is supposed to do
- identify the real users, customers, contacts, or operators it must serve
- simulate those users live against the real harness
- collect logs, traces, transcripts, tool calls, and state evidence
- cluster failures by reusable mechanisms, not anecdotes
- propose narrow harness changes tied to trace evidence
- rerun similar held-in and held-out simulations after owner-approved changes

All run artifacts stay inside the target repo under `.self-harness/`.

## How It Works

1. **Explore the repo**: the host agent reads docs, code, tests, routes, scripts, env examples, observability config, and existing evals, then writes `.self-harness/intent.json` from evidence.
2. **Confirm the audience**: propose evidence-backed user/customer/contact/operator profiles, then ask the owner to confirm or correct them before simulations.
3. **Create simulation clusters**: build representative AI users across goals, patience, trust, domain knowledge, ambiguity, memory pressure, tool pressure, and escalation patterns.
4. **Run live simulations**: drive the real harness through API, CLI, browser, webhook, worker, local app, or existing eval entrypoints.
5. **Mine weaknesses**: cluster failed traces by `phi(trace) = (terminal_cause, causal_status, agent_mechanism)`.
6. **Propose changes**: recommend minimal prompt, tool, runtime, memory, routing, or evaluator changes tied to one failure cluster and one declared surface.
7. **Validate if approved**: after owner approval, apply the change and rerun held-in and held-out simulations. Mark a change validated only if it improves at least one split and regresses neither.

## Quick Use

From a target harness repo:

```bash
# with this repo cloned somewhere locally
python3 /path/to/self-harness/tools/self_harness/cli.py init
# host agent now inspects repo and writes .self-harness/intent.json
# after owner confirms .self-harness/audience-confirmation.md
python3 /path/to/self-harness/tools/self_harness/cli.py confirm-audience --by owner
python3 /path/to/self-harness/tools/self_harness/cli.py create-sim-clusters
```

Or invoke the skill from your agent:

```text
Use $self-harness to evaluate this agent harness with live simulated users and propose improvements.
```

The agent should then create or update:

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

## Repository Description

Portable agent skill for improving agent harnesses with live simulated users, trace mining, and Self-Harness proposal validation.
