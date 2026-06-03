#!/usr/bin/env python3
# Co-located regression test for validate_falsification.py (Commons-owned; guards any modifier of the
# channel's schema enforcer). Plain Python, no framework — runnable now. Runs the REAL validators.
import os
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_falsification import validate_fr, validate_response, validate_disposition

FR = ("claim_id: c1\nclaim_type: design-model\nclaim: x\nevidence: y\n"
      "self_named_confounds: [z]\nfalsification_target: what would refute\ndomain: process\n"
      "submitter_dyad_id: dyad-a\nsubmitter_model: m\nsubmitter_human: h\nsubmitted_at: 2026-06-03\n")
RESP = ("responder_dyad_id: dyad-b\nresponder_model: m2\nresponder_human: h2\n"
        "divergent_axes: [model, corpus]\ngrounding: mechanism-grounded\ntarget_claim_hash: abc\n"
        "responded_at: 2026-06-03\nverdict: REFUTED\nattack_type: counter-evidence\nattack: a\n"
        "confound_surfaced: c\n")
DISP = ("disposes_claim_id: c1\ndisposing_dyad_id: dyad-a\ndisposed_verdicts: [dyad-b]\n"
        "disposed_at: 2026-06-03\nsubmitter_disposition: revise\noutcome: revised\n")


def case(body, fn, expected, label, **kw):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "r.yaml")
    open(p, "w", encoding="utf-8").write(body)
    got = fn(p, **kw)
    ok = got is expected
    print(f"{'ok' if ok else 'XX'}  {label}: {fn.__name__}→{got} (want {expected})")
    return not ok


def main():
    f = 0
    f += case(FR, validate_fr, True, "good FR")
    f += case(FR.replace("falsification_target: what would refute\n", ""), validate_fr, False, "no falsification_target (I8)")
    f += case(FR.replace("design-model", "bogus"), validate_fr, False, "bad claim_type")
    f += case(RESP, validate_response, True, "good response")
    f += case(RESP.replace("REFUTED", "MAYBE"), validate_response, False, "bad verdict")
    f += case(RESP.replace("[model, corpus]", "[model, bogus]"), validate_response, False, "bad divergent_axes")
    f += case(RESP.replace("dyad-b", "dyad-a"), validate_response, False, "self-response (I5)", submitter_id="dyad-a")
    f += case(DISP, validate_disposition, True, "good disposition")
    f += case(DISP.replace("revise", "rubber-stamp"), validate_disposition, False, "bad disposition")
    print("OK" if not f else f"{f} FAILED")
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
