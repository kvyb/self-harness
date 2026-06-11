from __future__ import annotations

from typing import Any


def validation_decision(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if _config_key(baseline) != _config_key(candidate):
        return _rejected("baseline and candidate validation configs differ")
    baseline_in = _split(baseline, "held_in")
    baseline_out = _split(baseline, "held_out")
    candidate_in = _split(candidate, "held_in")
    candidate_out = _split(candidate, "held_out")
    if baseline_in["total"] != candidate_in["total"] or baseline_out["total"] != candidate_out["total"]:
        return _rejected("baseline and candidate split totals differ")
    if any(split["unknown"] for split in (baseline_in, baseline_out, candidate_in, candidate_out)):
        return _rejected("validation cannot accept runs with unknown outcomes")
    baseline_held_in = baseline_in["pass"]
    baseline_held_out = baseline_out["pass"]
    candidate_held_in = candidate_in["pass"]
    candidate_held_out = candidate_out["pass"]
    held_in_delta = candidate_held_in - baseline_held_in
    held_out_delta = candidate_held_out - baseline_held_out
    validated = held_in_delta >= 0 and held_out_delta >= 0 and max(held_in_delta, held_out_delta) > 0
    return {
        "held_in_delta": held_in_delta,
        "held_out_delta": held_out_delta,
        "validated": validated,
        "reason": "paper non-regression gate passed" if validated else "paper non-regression gate failed",
        "rule": "held_in_delta >= 0 and held_out_delta >= 0 and max(delta) > 0",
    }


def _config_key(run: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    return (
        str(run.get("suite_id", "")),
        str(run.get("mode", "")),
        str(run.get("proposer", "")),
        str(run.get("model", "")),
        str(run.get("evaluator", "")),
        str(run.get("environment", "")),
    )


def _split(run: dict[str, Any], name: str) -> dict[str, int]:
    value = run.get(name)
    if not isinstance(value, dict):
        legacy_passes = run.get(f"{name}_passes")
        if legacy_passes is not None:
            passed = int(legacy_passes)
            return {"total": passed, "pass": passed, "fail": 0, "unknown": 0}
        raise ValueError(f"missing validation split: {name}")
    return {
        "total": int(value["total"]),
        "pass": int(value["pass"]),
        "fail": int(value["fail"]),
        "unknown": int(value["unknown"]),
    }


def _rejected(reason: str) -> dict[str, Any]:
    return {
        "held_in_delta": 0,
        "held_out_delta": 0,
        "validated": False,
        "reason": reason,
        "rule": "held_in_delta >= 0 and held_out_delta >= 0 and max(delta) > 0",
    }
