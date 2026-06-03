#!/usr/bin/env python3
# Co-located regression test for validate_registry.py (homes with the script it guards — Commons-owned;
# guards ANY modifier, not only when the Steward is in the loop). Plain Python, no framework — runnable
# now (`python3 scripts/test_validate_registry.py`); CI wiring on script-touching PRs is a deferred
# Founding step. Runs the REAL validate_file, never a reimplementation.
import os
import sys
import tempfile

sys.dont_write_bytecode = True  # don't dirty scripts/ with __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_registry import validate_file

GOOD = ("name: dyad-test\n"
        'birth_hash: "sha256:' + "a" * 64 + '"\n'
        "locator: github.com/x/dyad-test\n"
        "summits:\n  - alpha\n")

# (label, filename, body, expected) — each defect-earned or a core invariant
CASES = [
    ("good entry",            "dyad-test.yaml",  GOOD,                                              True),
    ("missing field",         "dyad-test.yaml",  "name: dyad-test\n",                               False),
    ("empty summits",         "dyad-test.yaml",  GOOD.replace("  - alpha\n", "  []\n"),             False),
    ("non-string summit (#20)","dyad-test.yaml", GOOD.replace("  - alpha", "  - 123"),              False),
    ("bad name",              "dyad-bad.yaml",   GOOD.replace("dyad-test", "Dyad_BAD"),             False),
    ("placeholder hash",      "dyad-test.yaml",  GOOD.replace("a" * 64, "TODO"),                    False),
    ("filename ≠ name",       "dyad-other.yaml", GOOD,                                              False),
]


def main():
    d = tempfile.mkdtemp()
    failures = 0
    for label, fname, body, expected in CASES:
        path = os.path.join(d, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        got = validate_file(path)
        ok = got is expected
        print(f"{'ok' if ok else 'XX'}  {label}: validate_file→{got} (want {expected})")
        failures += not ok
    print("OK" if not failures else f"{failures} FAILED")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
