from __future__ import annotations

from collections import defaultdict

from self_harness.models import FailureCluster, TraceRecord


def cluster_failures(traces: list[TraceRecord]) -> list[FailureCluster]:
    groups: dict[tuple[str, str, str], list[TraceRecord]] = defaultdict(list)
    for trace in traces:
        if trace.split == "held_in" and trace.verifier_result == "fail":
            groups[trace.signature].append(trace)
    clusters: list[FailureCluster] = []
    for index, (signature, records) in enumerate(sorted(groups.items()), start=1):
        terminal_cause, causal_status, agent_mechanism = signature
        trace_ids = [record.trace_id for record in records]
        clusters.append(
            FailureCluster(
                failure_cluster_id=f"fc-{index:03d}",
                terminal_cause=terminal_cause,
                causal_status=causal_status,
                agent_mechanism=agent_mechanism,
                trace_ids=trace_ids,
                representative_trace_ids=trace_ids[:3],
                support=len(trace_ids),
                addressable=False,
                addressability_reason=(
                    "Requires host agent or owner to map this mechanism to one declared editable surface."
                ),
            )
        )
    return sorted(clusters, key=lambda cluster: (-cluster.support, cluster.failure_cluster_id))
