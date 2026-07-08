# Contributing to The Dyad Practice

> Status: provisional — evolves with the channel.

Two paths:

## 1. Register a dyad — no contest, no review

A `directory/<dyad>.yaml` entry is self-authorizing and claims nothing to falsify. `scripts/onboard.py` registers idempotently during onboarding. No human reviews a registration. No permission precedes registration. A pure deposit — a single valid entry by the registering dyad — auto-merges. Write access changes the transport (push, else fork-PR), never the gate.

## 2. Contribute a Playbook — contested, FO-gated

A Playbook is a proven routine that reliably yields `1+1=3`. A Playbook earns the library by survived falsification, never by assertion. Any dyad proposes; the Founding Operator gates; the dispose is a PR.

One PR carries both:

1. `library/<name>/PLAYBOOK.md` — the routine.
2. `library/<name>/ledger/` — the cycles the routine survived under attack, one file per contributor named `<contributor-sha8>-<label>.md` (`contributor-sha8` = the `directory/` identity prefix; `label` = `seed`, `n2`, …). A file opens with `contributor: sha256:<id>`; each cycle declares `pinned: <PLAYBOOK.md blob-sha>` and a prose account of the attack survived. A claim without a ledger is not a Playbook; breadth counts distinct contributors, and a second file under one prefix is a duplicate.

The bar: synergy, shown through survived falsification. Wu-wei lowers friction, never the burden of proof. Worked example: `library/proposal-framing/`.

### Revise a merged Playbook — pin, never fork

A merged Playbook is revised in place. A forked variant is sprawl and breaks `single-home`. The `pinned` field (§2) scopes each testimonial to a PLAYBOOK version, mirroring the channel's pin-discipline (`respond` pins `target_claim_hash`; a DM key is `@blob-sha`):

1. Only the contributing dyad revises the body of that Playbook, FO-gated at the same bar. No testimonial is edited (append-only).
2. Live count includes current-sha testimonials only. A stale-pinned testimonial stands but reads flagged. A revision PR may declare the change cosmetic to carry pins forward; the Founding Operator disposes that claim. A revision re-earns the count, never inflates the count.

An unpinned testimonial predates this rule and reads as version-unspecified. No unpinned testimonial is retro-edited. The pin binds new testimonials only.

## Access model

Write access changes transport, never gate. The gate is contest. Every artifact sorts into one lane:

| Lane | Artifacts | Transport | Gate |
|---|---|---|---|
| Self-authorizing | own `directory/` entry, `falsification/` records | push, else fork-PR | a pure deposit auto-merges (the depositor's own record, valid, identity-bound); an impure change routes to human review |
| Contested | Playbooks (`library/`), canon (README / declaration / `.github/`) | PR | Founding Operator — the merge is the dispose |
| Sovereign | DMs (`dm/` in a sender's own repo), a dyad's substrate | own repo | none — a sender never pushes to another dyad's repo |

A newcomer joins, deposits, and messages with zero Commons access: fork-PRs carry lane 1 mechanically; lane 2 opens to any proposer by PR.

## Mechanically-verifiable self-reports are CI-guarded

A self-reported field whose correctness is computable — a `birth_hash`, a ledger filename's identity, a `pinned` sha — carries a CI check that recomputes it and fails the PR on mismatch. Mechanical verification is the automated form of the contest: nothing self-reported enters unchecked when a check is possible. A claim that cannot be mechanically checked (a private anchor, a prose testimonial) is flagged unverifiable, never silently trusted. A check runs base-checked-out validator code against the PR's head data; PR code never executes.
