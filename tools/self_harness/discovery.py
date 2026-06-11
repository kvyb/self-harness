from __future__ import annotations

import re
from pathlib import Path

from tools.self_harness.models import HarnessIntent, REQUIRED_QUESTIONS

DOC_NAMES = ("README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md")
DOC_DIRS = ("docs", "documentation", "examples", "evals", "tests")
ENTRYPOINT_FILES = ("package.json", "pyproject.toml", "go.mod", "Cargo.toml", "Makefile")


def discover(repo: Path) -> HarnessIntent:
    texts = _load_repo_text(repo)
    haystack = "\n".join(texts).lower()
    entrypoints = _find_entrypoints(repo)
    surfaces = _find_editable_surfaces(repo)
    audiences = _infer_audiences(haystack)
    purpose = _infer_purpose(haystack, entrypoints)
    value = _infer_value(haystack)
    failures = _infer_failures(haystack)
    confidence = _confidence(purpose, audiences, entrypoints, surfaces)
    questions = [] if confidence >= 0.65 else REQUIRED_QUESTIONS
    return HarnessIntent(
        purpose=purpose,
        value=value,
        audiences=audiences,
        target_failures=failures,
        entrypoints=entrypoints,
        editable_surfaces=surfaces,
        confidence=confidence,
        questions=questions,
    )


def _load_repo_text(repo: Path) -> list[str]:
    paths: list[Path] = []
    for name in DOC_NAMES:
        candidate = repo / name
        if candidate.exists():
            paths.append(candidate)
    for dirname in DOC_DIRS:
        base = repo / dirname
        if base.exists():
            paths.extend(sorted(base.rglob("*.md"))[:25])
            paths.extend(sorted(base.rglob("*.txt"))[:10])
    texts: list[str] = []
    for path in paths[:60]:
        try:
            texts.append(path.read_text(encoding="utf-8")[:12000])
        except UnicodeDecodeError:
            continue
    return texts


def _find_entrypoints(repo: Path) -> list[str]:
    found = [name for name in ENTRYPOINT_FILES if (repo / name).exists()]
    for pattern in ("scripts/*.py", "scripts/*.js", "bin/*", "src/**/app.py", "src/**/server.ts"):
        found.extend(str(path.relative_to(repo)) for path in sorted(repo.glob(pattern))[:10])
    return sorted(dict.fromkeys(found))


def _find_editable_surfaces(repo: Path) -> list[str]:
    candidates: list[str] = []
    for pattern in (
        "**/*prompt*.*",
        "**/*agent*.*",
        "**/*harness*.*",
        "**/*tool*.*",
        "**/*memory*.*",
        "**/*eval*.*",
    ):
        for path in sorted(repo.glob(pattern))[:20]:
            if ".git" not in path.parts and ARTIFACT_DIR_NAME not in path.parts and path.is_file():
                candidates.append(str(path.relative_to(repo)))
    return sorted(dict.fromkeys(candidates))[:40]


ARTIFACT_DIR_NAME = ".self-harness"


def _infer_audiences(text: str) -> list[str]:
    audience_terms = [
        "customer",
        "lead",
        "user",
        "operator",
        "developer",
        "support agent",
        "sales rep",
        "creator",
        "patient",
        "student",
    ]
    found = [term for term in audience_terms if re.search(rf"\b{re.escape(term)}s?\b", text)]
    return found[:6] or ["end user"]


def _infer_purpose(text: str, entrypoints: list[str]) -> str:
    if "support" in text:
        return "support or customer-service agent harness"
    if "sales" in text or "lead" in text:
        return "sales or intake agent harness"
    if "dating" in text or "persona" in text:
        return "persona conversation agent harness"
    if "code" in text or "developer" in text:
        return "coding or developer-assistant harness"
    if entrypoints:
        return "agent harness with repository-detected runtime entrypoints"
    return "unclear agent harness"


def _infer_value(text: str) -> list[str]:
    values: list[str] = []
    for word in ("conversion", "retention", "automation", "quality", "accuracy", "reliability"):
        if word in text:
            values.append(word)
    return values or ["deliver correct, useful outcomes for its intended users"]


def _infer_failures(text: str) -> list[str]:
    failures: list[str] = []
    for word in ("hallucination", "timeout", "handoff", "memory", "tool", "retry", "latency", "cost"):
        if word in text:
            failures.append(word)
    return failures or ["real-user failure modes to be confirmed by owner"]


def _confidence(
    purpose: str,
    audiences: list[str],
    entrypoints: list[str],
    surfaces: list[str],
) -> float:
    score = 0.0
    score += 0.25 if not purpose.startswith("unclear") else 0.0
    score += min(len(audiences), 3) * 0.1
    score += 0.25 if entrypoints else 0.0
    score += 0.2 if surfaces else 0.0
    return min(score, 1.0)

