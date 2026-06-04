#!/usr/bin/env python3
# Regression test: the FIRST responder to an FR must not crash. git does not persist the empty `responses/`
# dir cmd_submit creates, so on a fresh clone it is absent; cmd_respond must makedirs it. Plain Python.
import os
import sys
import tempfile
import types

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import falsify

FR = ("claim_id: c1\nclaim_type: design-model\nclaim: x\nevidence: y\n"
      "self_named_confounds: [z]\nfalsification_target: what would refute\ndomain: process\n"
      "submitter_dyad_id: dyad-a\nsubmitter_model: m\nsubmitter_human: h\nsubmitted_at: 2026-06-03\n")
RESP = ("responder_dyad_id: dyad-b\nresponder_model: m2\nresponder_human: h2\n"
        "divergent_axes: [model, corpus]\ngrounding: mechanism-grounded\n"
        "responded_at: 2026-06-03\nverdict: REFUTED\nattack_type: counter-evidence\nattack: a\n"
        "confound_surfaced: c\n")  # NB: no target_claim_hash → cmd_respond must auto-pin it


def main():
    ledger = tempfile.mkdtemp()
    cdir = os.path.join(ledger, "c1"); os.makedirs(cdir)          # claim dir WITHOUT responses/ (the bug trigger)
    open(os.path.join(cdir, "fr.yaml"), "w").write(FR)
    rf = os.path.join(tempfile.mkdtemp(), "r.yaml"); open(rf, "w").write(RESP)

    crashed = None
    try:
        falsify.cmd_respond(ledger, types.SimpleNamespace(claim_id="c1", file=rf))
    except SystemExit as e:                                       # sys.exit on validation fail = a real test failure
        crashed = f"SystemExit: {e}"
    except Exception as e:                                        # the FileNotFoundError this guards against
        crashed = f"{type(e).__name__}: {e}"

    landed = os.path.isfile(os.path.join(cdir, "responses", "dyad-b.yaml"))
    ok = crashed is None and landed
    print(("PASS" if ok else "FAIL") + "  first response lands without a pre-existing responses/ dir"
          + (f"  [{crashed}]" if crashed else ("" if landed else "  [file not written]")))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
