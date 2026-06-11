from __future__ import annotations

import json
import re
from pathlib import Path

from self_harness.models import HarnessIntent, REQUIRED_QUESTIONS

DOC_NAMES = ("README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md")
DOC_DIRS = ("docs", "documentation", "examples", "evals", "tests")
SOURCE_PATTERNS = (
    "src/**/*simulat*.py",
    "src/**/*judge*.py",
    "src/**/*eval*.py",
    "src/**/*prompt*.py",
    "src/**/*agent*.py",
    "src/**/*harness*.py",
    "src/**/*memory*.py",
)
ENTRYPOINT_FILES = ("package.json", "pyproject.toml", "go.mod", "Cargo.toml", "Makefile")
LIVE_EVAL_HINTS = ("live", "eval", "judge", "scenario", "simulation", "simulator", "batch")


def discover(repo: Path) -> HarnessIntent:
    texts = _load_repo_text(repo)
    haystack = "\n".join(texts).lower()
    entrypoints = _find_entrypoints(repo)
    surfaces = _find_editable_surfaces(repo)
    audiences = _infer_audiences(haystack)
    portraits = _audience_portraits(haystack, audiences)
    purpose = _infer_purpose(haystack, entrypoints)
    value = _infer_value(haystack)
    failures = _infer_failures(haystack)
    confidence = _confidence(purpose, audiences, entrypoints, surfaces)
    questions = [] if confidence >= 0.65 else REQUIRED_QUESTIONS
    return HarnessIntent(
        purpose=purpose,
        value=value,
        audiences=audiences,
        audience_portraits=portraits,
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
    for pattern in SOURCE_PATTERNS:
        paths.extend(sorted(repo.glob(pattern))[:12])
    texts: list[str] = []
    for path in paths[:60]:
        try:
            texts.append(path.read_text(encoding="utf-8")[:12000])
        except UnicodeDecodeError:
            continue
    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        texts.append(pyproject.read_text(encoding="utf-8")[:12000])
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            texts.append(json.dumps(json.loads(package_json.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            texts.append(package_json.read_text(encoding="utf-8")[:12000])
    return texts


def _find_entrypoints(repo: Path) -> list[str]:
    found = [name for name in ENTRYPOINT_FILES if (repo / name).exists()]
    found.extend(_pyproject_scripts(repo))
    found.extend(_package_scripts(repo))
    for pattern in ("scripts/*.py", "scripts/*.js", "bin/*", "src/**/app.py", "src/**/server.ts"):
        found.extend(str(path.relative_to(repo)) for path in sorted(repo.glob(pattern))[:10])
    return sorted(dict.fromkeys(found))


def _pyproject_scripts(repo: Path) -> list[str]:
    path = repo / "pyproject.toml"
    if not path.exists():
        return []
    scripts: list[str] = []
    in_scripts = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts and line.startswith("["):
            break
        if in_scripts and "=" in line:
            name = line.split("=", 1)[0].strip()
            prefix = "eval" if any(hint in name.lower() for hint in LIVE_EVAL_HINTS) else "script"
            scripts.append(f"pyproject:{prefix}:{name}")
    return scripts


def _package_scripts(repo: Path) -> list[str]:
    path = repo / "package.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        return []
    return [f"package:script:{name}" for name in sorted(scripts)]


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
        for path in sorted(repo.glob(pattern)):
            if _allowed_surface(repo, path):
                candidates.append(str(path.relative_to(repo)))
            if len(candidates) >= 80:
                break
    return sorted(dict.fromkeys(candidates))[:40]


ARTIFACT_DIR_NAME = ".self-harness"
DENY_DIR_PARTS = {
    ".agents",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "dist",
    "node_modules",
    "site-packages",
}
ALLOW_TOP_LEVEL = {"src", "tests", "docs", "scripts", "app", "apps", "packages"}
ALLOW_FILES = {"pyproject.toml", "package.json", "go.mod", "Cargo.toml", "Makefile"}


def _allowed_surface(repo: Path, path: Path) -> bool:
    if not path.is_file():
        return False
    rel = path.relative_to(repo)
    if ARTIFACT_DIR_NAME in rel.parts:
        return False
    if any(part in DENY_DIR_PARTS for part in rel.parts):
        return False
    if rel.name in ALLOW_FILES:
        return True
    return bool(rel.parts and rel.parts[0] in ALLOW_TOP_LEVEL)


def _infer_audiences(text: str) -> list[str]:
    phrase_patterns = [
        r"\badult dating-app user\b",
        r"\bdating-app user\b",
        r"\bend user\b",
        r"\bqualified lead\b",
        r"\bsupport customer\b",
        r"\bcustomer\b",
        r"\boperator\b",
        r"\bdeveloper\b",
        r"\bcreator\b",
    ]
    phrases = [match.group(0) for pattern in phrase_patterns for match in re.finditer(pattern, text)]
    if phrases:
        return sorted(dict.fromkeys(phrases))[:6]
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


def _audience_portraits(text: str, audiences: list[str]) -> list[dict[str, str]]:
    return [
        {
            "name": audience.replace(" ", "_"),
            "audience": audience,
            "hidden_goal": "achieve the harness value under realistic friction",
            "pressure": "varies patience, clarity, trust, and domain knowledge",
        }
        for audience in audiences[:4]
    ]


def _infer_purpose(text: str, entrypoints: list[str]) -> str:
    if "dating" in text or "persona" in text:
        return "persona conversation agent harness"
    if "support" in text:
        return "support or customer-service agent harness"
    if "sales" in text or "lead" in text:
        return "sales or intake agent harness"
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
    for word in (
        "ai smell",
        "scripted",
        "generic",
        "hallucination",
        "timeout",
        "handoff",
        "memory",
        "tool",
        "retry",
        "latency",
        "cost",
        "frozen",
        "recap",
        "promise",
    ):
        if word in text:
            failures.append(word.replace(" ", "_"))
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
