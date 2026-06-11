from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from self_harness.io import ArtifactError, read_json, read_jsonl
from self_harness.models import TraceRecord


def load_traces(path: Path) -> list[TraceRecord]:
    raw = _load_raw(path)
    return [normalize_trace(item, index=i) for i, item in enumerate(raw)]


def normalize_trace(item: dict[str, Any], *, index: int) -> TraceRecord:
    verifier = parse_verifier_result(item.get("verifier_result") or item.get("status") or "unknown")
    split = parse_split(item.get("split") or "held_in")
    trace_id = str(item.get("trace_id") or item.get("id") or f"trace-{index + 1}")
    terminal_cause = str(item.get("terminal_cause") or item.get("failure_reason") or "unknown")
    causal_status = str(item.get("causal_status") or "unattributed")
    agent_mechanism = str(item.get("agent_mechanism") or item.get("mechanism") or "unknown")
    if verifier == "fail" and "unknown" in {terminal_cause, causal_status, agent_mechanism}:
        raise ArtifactError(
            f"failed trace {trace_id} must include terminal_cause, causal_status, and agent_mechanism"
        )
    return TraceRecord(
        trace_id=trace_id,
        cluster_id=str(item.get("cluster_id") or "unknown_cluster"),
        case_id=str(item.get("case_id") or trace_id),
        split=split,
        harness_entrypoint=str(item.get("harness_entrypoint") or "unknown"),
        simulated_user_role=str(item.get("simulated_user_role") or item.get("user_role") or "unknown"),
        messages_or_actions=_list_field(item, "messages_or_actions", fallback="messages"),
        agent_steps=_list_field(item, "agent_steps", fallback="steps"),
        tool_calls=_list_field(item, "tool_calls"),
        observability_refs=_list_field(item, "observability_refs"),
        verifier_result=verifier,
        terminal_cause=terminal_cause,
        causal_status=causal_status,
        agent_mechanism=agent_mechanism,
        scores=_list_field(item, "scores"),
        metadata=_dict_field(item, "metadata"),
    )


def parse_split(value: object) -> Literal["held_in", "held_out"]:
    split = str(value).strip()
    if split not in {"held_in", "held_out"}:
        raise ArtifactError(f"invalid split `{split}`; expected held_in or held_out")
    return split  # type: ignore[return-value]


def parse_verifier_result(value: object) -> Literal["pass", "fail", "unknown"]:
    result = str(value).strip().lower()
    aliases = {"passed": "pass", "failed": "fail", "error": "fail"}
    result = aliases.get(result, result)
    if result not in {"pass", "fail", "unknown"}:
        raise ArtifactError(f"invalid verifier_result `{result}`; expected pass, fail, or unknown")
    return result  # type: ignore[return-value]


def _list_field(item: dict[str, Any], field: str, *, fallback: str | None = None) -> list[Any]:
    value = item.get(field)
    if value is None and fallback is not None:
        value = item.get(fallback)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ArtifactError(f"`{field}` must be a list")
    return value


def _dict_field(item: dict[str, Any], field: str) -> dict[str, Any]:
    value = item.get(field)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ArtifactError(f"`{field}` must be an object")
    return value


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
