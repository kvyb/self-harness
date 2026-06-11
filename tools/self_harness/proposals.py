from __future__ import annotations

from self_harness.models import FailureCluster, HarnessIntent, ProposalBundle


def propose(clusters: list[FailureCluster], intent: HarnessIntent) -> list[ProposalBundle]:
    surfaces = intent.editable_surfaces
    if not surfaces:
        return []
    proposals: list[ProposalBundle] = []
    for index, cluster in enumerate(clusters[:6], start=1):
        surface = _choose_surface(cluster, surfaces)
        proposals.append(
            ProposalBundle(
                proposal_id=f"proposal-{index:03d}",
                mode=intent.mode,
                proposer=intent.proposer,
                failure_cluster_id=cluster.failure_cluster_id,
                evidence_trace_ids=cluster.representative_trace_ids,
                editable_surface=surface,
                proposed_change=(
                    "Narrowly change this surface so the harness addresses "
                    f"`{cluster.agent_mechanism}` when verifier cause is `{cluster.terminal_cause}`. "
                    "Do not broaden unrelated behavior."
                ),
                expected_effect=(
                    "Reduce recurrence of this failure signature while preserving passing traces."
                ),
                regression_risk=(
                    "May overfit held-in simulations or weaken adjacent workflows; rerun held-out split."
                ),
                target_files=[surface],
                exact_amendments=[
                    "Host agent must inspect evidence traces and write a concrete diff before owner approval.",
                    "Keep the edit limited to the named surface unless owner broadens scope.",
                ],
                addressability_reason=(
                    f"Surface `{surface}` is declared editable; host agent must confirm it controls "
                    f"`{cluster.agent_mechanism}` before applying a patch."
                ),
                validation_plan=[
                    "Rerun held-in cases that produced this failure cluster.",
                    "Rerun held-out suite without exposing held-out traces to proposer.",
                    "Validate only if held-in and held-out non-regression gate passes.",
                ],
            )
        )
    return proposals


def _choose_surface(cluster: FailureCluster, surfaces: list[str]) -> str:
    mechanism_tokens = set(cluster.agent_mechanism.lower().replace("_", " ").split())
    cause_tokens = set(cluster.terminal_cause.lower().replace("_", " ").split())
    tokens = mechanism_tokens | cause_tokens
    for surface in surfaces:
        lowered = surface.lower()
        if any(token and token in lowered for token in tokens):
            return surface
    return surfaces[0]


def proposals_markdown(proposals: list[ProposalBundle]) -> str:
    lines = ["# Self-Harness Proposals", ""]
    if not proposals:
        lines.append("No failed held-in clusters found. Run or normalize traces first.")
    for proposal in proposals:
        lines.extend(
            [
                f"## {proposal.proposal_id}",
                "",
                f"- Mode: `{proposal.mode}`",
                f"- Proposer: `{proposal.proposer}`",
                f"- Failure cluster: `{proposal.failure_cluster_id}`",
                f"- Evidence: `{', '.join(proposal.evidence_trace_ids)}`",
                f"- Editable surface: `{proposal.editable_surface}`",
                f"- Proposed change: {proposal.proposed_change}",
                f"- Target files: `{', '.join(proposal.target_files)}`",
                f"- Expected effect: {proposal.expected_effect}",
                f"- Regression risk: {proposal.regression_risk}",
                f"- Addressability: {proposal.addressability_reason}",
                f"- Status: `{proposal.status}`",
                "",
            ]
        )
    return "\n".join(lines)
