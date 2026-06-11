# Connector Adapters

Trace stores are inputs, not the core method. Every connector must normalize into `TraceRecord`.

## Supported v1 Paths

- local JSONL: preferred portable artifact
- local JSON or CSV: accepted when fields can be mapped
- Langfuse: use existing repo credentials/config if present
- Braintrust, Phoenix, OpenTelemetry: treat as adapter targets; export then normalize

## Rules

- Do not make core logic depend on provider SDK objects.
- Record trace URLs/IDs in `observability_refs`.
- If traces lack verifier outcome, use them only as supplementary evidence until simulations produce pass/fail or judge results.
- Never read secrets directly into reports. Store only presence, provider name, and redacted refs.

