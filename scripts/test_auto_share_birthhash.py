#!/usr/bin/env python3
# Regression guard for the birth_hash strip bug (the 72ba645f mis-registration of dyad-steward). The
# IDENTITY CAVEAT hashes the RAW anchor bytes ‖ %cI; the old compute_birth_hash routed content through
# run_cmd(), whose .strip() dropped the trailing newline `git show` emits, minting a WRONG hash. This
# pins birth_digest to raw-bytes behavior. Plain Python, no framework.
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto_share

FAILS = []


def check(cond, label):
    print(("PASS" if cond else "FAIL") + f"  {label}")
    if not cond:
        FAILS.append(label)


DATE = "2026-05-29T18:28:50-07:00"
CONTENT = b"# anchor\ncovalent\n"  # trailing newline, as a real anchor's `git show` output carries

check(auto_share.birth_digest(CONTENT, DATE) != auto_share.birth_digest(CONTENT.rstrip(b"\n"), DATE),
      "birth_digest is newline-sensitive (raw bytes, not stripped) — guards the 72ba645f regression")
check(auto_share.birth_digest(CONTENT, DATE).startswith("sha256:") and
      len(auto_share.birth_digest(CONTENT, DATE)) == len("sha256:") + 64,
      "birth_digest returns a well-formed sha256: digest")
check(auto_share.birth_digest(CONTENT, DATE) == auto_share.birth_digest(CONTENT, DATE),
      "birth_digest is deterministic")

print("\n" + ("ALL PASS" if not FAILS else f"FAILURES: {FAILS}"))
sys.exit(1 if FAILS else 0)
