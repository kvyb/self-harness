import tempfile
import unittest
from pathlib import Path

from tools.self_harness.discovery import discover
from tools.self_harness.mining import cluster_failures
from tools.self_harness.models import TraceRecord
from tools.self_harness.simulations import create_clusters
from tools.self_harness.validation import validation_decision


class SelfHarnessTests(unittest.TestCase):
    def test_discovery_infers_unclear_repo_questions(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            intent = discover(Path(dirname))
        self.assertLess(intent.confidence, 0.65)
        self.assertTrue(intent.questions)

    def test_simulation_clusters_include_heldout(self) -> None:
        intent = discover(Path.cwd())
        clusters = create_clusters(intent, mode="standard")
        self.assertTrue(clusters)
        self.assertTrue(any(cluster.heldout for cluster in clusters))
        self.assertTrue(all(cluster.behavior_axes for cluster in clusters))

    def test_failure_clustering_uses_paper_signature(self) -> None:
        trace = TraceRecord(
            trace_id="t1",
            cluster_id="c1",
            case_id="case1",
            split="held_in",
            harness_entrypoint="api",
            simulated_user_role="skeptical customer",
            messages_or_actions=[],
            agent_steps=[],
            tool_calls=[],
            observability_refs=[],
            verifier_result="fail",
            terminal_cause="missing_artifact",
            causal_status="direct",
            agent_mechanism="late_deliverable",
            scores=[],
            metadata={},
        )
        clusters = cluster_failures([trace])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0].terminal_cause, "missing_artifact")
        self.assertEqual(clusters[0].agent_mechanism, "late_deliverable")

    def test_validation_gate_requires_no_regression(self) -> None:
        decision = validation_decision(
            {"held_in_passes": 3, "held_out_passes": 3},
            {"held_in_passes": 4, "held_out_passes": 2},
        )
        self.assertFalse(decision["validated"])


if __name__ == "__main__":
    unittest.main()

