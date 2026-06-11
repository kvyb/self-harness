from __future__ import annotations

from tools.self_harness.models import HarnessIntent, SimulationCluster


def create_clusters(intent: HarnessIntent, *, mode: str = "standard") -> list[SimulationCluster]:
    case_count = {"quick": 3, "standard": 6, "exploratory": 10}.get(mode, 6)
    audiences = intent.audiences or ["end user"]
    clusters: list[SimulationCluster] = []
    patterns = [
        ("skeptical", "low", "high", "medium", "challenge vague or generic behavior"),
        ("impatient", "very_low", "medium", "high", "force quick correct action"),
        ("ambiguous", "medium", "low", "low", "withhold key facts and reveal gradually"),
        ("high_value", "medium", "high", "high", "test premium or business-critical path"),
        ("memory_dependent", "high", "medium", "medium", "require continuity across turns"),
        ("tool_dependent", "medium", "medium", "high", "require correct external action or state change"),
    ]
    for idx, pattern in enumerate(patterns[:case_count]):
        audience = audiences[idx % len(audiences)]
        name, patience, trust, knowledge, purpose = pattern
        heldout = idx % 3 == 2
        clusters.append(
            SimulationCluster(
                cluster_id=f"{name}_{audience.replace(' ', '_')}",
                purpose=purpose,
                actor_type=_actor_type(audience),
                portrait=f"{name.replace('_', ' ')} {audience} using the harness for: {intent.purpose}",
                behavior_axes={
                    "patience": patience,
                    "trust": trust,
                    "domain_knowledge": knowledge,
                    "ambiguity": "high" if name == "ambiguous" else "medium",
                    "memory_dependency": "high" if name == "memory_dependent" else "medium",
                    "tool_dependency": "high" if name == "tool_dependent" else "medium",
                },
                case_count=4 if not heldout else 2,
                heldout=heldout,
                success_checks=[
                    "agent produces outcome aligned with harness value",
                    "agent handles user pressure without generic fallback",
                    "required state, tool, or handoff evidence is present",
                ],
                failure_checks=[
                    "agent invents facts or capabilities",
                    "agent ignores user goal or hidden constraint",
                    "agent completes conversation but fails downstream state",
                ],
            )
        )
    return clusters


def _actor_type(audience: str) -> str:
    lowered = audience.lower()
    if "lead" in lowered or "customer" in lowered:
        return "customer"
    if "operator" in lowered:
        return "operator"
    if "developer" in lowered:
        return "developer"
    return "end_user"

