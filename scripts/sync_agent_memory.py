"""Synchronize Cairn memory from an explicitly supplied generic JSONL transcript."""
import sys
from sync_memory import main

if __name__ == "__main__":
    sys.argv[1:1] = ["--agent", "generic"]
    raise SystemExit(main())
