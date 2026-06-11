from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.self_harness.io import read_json, read_jsonl
from tools.self_harness.models import TraceRecord


def load_traces(path: Path) -> list[TraceRecord]:
    raw = _load_raw(path)
    return [normalize_trace(item, index=i) for i, item in enumerate(raw)]


def normalize_trace(item: dict[str, Any], *, index: int) -> TraceRecord:
    verifier = str(item.get("verifier_result") or item.get("status") or "unknown").lower()
    if verifier not in {"pass", "fail", "unknown"}:
        verifier = "fail" if verifier in {"failed", "error"} else "unknown"
    split = str(item.get("split") or "held_in")
    if split not in {"held_in", "held_out"}:
        split = "held_in"
    trace_id = str(item.get("trace_id") or item.get("id") or f"trace-{index + 1}")
    terminal_cause = str(item.get("terminal_cause") or item.get("failure_reason") or "unknown")
    causal_status = str(item.get("causal_status") or "unattributed")
    agent_mechanism = str(item.get("agent_mechanism") or item.get("mechanism") or "unknown")
    return TraceRecord(
        trace_id=trace_id,
        cluster_id=str(item.get("cluster_id") or "unknown_cluster"),
        case_id=str(item.get("case_id") or trace_id),
        split=split,  # type: ignore[arg-type]
        harness_entrypoint=str(item.get("harness_entrypoint") or "unknown"),
        simulated_user_role=str(item.get("simulated_user_role") or item.get("user_role") or "unknown"),
        messages_or_actions=list(item.get("messages_or_actions") or item.get("messages") or []),
        agent_steps=list(item.get("agent_steps") or item.get("steps") or []),
        tool_calls=list(item.get("tool_calls") or []),
        observability_refs=list(item.get("observability_refs") or []),
        verifier_result=verifier,  # type: ignore[arg-type]
        terminal_cause=terminal_cause,
        causal_status=causal_status,
        agent_mechanism=agent_mechanism,
        scores=list(item.get("scores") or []),
        metadata=dict(item.get("metadata") or {}),
    )


def _load_raw(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return read_jsonl(path)
    payload = read_json(path)
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict) and isinstance(payload.get("traces"), list):
        return [dict(item) for item in payload["traces"]]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError(f"unsupported trace payload at {path}")

