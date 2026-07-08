#!/usr/bin/env python3
# CI guard — instance #1 of the invariant "mechanically-verifiable self-reports are CI-guarded"
# (CONTRIBUTING §Mechanically-verifiable self-reports are CI-guarded). Audits each directory birth_hash by
# RE-RUNNING onboard.py's OWN algorithm (the definitive registration engine — birth_anchor + birth_hash)
# against a clone of the entry's locator, then failing on mismatch. Leveraging the same engine that MINTS the
# hash is the point: the audit and the registration can never diverge on the derivation (raw-vs-strip, anchor
# choice, date format). Would have caught PR #12 — and it flags PR #82's own wrong 4c42be0b.
#
# For each directory/<dyad>.yaml: clone its `locator` (public only), run onboard.birth_anchor + birth_hash in
# the clone, compare to the declared birth_hash.
#   match -> PASS ; mismatch -> FAIL (exit 1) ; private/unreachable/no-anchor -> SKIP (flagged, never trusted).
#
# Trust model (mirrors validate-falsification.yml): run this BASE-checked-out code against the PR's head DATA.
# Cloning + onboard's `git show` read blobs only — no cloned-repo or PR code executes.
import glob
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yaml
import onboard  # the definitive registration engine — single home of the birth_hash algorithm


def locator_url(loc):
    m = re.search(r"github\.com[/:]([^/]+)/(.+?)(?:\.git)?/?$", str(loc or "").strip())
    return f"https://github.com/{m.group(1)}/{m.group(2)}.git" if m else None


def recompute(url):
    """Clone the locator and run onboard.py's OWN birth_anchor + birth_hash in it. (hash, anchor) or (None, reason)."""
    with tempfile.TemporaryDirectory() as d:
        if subprocess.run(["git", "clone", "--quiet", url, d], capture_output=True).returncode != 0:
            return None, "unreachable/private"
        cwd = os.getcwd()
        os.chdir(d)
        try:
            anchor = onboard.birth_anchor()  # (shim, commit) or None — uses CWD, hence the chdir
            if not anchor:
                return None, "no CLAUDE.md/GEMINI.md anchor"
            shim, commit = anchor
            return onboard.birth_hash(shim, commit), shim
        except SystemExit:
            return None, "onboard derivation error"
        finally:
            os.chdir(cwd)


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
        print(f"PASS {name}: birth_hash reproduces via onboard.py ({info})")
        return True
    print(f"FAIL {name}: declared {declared} != onboard.py recompute {got} (anchor {info})")
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
