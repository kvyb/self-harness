import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from self_harness.discovery import discover
from self_harness.mining import cluster_failures
from self_harness.models import TraceRecord
from self_harness.simulations import create_clusters, create_suite
from self_harness.traces import normalize_trace
from self_harness.validation import validation_decision


class SelfHarnessTests(unittest.TestCase):
    def test_discovery_infers_unclear_repo_questions(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            intent = discover(Path(dirname))
        self.assertLess(intent.confidence, 0.65)
        self.assertTrue(intent.questions)
        self.assertTrue(intent.audience_portraits)

    def test_discovery_infers_persona_audience_portraits(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname)
            (path / "README.md").write_text("Persona agent for users with memory continuity.", encoding="utf-8")
            intent = discover(path)
        self.assertIn("user", intent.audiences)
        self.assertTrue(intent.audience_portraits)

    def test_simulation_clusters_include_heldout(self) -> None:
        intent = discover(Path.cwd())
        clusters = create_clusters(intent, mode="standard")
        self.assertTrue(clusters)
        self.assertTrue(any(cluster.heldout for cluster in clusters))
        self.assertTrue(all(cluster.behavior_axes for cluster in clusters))
        self.assertTrue(all("Hidden goal:" in cluster.portrait for cluster in clusters))

    def test_simulation_suite_contains_runnable_cases(self) -> None:
        intent = discover(Path.cwd())
        suite = create_suite(intent, mode="quick")
        self.assertTrue(suite["cases"])
        self.assertTrue(any(case["split"] == "held_out" for case in suite["cases"]))

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
            {
                "suite_id": "suite",
                "model": "model",
                "evaluator": "eval",
                "environment": "env",
                "held_in": {"total": 3, "pass": 3, "fail": 0, "unknown": 0},
                "held_out": {"total": 3, "pass": 3, "fail": 0, "unknown": 0},
            },
            {
                "suite_id": "suite",
                "model": "model",
                "evaluator": "eval",
                "environment": "env",
                "held_in": {"total": 3, "pass": 3, "fail": 0, "unknown": 0},
                "held_out": {"total": 3, "pass": 2, "fail": 1, "unknown": 0},
            },
        )
        self.assertFalse(decision["validated"])

    def test_failed_trace_requires_paper_signature_fields(self) -> None:
        with self.assertRaisesRegex(Exception, "terminal_cause"):
            normalize_trace({"verifier_result": "fail", "split": "held_in"}, index=0)

    def test_invalid_split_is_rejected(self) -> None:
        with self.assertRaisesRegex(Exception, "invalid split"):
            normalize_trace({"verifier_result": "pass", "split": "train"}, index=0)


if __name__ == "__main__":
    unittest.main()
