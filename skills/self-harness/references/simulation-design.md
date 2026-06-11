# Simulation design

Simulations are the product adaptation of the paper's task split. They create repeatable pressure against the real harness so failures become trace evidence instead of opinions.

## Required stages

1. Read the repo and owner answers.
2. Write audience portraits.
3. Ask owner to confirm audience qualification.
4. Build behavior clusters from confirmed portraits.
5. Split into held-in and held-out cases.
6. Run live cases through real harness entrypoints.
7. Capture traces and verifier outcomes.

Do not skip stage 3. Wrong audience means wrong failures.

## Audience portraits

Each portrait should include:

- role or relationship to the harness
- context before the first turn
- hidden goal
- what value the user wants
- what the user knows
- what the user does not know
- patience level
- trust level
- domain expertise
- likely escalation behavior
- what success looks like from the user's side

Portraits should be specific enough for a simulator to act naturally but generic enough to avoid overfitting to one scripted transcript.

## Behavior clusters

Build clusters that vary pressure. Good default axes:

- role and goal
- sophistication
- patience
- trust
- ambiguity
- emotional or business pressure
- adversarial pressure
- memory dependency
- tool dependency
- context length
- escalation pattern

Examples of generic clusters:

- skeptical high-knowledge user
- impatient low-context user
- ambiguous user who reveals facts slowly
- high-value user with strict success criteria
- memory-dependent returning user
- tool-dependent user who needs real state change
- adversarial user testing policy boundaries
- escalation-seeking user who wants a handoff

The labels are generic. The content must come from the target repo and confirmed audience.

## Case contract

Every simulation case needs:

- case ID
- held-in or held-out split
- cluster ID
- target harness entrypoint
- run command, URL, webhook, or manual instruction
- simulator prompt
- hidden intent
- success checks
- failure checks
- max turns
- timeout
- trace capture plan
- verifier or judge config

The simulator prompt must say that the simulator is a user/contact/operator, not an evaluator. It must not reveal the rubric or tell the simulator it is helping improve a harness.

## Live execution

Prefer real entrypoints:

- API route
- CLI command
- browser flow
- webhook receiver
- background worker
- local app
- existing eval runner

If automation is impossible, write the exact manual command and required capture steps. Do not silently replace live simulation with static analysis.

## Held-in and held-out

Held-in cases feed Weakness Mining and proposal generation.

Held-out cases are regression tests. Do not inspect held-out failures while writing proposals. Use them only after an approved candidate change is applied.

Keep split definitions stable between baseline and candidate runs.

## Budgets

Defaults:

- quick: 3 clusters, 3 cases each, max 6 turns
- standard: 6 clusters, 4 held-in and 2 held-out cases each, max 8 turns
- exploratory: 10 or more clusters only with explicit owner-approved cost and time cap

Always cap:

- turns
- wall-clock time
- retries
- concurrency
- total cost
- trace size

## Trace capture

Capture enough evidence to diagnose behavior:

- simulated user messages or actions
- agent messages
- tool calls and results
- retrieval or memory evidence
- state changes
- logs and runtime events
- observability trace IDs
- verifier inputs
- verifier outputs
- final pass, fail, or unknown result

If using Langfuse, Braintrust, Phoenix, OpenTelemetry, or another trace store, normalize links and IDs into `observability_refs`. Keep local canonical traces in `.self-harness/traces.jsonl`.
