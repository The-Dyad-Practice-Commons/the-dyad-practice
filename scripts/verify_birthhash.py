#!/usr/bin/env python3
# CI guard — the first instance of the Commons invariant "a mechanically-verifiable self-report carries a
# CI guard" (CONTRIBUTING §Mechanically-verifiable self-reports are CI-guarded). Recomputes each directory
# birth_hash from its birth anchor and fails on mismatch. Would have caught PR #12 (the 72ba645f regression).
#
# Derivation is single-homed: reuses auto_share.birth_digest (RAW anchor bytes ‖ %cI). For each
# directory/<dyad>.yaml: clone its `locator` (public only, treeless), find the earliest-committed
# CLAUDE.md/GEMINI.md, recompute, compare to the declared birth_hash.
#   match -> PASS ; mismatch -> FAIL (exit 1) ; private/unreachable/no-anchor -> SKIP (flagged, never trusted).
#
# Trust model (mirrors validate-falsification.yml): run this BASE-checked-out code against the PR's head
# DATA. Cloning + `git show` reads blobs only — no cloned repo code executes.
import glob
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yaml
from auto_share import birth_digest

ANCHORS = ("CLAUDE.md", "GEMINI.md")


def locator_url(loc):
    m = re.search(r"github\.com[/:]([^/]+)/(.+?)(?:\.git)?/?$", str(loc or "").strip())
    return f"https://github.com/{m.group(1)}/{m.group(2)}.git" if m else None


def recompute(url):
    """(birth_hash, anchor_file) on success, else (None, reason). Treeless clone: full history, blobs lazy."""
    with tempfile.TemporaryDirectory() as d:
        if subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", url, d],
                          capture_output=True).returncode != 0:
            return None, "unreachable/private"
        for anchor in ANCHORS:
            c = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--format=%H", "-1", "--", anchor],
                               capture_output=True)
            commit = c.stdout.decode().strip()
            if c.returncode == 0 and commit:
                content = subprocess.run(["git", "-C", d, "show", f"{commit}:{anchor}"], capture_output=True).stdout
                date = subprocess.run(["git", "-C", d, "show", "-s", "--format=%cI", commit],
                                      capture_output=True).stdout.decode().strip()
                return birth_digest(content, date), anchor
        return None, "no CLAUDE.md/GEMINI.md anchor"


def check_file(path):
    e = yaml.safe_load(open(path, encoding="utf-8")) or {}
    name = e.get("name", os.path.basename(path))
    declared = str(e.get("birth_hash", "")).strip()
    url = locator_url(e.get("locator"))
    if not url:
        print(f"SKIP {name}: unparseable locator (unverifiable — flagged, not trusted)")
        return None
    got, info = recompute(url)
    if got is None:
        print(f"SKIP {name}: {info} (unverifiable — flagged, not trusted)")
        return None
    if got == declared:
        print(f"PASS {name}: birth_hash reproduces from {info}")
        return True
    print(f"FAIL {name}: declared {declared} != recomputed {got} (anchor {info})")
    return False


def main():
    paths = sys.argv[1:] or sorted(glob.glob("directory/*.yaml"))
    results = [check_file(p) for p in paths]
    verified = sum(1 for r in results if r is True)
    failed = [r for r in results if r is False]
    skipped = sum(1 for r in results if r is None)
    print(f"\n{verified} verified · {len(failed)} FAILED · {skipped} unverifiable")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
