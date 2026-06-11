---
name: self-harness
description: >
  Use when improving, evaluating, or stress-testing an agent harness. Guides the host agent to
  inspect the target repo, reason from evidence to identify and confirm end-user audience, run live AI user/contact/operator
  simulations through the real harness, mine traces using the Self-Harness paper method, propose
  code changes, and validate owner-approved changes. Works across Claude Code, Codex, Hermes, and
  other coding agents.
---

# Self-Harness

Apply the method from [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498) inside the current target repo.

This is a skill workflow, not a standalone optimizer app. Create all run artifacts and helper scripts inside the target repo's `.self-harness/` directory. Do not edit target harness code until the owner explicitly accepts a proposal.

## Required Loop

Follow the paper loop exactly:

1. **Weakness Mining**: run the current harness, collect traces, and cluster failed held-in traces by `phi(trace) = (terminal_cause, causal_status, agent_mechanism)`.
2. **Harness Proposal**: propose diverse, minimal edits tied to one failure mechanism and one declared editable surface.
3. **Proposal Validation**: after owner approval, rerun held-in and held-out simulations. Mark validated only if neither split regresses and at least one split improves.

## Workflow

1. Inspect repo docs/code/tests/evals/routes/CLI/env examples before asking questions.
2. As the host agent, reason from repo evidence and author `.self-harness/intent.json`: purpose, audience, value, hard failures, entrypoints, observability, editable surfaces. Do not rely on a generic discovery script to decide this.
3. If intent is unclear, ask exactly:
   - What is this harness intended for?
   - What value should it deliver?
   - What difficulties or failures should it solve?
4. Create ideal customer/user/contact/operator portraits and representative simulation clusters.
5. Write `.self-harness/audience-confirmation.md` and ask the owner to confirm audience qualification.
6. After owner confirmation, write `.self-harness/owner-confirmation.json`.
7. Build `.self-harness/simulation-suite.json`, `.self-harness/held-in-suite.json`, and `.self-harness/held-out-suite.json`.
8. Run live simulations through the real harness when possible: API, CLI, browser, webhook, worker, local app, or existing eval runner.
9. Capture transcripts, logs, tool calls, retrieval/memory evidence, state snapshots, trace IDs, verifier/judge results.
10. Normalize traces to `.self-harness/traces.jsonl`.
11. Mine weakness clusters and write `.self-harness/evidence-bundle.json`.
12. Propose logical code changes in `.self-harness/proposals.md` and `.self-harness/proposals.json`.
13. If owner accepts, apply code changes, rerun similar held-in and held-out simulations, write `.self-harness/validation.json`, and notify owner with verdict.

## Critical Rules

- Simulations are mandatory. Observability traces supplement them; they do not replace live end-user simulation.
- Audience confirmation is mandatory before expensive live simulations. If the agent-authored user portraits are wrong, stop and correct portraits first.
- Simulator and judge must be separate. Simulator acts like a real user/contact/operator and does not see judge rubric.
- Held-out cases must not enter proposal context.
- Keep model, evaluator, tools, budget, and environment fixed between baseline and candidate validation.
- Never claim a proposal is validated before rerunning candidate harness.
- Prefer deterministic verifiers. If using LLM-as-judge, freeze prompt/model/config and record them.
- Do not create generic prompt bloat. Every proposal needs trace evidence, target mechanism, edited surface, expected behavior, and regression risk.
- Discovery is agent reasoning work. Scripts may scaffold templates and validate artifacts, but they must not replace repo-specific understanding.

## Helper Tools

If this repo is available locally, helper tools can scaffold artifacts:

```bash
python3 /path/to/self-harness/tools/self_harness/cli.py init
# host agent inspects the repo and writes .self-harness/intent.json
python3 /path/to/self-harness/tools/self_harness/cli.py confirm-audience --by owner
python3 /path/to/self-harness/tools/self_harness/cli.py create-sim-clusters
python3 /path/to/self-harness/tools/self_harness/cli.py cluster-failures
python3 /path/to/self-harness/tools/self_harness/cli.py propose-harness-edits
```

Read references when needed:

- `references/paper-method.md`: exact method constraints from the paper.
- `references/simulation-design.md`: how to create realistic user clusters.
- `references/contracts.md`: canonical artifact schemas.
- `references/proposal-validation.md`: validation semantics and owner approval.
- `references/connector-adapters.md`: how to use Langfuse, local JSONL, and other trace stores.
