"""Synchronize consented Cairn memory from local Gemini transcripts."""
import sys
from sync_memory import main

if __name__ == "__main__":
    sys.argv[1:1] = ["--agent", "gemini"]
    raise SystemExit(main())
