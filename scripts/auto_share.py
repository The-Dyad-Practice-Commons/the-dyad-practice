#!/usr/bin/env python3
import os
import sys
import subprocess
import hashlib

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def birth_digest(anchor_bytes, date_str):
    # The IDENTITY CAVEAT hashes `git show <first-commit>:<anchor>` VERBATIM ‖ %cI. Hash the RAW anchor
    # bytes — stripping (e.g. dropping the trailing newline `git show` emits) mints a DIFFERENT, WRONG
    # hash: the 72ba645f regression that mis-registered dyad-steward (canonical was 4c42be0b). The old code
    # took content through run_cmd(), whose .strip() silently dropped that newline. Bytes in, no normalization.
    return "sha256:" + hashlib.sha256(anchor_bytes + date_str.encode("utf-8")).hexdigest()


def compute_birth_hash():
    # Run from the dyad root; the birth anchor is the earliest-committed CLAUDE.md/GEMINI.md.
    anchor_file = next((f for f in ("CLAUDE.md", "GEMINI.md") if os.path.exists(f)), None)
    if not anchor_file:
        print("Error: Could not find CLAUDE.md or GEMINI.md in the current directory.")
        sys.exit(1)
    first_commit = run_cmd(f"git log --diff-filter=A --format=%H -1 -- {anchor_file}")
    anchor_bytes = subprocess.run(["git", "show", f"{first_commit}:{anchor_file}"],
                                  capture_output=True).stdout  # RAW bytes — must NOT strip (see birth_digest)
    date_str = run_cmd(f"git show -s --format=%cI {first_commit}")
    return birth_digest(anchor_bytes, date_str)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./commons/scripts/auto_share.py <discipline-name>")
        sys.exit(1)
        
    discipline_name = sys.argv[1]
    
    if not os.path.isdir("commons"):
        print("Error: 'commons' submodule not found.")
        sys.exit(1)

    print("Computing birth-hash for provenance...")
    birth_hash = compute_birth_hash()
    
    # We are scaffold the library inside the commons submodule
    lib_dir = f"commons/library/{discipline_name}"
    ledger_dir = f"{lib_dir}/ledger"
    
    os.makedirs(ledger_dir, exist_ok=True)
    
    playbook_file = f"{lib_dir}/PLAYBOOK.md"
    if not os.path.exists(playbook_file):
        print(f"Scaffolding {playbook_file}...")
        content = f"""---
origin: "{birth_hash}"
unit-kind: playbook
schema-version: discipline-ontology@2026-05-31
trigger: "Fill in the trigger condition here"
---
# Playbook: {discipline_name}

## The Move
*(Write the one-liner recipe here - the move that creates the +1)*

## Context
*(Explain when to use this playbook and what problem it solves)*
"""
        with open(playbook_file, "w", encoding="utf-8") as f:
            f.write(content)
            
    ledger_file = f"{ledger_dir}/{birth_hash.replace('sha256:', '')}-1.md"
    if not os.path.exists(ledger_file):
        print(f"Scaffolding {ledger_file}...")
        ledger_content = f"""# Testimonial 1
- **contributor:** `{birth_hash}`

## The Output
*(Describe how this playbook produced a +1 in your specific use case)*
"""
        with open(ledger_file, "w", encoding="utf-8") as f:
            f.write(ledger_content)

    print("\n--- ACTION REQUIRED ---")
    print(f"1. Open {playbook_file} and define the playbook.")
    print(f"2. Open {ledger_file} and write your testimonial (evidence).")
    print(f"3. cd commons && git checkout -b share/{discipline_name}")
    print("4. git add library/ && git commit -m 'Share: {discipline_name}' && git push && gh pr create")

if __name__ == "__main__":
    main()
