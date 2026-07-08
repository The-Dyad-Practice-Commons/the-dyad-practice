#!/usr/bin/env python3
# Pure-logic test for verify_birthhash.locator_url (the network path — clone + recompute — is exercised
# live and in CI). Plain Python, no framework.
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_birthhash as v

FAILS = []


def check(cond, label):
    print(("PASS" if cond else "FAIL") + f"  {label}")
    if not cond:
        FAILS.append(label)


check(v.locator_url("github.com/pltrinh1122/dyad-steward") == "https://github.com/pltrinh1122/dyad-steward.git",
      "bare github.com/owner/repo -> https .git clone URL")
check(v.locator_url("https://github.com/o/r.git") == "https://github.com/o/r.git",
      "full .git URL preserved")
check(v.locator_url("git@github.com:o/r") == "https://github.com/o/r.git",
      "ssh form normalizes to https")
check(v.locator_url("") is None and v.locator_url(None) is None,
      "empty/None locator -> None (unverifiable, not trusted)")
check(v.locator_url("https://example.com/x") is None,
      "non-github locator -> None")

print("\n" + ("ALL PASS" if not FAILS else f"FAILURES: {FAILS}"))
sys.exit(1 if FAILS else 0)
