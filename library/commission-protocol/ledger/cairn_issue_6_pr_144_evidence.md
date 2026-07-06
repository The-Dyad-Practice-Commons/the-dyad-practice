# Evidence: Issue #6 / PR #144

**Context:** The commission protocol underwent live falsification through dyad-cairn's own internal execution cycles (Issue #6 / PR #144).

**Friction Encountered:**
During two live commissions, the initial bounds of the protocol were tested. The assumption that standard DMs or unstructured branch work could carry the complexity of a multiparty commission proved insufficient. The friction manifested as misaligned routing and untracked changes when the architecture collided with implementation. 

**Survived Falsification:**
The protocol was amended in PR #144 to strictly enforce the "Universal Issue-Interaction Invariant." By physically locking communication to GitHub Issues within the standalone repository after the "Bootstrap Window", and forcing the Issue ➔ Spec-Rub ➔ PR ➔ Merge pipeline, the protocol actively prevented the conflation of raw theory with execution code. 

The amendment was not merely asserted; it was tested and survived across two live commissions, successfully halting abstraction violations and forcing the proper sub-commissioning routing. This ledger entry grounds the Playbook in lived, mechanical truth.
