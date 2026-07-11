# Cairn

**Cairn is a privacy-first project delivery workflow for Codex.** It helps an
agent set up durable project guidance, keep documentation current, validate
change sets, and—only if you choose—maintain a private local Obsidian memory
vault.

Cairn is created by [Jsooonx](https://github.com/Jsooonx) and released under
the [MIT License](LICENSE).

## What Cairn does

- Creates a small, project-local delivery baseline: `AGENTS.md`, workflow docs,
  and `.cairn.json`.
- Guides Codex toward scoped work, documentation, validation, and clean handoff.
- Provides optional local-only project memory for Obsidian.
- Keeps memory consent separate from normal project setup.

## What Cairn never does

- Upload data, send telemetry, run analytics, or require an account.
- Read any agent transcript before you explicitly enable memory.
- Commit the generated vault.
- Copy full prompt text into the vault by default.

Read the complete data-handling statement in [PRIVACY.md](PRIVACY.md).

## Codex quick start

Install the Cairn plugin through your Codex plugin source, then start a new
Codex thread and enter:

```text
/cairn
```

`/cairn` performs first-run onboarding before it writes project files. It asks
you to choose one memory mode:

| Mode | Behavior |
| --- | --- |
| **Off** | No vault, sync scripts, or transcript reading. |
| **On-demand** (recommended) | Install local tools, but only sync after you explicitly ask `/cairn sync`. |
| **Workflow auto** | Allow a local sync after each completed change set. Choose this only if you want the workflow automated. |

The choice is saved per project in `.cairn.json`; Cairn does not ask again.
You can still use the workflow in natural language with `$cairn` or “Use Cairn
to set up this project.” The slash command is the most predictable Codex entry
point.

## Memory and Obsidian

When memory is enabled, Cairn creates an Obsidian-compatible vault at:

```text
obsidian_memory_vault/
├── Files/       # project-scoped file timelines
└── _index.md    # vault entry point
```

The folder is added to `.gitignore`. By default, the vault contains only file
paths, edit operation labels, and timestamps. Full request text remains off
unless you deliberately set `memory.include_request_text` to `true` in
`.cairn.json`.

Open the project folder as a vault in Obsidian, or open
`obsidian_memory_vault/` directly as its own vault. No Obsidian plugin is
required.

### Sync manually

For an on-demand project, ask Codex:

```text
/cairn sync
```

Or run the project-local command yourself:

```powershell
python scripts/sync_codex_memory.py --discover
```

`--discover` is intentional: without it (or an explicit `--transcript` path),
the script reads no transcript. Gemini support is available through
`python scripts/sync_gemini_memory.py --discover` after you explicitly choose
it for the project.

For another AI agent, point Cairn to a specific local JSONL file instead of
allowing discovery:

```powershell
python scripts/sync_agent_memory.py --transcript C:\logs\agent-session.jsonl
```

The generic format accepts optional `timestamp`, `user_message` or `request`,
and `files` fields. Each file may be a path string or an object with `path` and
`operation`.

### Change or remove memory

Ask Codex one of:

```text
/cairn memory enable
/cairn memory disable
/cairn memory remove
```

Disabling stops future syncs. Removing deletes only Cairn's generated local
vault; it does not touch source code or original agent transcripts.

## Installation scope

There are two ways to install the workflow skill. Run these commands in any
terminal with Node.js available.

### Global installation

Use this when you want Cairn available across all projects for your user:

```powershell
npx skills add https://github.com/Jsooonx/cairn/tree/main/skills/cairn -g -a codex -y
```

After installation, start a new Codex thread and use `$cairn`.

### Project-specific installation

Use this when Cairn should be available only inside one project. Run the
command from that project's root and omit `-g`:

```powershell
cd "<project-root>"
npx skills add https://github.com/Jsooonx/cairn/tree/main/skills/cairn -a codex -y
```

This installs the skill into the project's agent skill directory rather than
your global user directory. It is useful when a team wants the workflow
versioned or enabled for only one repository.

The Skills CLI installs skill files only. The Codex plugin is what provides the
`/cairn` slash command; `$cairn` works with either global or project-specific
skill installation.

## Manual setup

If you prefer direct control, run the bundled script from this package:

```powershell
python scripts/setup_project.py "<project-root>" --memory on-demand
```

Replace `on-demand` with `off` or `auto` as desired. Add
`--include-request-text` only when you explicitly want full requests copied to
the local vault.

## Repository layout

```text
cairn/
├── .codex-plugin/     # Codex plugin manifest
├── commands/          # /cairn command entry
├── skills/cairn/      # reusable workflow instructions
├── scripts/           # setup and consent-gated local sync tools
├── templates/         # project-local docs and AGENTS.md templates
├── PRIVACY.md
└── LICENSE
```
