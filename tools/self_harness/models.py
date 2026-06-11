from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

ARTIFACT_DIR = Path(".self-harness")


@dataclass(frozen=True)
class HarnessIntent:
    purpose: str
    value: list[str]
    audiences: list[str]
    target_failures: list[str]
    entrypoints: list[str]
    editable_surfaces: list[str]
    confidence: float
    questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SimulationCluster:
    cluster_id: str
    purpose: str
    actor_type: str
    portrait: str
    behavior_axes: dict[str, str]
    case_count: int
    heldout: bool
    success_checks: list[str]
    failure_checks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TraceRecord:
    trace_id: str
    cluster_id: str
    case_id: str
    split: Literal["held_in", "held_out"]
    harness_entrypoint: str
    simulated_user_role: str
    messages_or_actions: list[dict[str, Any]]
    agent_steps: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    observability_refs: list[str]
    verifier_result: Literal["pass", "fail", "unknown"]
    terminal_cause: str
    causal_status: str
    agent_mechanism: str
    scores: list[dict[str, Any]]
    metadata: dict[str, Any]

    @property
    def signature(self) -> tuple[str, str, str]:
        return (self.terminal_cause, self.causal_status, self.agent_mechanism)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FailureCluster:
    failure_cluster_id: str
    terminal_cause: str
    causal_status: str
    agent_mechanism: str
    trace_ids: list[str]
    representative_trace_ids: list[str]
    support: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProposalBundle:
    proposal_id: str
    failure_cluster_id: str
    evidence_trace_ids: list[str]
    editable_surface: str
    proposed_change: str
    expected_effect: str
    regression_risk: str
    status: str = "proposed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REQUIRED_QUESTIONS = [
    "What is this harness intended for?",
    "What value should it deliver?",
    "What difficulties or failures should it solve?",
]

