"""Synchronize consented Cairn memory from local Codex transcripts."""
import sys
from sync_memory import main

if __name__ == "__main__":
    sys.argv[1:1] = ["--agent", "codex"]
    raise SystemExit(main())
