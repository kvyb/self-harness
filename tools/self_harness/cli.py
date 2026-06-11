from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from self_harness.io import (
    ArtifactError,
    artifact_path,
    ensure_artifact_dir,
    read_json,
    require_artifact,
    write_json,
    write_jsonl,
)
from self_harness.mining import cluster_failures
from self_harness.models import REQUIRED_QUESTIONS, HarnessIntent
from self_harness.proposals import proposals_markdown, propose
from self_harness.simulations import create_suite
from self_harness.traces import load_traces
from self_harness.validation import validation_decision


def main() -> None:
    parser = argparse.ArgumentParser(prog="self-harness")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    confirm = sub.add_parser("confirm-audience")
    confirm.add_argument("--by", default="owner")
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
    try:
        if args.command == "init":
            run_init(repo)
        elif args.command == "confirm-audience":
            run_confirm_audience(repo, args.by)
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
    except ArtifactError as exc:
        print(f"self-harness: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def run_init(repo: Path) -> None:
    base = ensure_artifact_dir(repo)
    (base / "README.md").write_text(
        "# .self-harness\n\n"
        "Local artifacts for Self-Harness simulations, trace mining, proposals, and validation.\n",
        encoding="utf-8",
    )
    write_json(base / "intent.template.json", _intent_template())
    (base / "audience-confirmation.md").write_text(_audience_confirmation_template(), encoding="utf-8")
    (base / "lineage.jsonl").touch()
    print(f"initialized {base}")


def run_create_sim_clusters(repo: Path, mode: str) -> None:
    require_artifact(repo, "intent.json")
    confirmation = read_json(require_artifact(repo, "owner-confirmation.json"))
    if not confirmation.get("audiences_confirmed"):
        raise ArtifactError("owner-confirmation.json must set audiences_confirmed=true")
    payload = read_json(artifact_path("intent.json", repo=repo))
    intent = HarnessIntent(**payload)
    suite = create_suite(intent, mode=mode)
    write_json(artifact_path("simulation-suite.json", repo=repo), suite)
    write_json(
        artifact_path("held-in-suite.json", repo=repo),
        {**suite, "cases": [case for case in suite["cases"] if case["split"] == "held_in"]},
    )
    write_json(
        artifact_path("held-out-suite.json", repo=repo),
        {**suite, "cases": [case for case in suite["cases"] if case["split"] == "held_out"]},
    )
    print(f"wrote {artifact_path('simulation-suite.json', repo=repo)}")


def run_normalize_traces(repo: Path, path: Path) -> None:
    traces = load_traces(path)
    write_jsonl(artifact_path("traces.jsonl", repo=repo), [trace.to_dict() for trace in traces])
    print(f"wrote {artifact_path('traces.jsonl', repo=repo)}")


def run_cluster_failures(repo: Path) -> None:
    traces = load_traces(require_artifact(repo, "traces.jsonl"))
    clusters = cluster_failures(traces)
    write_json(
        artifact_path("evidence-bundle.json", repo=repo),
        {"failure_clusters": [cluster.to_dict() for cluster in clusters]},
    )
    print(f"wrote {artifact_path('evidence-bundle.json', repo=repo)}")


def run_propose(repo: Path) -> None:
    intent = HarnessIntent(**read_json(require_artifact(repo, "intent.json")))
    bundle = read_json(require_artifact(repo, "evidence-bundle.json"))
    from self_harness.models import FailureCluster

    clusters = [FailureCluster(**item) for item in bundle.get("failure_clusters", [])]
    proposals = propose(clusters, intent)
    write_json(artifact_path("proposals.json", repo=repo), [proposal.to_dict() for proposal in proposals])
    artifact_path("proposals.md", repo=repo).write_text(proposals_markdown(proposals), encoding="utf-8")
    print(f"wrote {artifact_path('proposals.md', repo=repo)}")


def run_validate(repo: Path, baseline: Path, candidate: Path) -> None:
    decision = validation_decision(read_json(baseline), read_json(candidate))
    write_json(artifact_path("validation.json", repo=repo), decision)
    print(f"wrote {artifact_path('validation.json', repo=repo)}")


def run_confirm_audience(repo: Path, confirmed_by: str) -> None:
    require_artifact(repo, "intent.json")
    path = artifact_path("owner-confirmation.json", repo=repo)
    write_json(
        path,
        {
            "audiences_confirmed": True,
            "confirmed_by": confirmed_by,
            "corrections": [],
            "note": "Owner confirmed agent-authored audience portraits before simulation suite generation.",
        },
    )
    print(f"wrote {path}")


def _intent_template() -> dict[str, object]:
    return {
        "purpose": "HOST_AGENT_FILL_FROM_REPO_EVIDENCE",
        "value": ["HOST_AGENT_FILL_FROM_REPO_EVIDENCE"],
        "audiences": ["HOST_AGENT_FILL_FROM_REPO_EVIDENCE"],
        "target_failures": ["HOST_AGENT_FILL_FROM_REPO_EVIDENCE"],
        "entrypoints": ["HOST_AGENT_FILL_FROM_REPO_EVIDENCE"],
        "editable_surfaces": ["HOST_AGENT_FILL_FROM_REPO_EVIDENCE"],
        "confidence": 0.0,
        "audience_portraits": [
            {
                "name": "HOST_AGENT_FILL",
                "audience": "HOST_AGENT_FILL",
                "hidden_goal": "HOST_AGENT_FILL",
                "pressure": "HOST_AGENT_FILL",
            }
        ],
        "questions": REQUIRED_QUESTIONS,
    }


def _audience_confirmation_template() -> str:
    return "\n".join(
        [
            "# Audience Confirmation",
            "",
            "Host agent: fill this from your repo inspection before live simulation.",
            "",
            "## Proposed Portraits",
            "",
            "- TODO: audience, hidden goal, pressure, success criteria",
            "",
            "## Owner Decision",
            "",
            "- [ ] Confirm these portraits",
            "- [ ] Edit portraits before simulation",
            "- [ ] Replace with different audience",
            "",
            "Do not run expensive live simulations until this is confirmed.",
        ]
    ) + "\n"


if __name__ == "__main__":
    main()
