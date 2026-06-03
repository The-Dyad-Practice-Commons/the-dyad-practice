#!/usr/bin/env python3
# Co-located regression test for falsify.py's per-source UNREACHABLE detection (Commons-owned). Guards the
# fix for healer's falsification: a clean inbox must never silently mean 'no mail I could reach'. Plain
# Python, no framework — runnable now. Mocks `subprocess.run` so it drives the REAL _gh_json / dm_items.
import os
import sys
import tempfile
import types

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subprocess

import falsify

# Each directory entry maps to a (owner/repo) mailbox; the fake gh returns a canned result per endpoint.
# Endpoints: "repos/<o>/<r>/contents/dm/dyad-steward" (mailbox listing) and "repos/<o>/<r>" (repo probe).
ME = "dyad-steward"
RESPONSES = {
    # dyad-mail: public repo WITH a DM for me → 200 + file list (no probe needed)
    "repos/o-mail/box/contents/dm/dyad-steward": (0, '[{"name":"2026-06-03-hi.md","html_url":"u"}]', ""),
    # dyad-nomail: public repo, no dm/<me> dir → contents 404 but repo reachable → BENIGN (silent)
    "repos/o-nomail/box/contents/dm/dyad-steward": (1, "", "gh: Not Found (HTTP 404)"),
    "repos/o-nomail/box": (0, '{"full_name":"o-nomail/box"}', ""),
    # dyad-private: private/gone anchor → contents 404 AND repo 404 → UNREACHABLE (private)
    "repos/o-priv/box/contents/dm/dyad-steward": (1, "", "gh: Not Found (HTTP 404)"),
    "repos/o-priv/box": (1, "", "gh: Not Found (HTTP 404)"),
    # dyad-net: transport failure, no HTTP code → UNREACHABLE (network)
    "repos/o-net/box/contents/dm/dyad-steward": (1, "", "error connecting to api.github.com: timeout"),
    "repos/o-net/box": (1, "", "error connecting to api.github.com: timeout"),
}


def fake_run(argv, capture_output=True, text=True):
    path = argv[2]  # ["gh", "api", path]
    rc, out, err = RESPONSES[path]
    return types.SimpleNamespace(returncode=rc, stdout=out, stderr=err)


def setup_dir():
    root = tempfile.mkdtemp()
    ddir = os.path.join(root, "directory"); os.makedirs(ddir)
    os.makedirs(os.path.join(root, "falsification"))
    for name, owner in [("dyad-mail", "o-mail"), ("dyad-nomail", "o-nomail"),
                        ("dyad-priv", "o-priv"), ("dyad-net", "o-net"), (ME, "o-self")]:
        open(os.path.join(ddir, f"{name}.yaml"), "w").write(
            f"name: {name}\nlocator: https://github.com/{owner}/box\n")
    return os.path.join(root, "falsification")


FAILS = []


def check(cond, label):
    print(("PASS" if cond else "FAIL") + f"  {label}")
    if not cond:
        FAILS.append(label)


def main():
    subprocess.run = fake_run  # falsify.py calls subprocess.run by module ref
    ledger = setup_dir()

    unreachable = []
    items = list(falsify.dm_items(ledger, ME, unreachable))

    # 1. The one reachable DM is yielded.
    check(len(items) == 1 and items[0][0] == "dyad-mail", "reachable DM yielded (dyad-mail)")

    # 2. A public repo with no dm/<me> dir is BENIGN — not flagged (no cry-wolf on empty mailboxes).
    names = {n for n, _repo, _why in unreachable}
    check("dyad-nomail" not in names, "benign 404 (no dm dir) is NOT flagged unreachable")

    # 3. Private anchor and network failure ARE flagged, with the boundary named.
    check("dyad-priv" in names and "dyad-net" in names, "private + network sources flagged unreachable")
    why = {n: w for n, _r, w in unreachable}
    check(why.get("dyad-priv") == "private/not-a-collaborator", "private boundary named")
    check(why.get("dyad-net") == "gh/network error", "network boundary named")
    check(len(unreachable) == 2, "exactly 2 unreachable (not the benign one)")

    # 4. _gh_json parses the HTTP code out of stderr.
    ok, status, _ = falsify._gh_json("repos/o-priv/box")
    check(ok is False and status == 404, "_gh_json extracts HTTP 404 from stderr")

    # 5. The warning line is non-counterfeit: states the count and that 'no mail' != 'all reached'.
    line = falsify._unreachable_line(unreachable)
    check(line.startswith("⚠ 2 sources UNREACHABLE") and "no mail from everyone" in line,
          "warning line names count + the counterfeit-green risk")

    print(("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED: {FAILS}"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
