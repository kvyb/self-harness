# Canonical Contracts

Artifacts live in the target repo under `.self-harness/`.

## HarnessIntent

```json
{
  "purpose": "string",
  "value": ["string"],
  "audiences": ["string"],
  "audience_portraits": [
    {
      "name": "string",
      "audience": "string",
      "hidden_goal": "string",
      "pressure": "string"
    }
  ],
  "target_failures": ["string"],
  "entrypoints": ["string"],
  "editable_surfaces": ["string"],
  "confidence": 0.0,
  "questions": ["string"]
}
```

## SimulationCluster

```json
{
  "cluster_id": "string",
  "purpose": "string",
  "actor_type": "end_user|customer|contact|operator|owner|developer",
  "portrait": "string",
  "behavior_axes": {},
  "case_count": 0,
  "heldout": false,
  "success_checks": [],
  "failure_checks": []
}
```

## SimulationCase

```json
{
  "case_id": "string",
  "split": "held_in|held_out",
  "cluster_id": "string",
  "entrypoint": "api|cli|browser|webhook|worker|eval_runner",
  "run_command_or_url": "string",
  "simulator_prompt": "string",
  "max_turns": 8,
  "timeout_seconds": 600,
  "verifier": {"type": "deterministic|llm_judge", "config_ref": "string"},
  "trace_capture": ["transcript", "tool_calls", "logs", "state_refs"]
}
```

## TraceRecord

```json
{
  "trace_id": "string",
  "cluster_id": "string",
  "case_id": "string",
  "split": "held_in|held_out",
  "harness_entrypoint": "string",
  "simulated_user_role": "string",
  "messages_or_actions": [],
  "agent_steps": [],
  "tool_calls": [],
  "observability_refs": [],
  "verifier_result": "pass|fail|unknown",
  "terminal_cause": "string",
  "causal_status": "string",
  "agent_mechanism": "string",
  "scores": [],
  "metadata": {}
}
```

## ProposalBundle

```json
{
  "proposal_id": "string",
  "failure_cluster_id": "string",
  "evidence_trace_ids": [],
  "editable_surface": "string",
  "proposed_change": "string",
  "expected_effect": "string",
  "regression_risk": "string",
  "target_files": [],
  "exact_amendments": [],
  "unified_diff": "optional string",
  "addressability_reason": "string",
  "validation_plan": [],
  "predicted_delta": {"held_in": 0, "held_out": 0},
  "status": "proposed|implemented|validated|rejected|not_validated"
}
```
