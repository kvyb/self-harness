from __future__ import annotations

from self_harness.models import HarnessIntent, SimulationCase, SimulationCluster


def create_suite(intent: HarnessIntent, *, mode: str = "standard") -> dict[str, object]:
    clusters = create_clusters(intent, mode=mode)
    cases = create_cases(intent, clusters)
    return {
        "mode": mode,
        "requires_owner_confirmation": True,
        "clusters": [cluster.to_dict() for cluster in clusters],
        "cases": [case.to_dict() for case in cases],
    }


def create_clusters(intent: HarnessIntent, *, mode: str = "standard") -> list[SimulationCluster]:
    case_count = {"quick": 3, "standard": 6, "exploratory": 10}.get(mode, 6)
    portraits = intent.audience_portraits or [
        {
            "name": audience.replace(" ", "_"),
            "audience": audience,
            "hidden_goal": "achieve the harness value under realistic friction",
            "pressure": "varies patience, clarity, trust, and domain knowledge",
        }
        for audience in (intent.audiences or ["end user"])
    ]
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
        portrait = portraits[idx % len(portraits)]
        audience = portrait["audience"]
        name, patience, trust, knowledge, purpose = pattern
        heldout = idx % 3 == 2
        portrait_text = (
            f"{portrait['name']}: {audience}. Hidden goal: {portrait['hidden_goal']}. "
            f"Pressure style: {portrait['pressure']}."
        )
        clusters.append(
            SimulationCluster(
                cluster_id=f"{name}_{_slug(portrait['name'])}",
                purpose=f"{purpose}; portrait must stay realistic for {intent.purpose}",
                actor_type=_actor_type(audience),
                portrait=portrait_text,
                behavior_axes={
                    "patience": patience,
                    "trust": trust,
                    "domain_knowledge": knowledge,
                    "ambiguity": "high" if name == "ambiguous" else "medium",
                    "memory_dependency": "high" if name == "memory_dependent" else "medium",
                    "tool_dependency": "high" if name == "tool_dependent" else "medium",
                    "hidden_goal": portrait["hidden_goal"],
                },
                case_count=4 if not heldout else 2,
                heldout=heldout,
                success_checks=[
                    f"agent produces outcome aligned with harness value: {', '.join(intent.value[:3])}",
                    "agent handles user pressure without generic fallback",
                    "required state, tool, or handoff evidence is present",
                ],
                failure_checks=[
                    *(intent.target_failures[:3] or ["agent invents facts or capabilities"]),
                    "agent ignores hidden user goal or pressure style",
                    "agent completes conversation but fails downstream state or trace evidence",
                ],
            )
        )
    return clusters


def create_cases(intent: HarnessIntent, clusters: list[SimulationCluster]) -> list[SimulationCase]:
    command = _default_run_command(intent)
    cases: list[SimulationCase] = []
    for cluster in clusters:
        for index in range(1, cluster.case_count + 1):
            split = "held_out" if cluster.heldout else "held_in"
            cases.append(
                SimulationCase(
                    case_id=f"{cluster.cluster_id}_case_{index}",
                    split=split,
                    cluster_id=cluster.cluster_id,
                    entrypoint=_entrypoint_kind(command),
                    run_command_or_url=command,
                    simulator_prompt=(
                        "Act only as this simulated end user/contact/operator. "
                        f"Portrait: {cluster.portrait} "
                        f"Pressure: {cluster.purpose} "
                        "Do not mention evals, prompts, tests, traces, rubrics, or models."
                    ),
                    max_turns=8,
                    timeout_seconds=600,
                    verifier={
                        "type": "deterministic_or_llm_judge",
                        "config_ref": ".self-harness/verifier.md",
                    },
                    trace_capture=["transcript", "tool_calls", "logs", "state_refs", "judge_result"],
                )
            )
    return cases


def _actor_type(audience: str) -> str:
    lowered = audience.lower()
    if "lead" in lowered or "customer" in lowered:
        return "customer"
    if "operator" in lowered:
        return "operator"
    if "developer" in lowered:
        return "developer"
    return "end_user"


def _slug(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value.lower()).strip("_")


def _default_run_command(intent: HarnessIntent) -> str:
    for entrypoint in intent.entrypoints:
        if ":eval:" in entrypoint:
            return f"uv run {entrypoint.rsplit(':', 1)[-1]}"
    for entrypoint in intent.entrypoints:
        if entrypoint.startswith("package:script:"):
            return f"npm run {entrypoint.rsplit(':', 1)[-1]}"
    return "OWNER_CONFIRM_RUN_COMMAND"


def _entrypoint_kind(command: str) -> str:
    if command.startswith("http"):
        return "api"
    if command.startswith("uv run") or command.startswith("npm run"):
        return "eval_runner"
    return "cli"
