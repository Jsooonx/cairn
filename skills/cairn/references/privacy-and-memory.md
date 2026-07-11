# Privacy and Memory

Memory is optional. Cairn has no network calls, telemetry, analytics, remote
backup, or account. It only writes generated Markdown into the configured local
vault.

## Modes

- `off`: no memory scripts are installed into the project and no transcript is
  read.
- `on-demand`: scripts are installed, but a sync requires an explicit user
  request such as `/cairn sync`.
- `auto`: sync may run at the end of completed change sets after the user has
  explicitly selected this mode.

## What is stored

By default, the vault contains project-scoped file paths, edit timestamps, and
operation labels. Full request text is excluded unless the user changes
`memory.include_request_text` to `true` in `.cairn.json`.

## Remove memory

Set `memory.mode` to `off`, then delete the configured vault folder. This only
removes Cairn-generated local Markdown; it does not alter source files or the
original agent transcript.
