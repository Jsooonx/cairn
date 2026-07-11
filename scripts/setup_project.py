"""Install Cairn's project-local workflow with an explicit memory mode."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
MEMORY_SCRIPTS = ("sync_memory.py", "sync_codex_memory.py", "sync_gemini_memory.py", "sync_agent_memory.py")


def write_missing(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "written"


def copy_missing(source: Path, target: Path, force: bool) -> str:
    if target.exists() and not force:
        return "kept"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return "written"


def ensure_ignored(project: Path, entry: str) -> str:
    path = project / ".gitignore"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    if entry in {line.strip() for line in content.splitlines()}:
        return "kept"
    path.write_text(content.rstrip() + f"\n{entry}\n", encoding="utf-8")
    return "written"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--memory", choices=("off", "on-demand", "auto"), required=True)
    parser.add_argument("--include-request-text", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = args.project_root.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"Project directory does not exist: {project}")
    if args.memory == "off" and args.include_request_text:
        parser.error("Request text cannot be enabled while memory is off.")

    config = {
        "version": 1,
        "memory": {
            "mode": args.memory,
            "vault_dir": "obsidian_memory_vault",
            "include_request_text": args.include_request_text,
        },
        "privacy": {"telemetry": False, "network": False},
    }
    results = [(".cairn.json", write_missing(project / ".cairn.json", json.dumps(config, indent=2) + "\n", args.force))]
    results.append(("AGENTS.md", write_missing(project / "AGENTS.md", (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8"), args.force)))
    for name in ("development-workflow.md", "design-taste.md"):
        results.append((f"docs/{name}", write_missing(project / "docs" / name, (TEMPLATES / "docs" / name).read_text(encoding="utf-8"), args.force)))

    if args.memory != "off":
        results.append(("docs/memory.md", write_missing(project / "docs" / "memory.md", (TEMPLATES / "docs" / "memory.md").read_text(encoding="utf-8"), args.force)))
        results.append((".gitignore: obsidian_memory_vault/", ensure_ignored(project, "obsidian_memory_vault/")))
        for script in MEMORY_SCRIPTS:
            results.append((f"scripts/{script}", copy_missing(ROOT / "scripts" / script, project / "scripts" / script, args.force)))

    print(f"Cairn initialized in {project} (memory: {args.memory})")
    for path, state in results:
        print(f"  {state:7} {path}")
    if args.memory == "off":
        print("Memory is off: no vault or sync scripts were installed.")
    elif args.memory == "on-demand":
        print("Memory is on-demand: run a sync only after an explicit user request.")
    else:
        print("Memory is auto: sync only at completed change-set boundaries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
