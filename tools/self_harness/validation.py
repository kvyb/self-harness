from __future__ import annotations

from typing import Any


def validation_decision(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_held_in = int(baseline.get("held_in_passes", 0))
    baseline_held_out = int(baseline.get("held_out_passes", 0))
    candidate_held_in = int(candidate.get("held_in_passes", 0))
    candidate_held_out = int(candidate.get("held_out_passes", 0))
    held_in_delta = candidate_held_in - baseline_held_in
    held_out_delta = candidate_held_out - baseline_held_out
    validated = held_in_delta >= 0 and held_out_delta >= 0 and max(held_in_delta, held_out_delta) > 0
    return {
        "held_in_delta": held_in_delta,
        "held_out_delta": held_out_delta,
        "validated": validated,
        "rule": "held_in_delta >= 0 and held_out_delta >= 0 and max(delta) > 0",
    }

