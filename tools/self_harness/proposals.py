from __future__ import annotations

from tools.self_harness.models import FailureCluster, HarnessIntent, ProposalBundle


def propose(clusters: list[FailureCluster], intent: HarnessIntent) -> list[ProposalBundle]:
    surfaces = intent.editable_surfaces or ["declare editable harness surface before implementation"]
    proposals: list[ProposalBundle] = []
    for index, cluster in enumerate(clusters[:6], start=1):
        surface = surfaces[(index - 1) % len(surfaces)]
        proposals.append(
            ProposalBundle(
                proposal_id=f"proposal-{index:03d}",
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
            )
        )
    return proposals


def proposals_markdown(proposals: list[ProposalBundle]) -> str:
    lines = ["# Self-Harness Proposals", ""]
    if not proposals:
        lines.append("No failed held-in clusters found. Run or normalize traces first.")
    for proposal in proposals:
        lines.extend(
            [
                f"## {proposal.proposal_id}",
                "",
                f"- Failure cluster: `{proposal.failure_cluster_id}`",
                f"- Evidence: `{', '.join(proposal.evidence_trace_ids)}`",
                f"- Editable surface: `{proposal.editable_surface}`",
                f"- Proposed change: {proposal.proposed_change}",
                f"- Expected effect: {proposal.expected_effect}",
                f"- Regression risk: {proposal.regression_risk}",
                f"- Status: `{proposal.status}`",
                "",
            ]
        )
    return "\n".join(lines)

