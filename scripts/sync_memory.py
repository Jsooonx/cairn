"""Build a local, project-scoped Obsidian vault only after Cairn memory consent."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def normal(value: str | Path) -> str:
    return str(value).strip().strip("\"'").replace("\\", "/").rstrip("/").lower()


def project_path(value: str | Path, project: Path) -> bool:
    candidate, root = normal(value), normal(project)
    return candidate == root or candidate.startswith(root + "/")


def relative(value: str | Path, project: Path) -> str:
    raw, root = str(value).replace("\\", "/"), str(project).replace("\\", "/")
    return raw[len(root):].lstrip("/") if raw.lower().startswith(root.lower()) else raw


def safe(value: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "-", value).replace(" ", "_")


def patch_paths(text: str) -> list[tuple[str, str]]:
    return [(match.group(1).lower(), match.group(2).strip()) for match in re.finditer(r"\*\*\* (Add|Update|Delete) File: (.+)", text)]


def records(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        try:
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    yield value
        except OSError:
            continue


def collect_codex(paths: Iterable[Path], project: Path, include_requests: bool) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    requests: list[dict[str, str]] = []
    changes: list[dict[str, str]] = []
    for item in records(paths):
        payload, time = item.get("payload") or {}, str(item.get("timestamp", ""))
        if include_requests and item.get("type") == "event_msg" and payload.get("type") == "user_message":
            text = str(payload.get("message", "")).strip()
            if text:
                requests.append({"time": time, "text": text})
        if item.get("type") == "response_item" and payload.get("name") == "apply_patch":
            for operation, path in patch_paths(str(payload.get("input", ""))):
                if project_path(path, project):
                    changes.append({"time": time, "path": relative(path, project), "operation": operation})
    return requests, changes


def collect_gemini(paths: Iterable[Path], project: Path, include_requests: bool) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    requests: list[dict[str, str]] = []
    changes: list[dict[str, str]] = []
    for item in records(paths):
        time = str(item.get("created_at", ""))
        if include_requests and item.get("type") == "USER_INPUT":
            content = str(item.get("content", ""))
            match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.S)
            if match and match.group(1).strip():
                requests.append({"time": time, "text": match.group(1).strip()})
        for call in item.get("tool_calls") or []:
            args = call.get("args") or {}
            path = args.get("TargetFile") or args.get("AbsolutePath")
            if path and project_path(str(path), project):
                changes.append({"time": time, "path": relative(str(path), project), "operation": str(call.get("name", "edit"))})
    return requests, changes


def collect_generic(paths: Iterable[Path], project: Path, include_requests: bool) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Accept a deliberately small JSONL format from another local agent."""
    requests: list[dict[str, str]] = []
    changes: list[dict[str, str]] = []
    for item in records(paths):
        time = str(item.get("timestamp") or item.get("created_at") or "")
        if include_requests:
            text = item.get("user_message") or item.get("request")
            if isinstance(text, str) and text.strip():
                requests.append({"time": time, "text": text.strip()})
        for file in item.get("files") or []:
            path = file.get("path") if isinstance(file, dict) else file
            if isinstance(path, str) and project_path(path, project):
                operation = str(file.get("operation", "edit")) if isinstance(file, dict) else "edit"
                changes.append({"time": time, "path": relative(path, project), "operation": operation})
    return requests, changes


def write_vault(vault: Path, project: Path, changes: list[dict[str, str]], requests: list[dict[str, str]], agent: str) -> None:
    if vault.exists():
        shutil.rmtree(vault)
    (vault / "Files").mkdir(parents=True)
    if requests:
        (vault / "Requests").mkdir()
    history: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in changes:
        history[item["path"]].append(item)
    file_links = []
    for path, entries in sorted(history.items()):
        name = safe(path) + ".md"
        file_links.append(f"- [[Files/{name}|{path}]]")
        lines = [f"# {path}", "", "## Change Timeline", ""]
        lines.extend(f"- {entry['time'] or 'Unknown'} [{entry['operation']}]" for entry in entries)
        (vault / "Files" / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    request_links = []
    for number, item in enumerate(requests, 1):
        name = f"request-{number:03d}.md"
        request_links.append(f"- [[Requests/{name}|Request {number}]]")
        (vault / "Requests" / name).write_text(f"# Request {number}\n\n- Time: {item['time'] or 'Unknown'}\n\n{item['text']}\n", encoding="utf-8")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    index = ["# Cairn Project Memory", "", f"- Project: `{project}`", f"- Source: {agent}", f"- Generated: {now}", "", "## Files", "", *(file_links or ["- No project-scoped edits found"])]
    if requests:
        index.extend(["", "## Requests", "", *request_links])
    (vault / "_index.md").write_text("\n".join(index) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("codex", "gemini", "generic"), default="codex")
    parser.add_argument("--discover", action="store_true", help="Explicitly discover local agent transcripts.")
    parser.add_argument("--transcript", action="append", type=Path, default=[])
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    config_path = project / ".cairn.json"
    if not config_path.is_file():
        parser.error("Cairn is not configured in this project. Run /cairn setup first.")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    memory = config.get("memory") or {}
    if memory.get("mode", "off") == "off":
        print("Cairn memory is off. No transcript was read.")
        return 0
    paths = [path.expanduser() for path in args.transcript if path.is_file()]
    if args.discover and not paths:
        if args.agent == "codex":
            home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            root = Path(os.environ.get("CODEX_SESSIONS_DIR", home / "sessions"))
            paths = list(root.rglob("*.jsonl")) if root.is_dir() else []
        elif args.agent == "gemini":
            root = Path(os.environ.get("ANTIGRAVITY_BRAIN_DIR", Path.home() / ".gemini" / "antigravity" / "brain"))
            paths = list(root.rglob("transcript.jsonl")) if root.is_dir() else []
    if not paths:
        print("No transcript was read. Pass --transcript or explicitly use --discover.")
        return 0
    collector = {"codex": collect_codex, "gemini": collect_gemini, "generic": collect_generic}[args.agent]
    requests, changes = collector(paths, project, bool(memory.get("include_request_text")))
    vault = project / str(memory.get("vault_dir", "obsidian_memory_vault"))
    write_vault(vault, project, changes, requests, args.agent)
    print(f"Cairn memory rebuilt locally: {vault} ({len(changes)} changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
