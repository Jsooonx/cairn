---
name: cairn
description: "Set up and operate Cairn, a privacy-first project delivery workflow for Codex. Use when creating or adopting a project, standardizing agent collaboration, documenting a change, validating delivery, or optionally maintaining a local Obsidian project-memory vault."
---

# Cairn

Use Cairn to give a project durable instructions, documentation, validation
habits, and optional local memory. Read any repository `AGENTS.md` first.

## First use

Before writing project files, check for `.cairn.json`. If it is absent, explain
the three memory modes and ask the user to choose:

- **Off** — do not install memory scripts or read transcripts.
- **On-demand** — install local memory tools, but sync only after the user
  explicitly asks to sync. This is the default recommendation.
- **Workflow auto** — run a local, project-scoped sync after completed change
  sets. Never enable it without explicit consent.

Explain that memory is local-only, has no telemetry or upload, may inspect
local agent transcripts after consent, and stores file paths by default—not
full prompt text. Run `scripts/setup_project.py <project-root> --memory <mode>`
only after the user chooses.

## Delivery loop

1. Inspect local instructions and the requested surface.
2. Implement only the requested outcome and necessary dependent work.
3. Update documentation that describes changed behavior or architecture.
4. Run proportionate validation and inspect the diff.
5. If memory is configured for workflow auto, synchronize it after the complete
   change set. If on-demand, synchronize only when requested.
6. Commit or push only when the repository instructions authorize it.

## Privacy rules

- Never run a memory synchronizer when `.cairn.json` says `memory.mode: off`.
- Never enable transcript discovery or full request-text capture without
  explicit user consent.
- Keep generated vaults private and ignored by Git.
- Use `references/privacy-and-memory.md` for the exact data model and removal
  procedure.
