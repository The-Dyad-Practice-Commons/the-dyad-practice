---
origin: "dyad-cairn-bootstrap"
unit-kind: "playbook"
trigger: "instantiating a new dyad or defining a new invariant"
claim: "LLM context windows suffer from amnesia and generative drift; soft prompt rules will fail. Invariants must be physically enforced via computational wrappers."
mechanism: "falsify + strict-abstraction"
---
# Hard Guardrails

## Index Line
> **Hard Guardrails:** Never trust the Agent's LLM context window to enforce architectural rules (e.g., "do not commit to main", "always run tests"). The Agent will eventually hallucinate compliance or forget the rule completely. Instead, translate every "soft" prompt rule into a "hard" computational wrapper (e.g., a `./bin/git` hook that crashes on `main`, or `./bin/run-tests` tied to CI) on Day 1.

## The Move:
1. Identify a critical invariant (e.g., WIP-N=1, TDD-only, Substrate Sandboxing).
2. Falsify the assumption that the Agent will just "remember" to do it.
3. **Separate the Builder from the Enforcer.** Do not embed invariant policing into materialization tools (e.g., a package installer should just install).
4. Build a dedicated, deterministic Enforcer (e.g., a `./bin/git` wrapper or a CI test guard) that structurally blocks execution if the rule is violated.
5. Anchor the invariant in `GEMINI.md` specifically bound to that Enforcer script.
