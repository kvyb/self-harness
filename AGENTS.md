@./skills/self-harness/SKILL.md

# Self-Harness Repo Guidance

This repository ships a portable skill. The skill is the product.

Keep `skills/self-harness/SKILL.md` concise and put detailed method notes in `skills/self-harness/references/`. Helper code under `tools/self_harness/` must support the skill workflow and write run artifacts into the target repo's `.self-harness/` directory.

Do not turn this into a standalone optimizer app. The intended use is: user invokes the skill from Claude Code, Codex, Hermes, or another agent inside a target harness repo; that host agent runs the workflow.

