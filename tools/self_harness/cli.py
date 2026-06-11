from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.self_harness.discovery import discover
from tools.self_harness.io import artifact_path, ensure_artifact_dir, read_json, write_json, write_jsonl
from tools.self_harness.mining import cluster_failures
from tools.self_harness.models import REQUIRED_QUESTIONS, HarnessIntent
from tools.self_harness.proposals import proposals_markdown, propose
from tools.self_harness.simulations import create_clusters
from tools.self_harness.traces import load_traces
from tools.self_harness.validation import validation_decision


def main() -> None:
    parser = argparse.ArgumentParser(prog="self-harness")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("discover")
    sim = sub.add_parser("create-sim-clusters")
    sim.add_argument("--mode", choices=["quick", "standard", "exploratory"], default="standard")
    norm = sub.add_parser("normalize-traces")
    norm.add_argument("path", type=Path)
    sub.add_parser("cluster-failures")
    sub.add_parser("propose-harness-edits")
    val = sub.add_parser("validate-proposals")
    val.add_argument("--baseline", type=Path, required=True)
    val.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    repo = Path.cwd()
    if args.command == "init":
        run_init(repo)
    elif args.command == "discover":
        run_discover(repo)
    elif args.command == "create-sim-clusters":
        run_create_sim_clusters(repo, args.mode)
    elif args.command == "normalize-traces":
        run_normalize_traces(repo, args.path)
    elif args.command == "cluster-failures":
        run_cluster_failures(repo)
    elif args.command == "propose-harness-edits":
        run_propose(repo)
    elif args.command == "validate-proposals":
        run_validate(repo, args.baseline, args.candidate)


def run_init(repo: Path) -> None:
    base = ensure_artifact_dir(repo)
    (base / "README.md").write_text(
        "# .self-harness\n\n"
        "Local artifacts for Self-Harness simulations, trace mining, proposals, and validation.\n",
        encoding="utf-8",
    )
    (base / "lineage.jsonl").touch()
    print(f"initialized {base}")


def run_discover(repo: Path) -> None:
    intent = discover(repo)
    write_json(artifact_path("intent.json", repo=repo), intent.to_dict())
    lines = ["# Harness Intent", "", f"- Purpose: {intent.purpose}", f"- Confidence: {intent.confidence}"]
    if intent.questions:
        lines.extend(["", "## Owner Questions", *[f"- {question}" for question in REQUIRED_QUESTIONS]])
    artifact_path("intent.md", repo=repo).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {artifact_path('intent.json', repo=repo)}")


def run_create_sim_clusters(repo: Path, mode: str) -> None:
    payload = read_json(artifact_path("intent.json", repo=repo))
    intent = HarnessIntent(**payload)
    clusters = create_clusters(intent, mode=mode)
    suite = {"mode": mode, "clusters": [cluster.to_dict() for cluster in clusters]}
    write_json(artifact_path("simulation-suite.json", repo=repo), suite)
    print(f"wrote {artifact_path('simulation-suite.json', repo=repo)}")


def run_normalize_traces(repo: Path, path: Path) -> None:
    traces = load_traces(path)
    write_jsonl(artifact_path("traces.jsonl", repo=repo), [trace.to_dict() for trace in traces])
    print(f"wrote {artifact_path('traces.jsonl', repo=repo)}")


def run_cluster_failures(repo: Path) -> None:
    traces = load_traces(artifact_path("traces.jsonl", repo=repo))
    clusters = cluster_failures(traces)
    write_json(
        artifact_path("evidence-bundle.json", repo=repo),
        {"failure_clusters": [cluster.to_dict() for cluster in clusters]},
    )
    print(f"wrote {artifact_path('evidence-bundle.json', repo=repo)}")


def run_propose(repo: Path) -> None:
    intent = HarnessIntent(**read_json(artifact_path("intent.json", repo=repo)))
    bundle = read_json(artifact_path("evidence-bundle.json", repo=repo))
    from tools.self_harness.models import FailureCluster

    clusters = [FailureCluster(**item) for item in bundle.get("failure_clusters", [])]
    proposals = propose(clusters, intent)
    write_json(artifact_path("proposals.json", repo=repo), [proposal.to_dict() for proposal in proposals])
    artifact_path("proposals.md", repo=repo).write_text(proposals_markdown(proposals), encoding="utf-8")
    print(f"wrote {artifact_path('proposals.md', repo=repo)}")


def run_validate(repo: Path, baseline: Path, candidate: Path) -> None:
    decision = validation_decision(read_json(baseline), read_json(candidate))
    write_json(artifact_path("validation.json", repo=repo), decision)
    print(f"wrote {artifact_path('validation.json', repo=repo)}")


if __name__ == "__main__":
    main()
