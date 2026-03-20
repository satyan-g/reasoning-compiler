# FINDINGS.md

A running log of experiment results and key observations. Each entry should be dated and reference the experiment config that produced it.

---

## 2026-03-15: Baseline LLM test — Sonnet on raw NL problems

**Config**: `scripts/baseline_llm_test.sh` (9 problems: 3 logic grid, 5 GSM8K arithmetic, 1 UNSAT)
**Question**: Can frontier models (Sonnet) solve our test problems without FRL or solvers?

**Result**: 8/9 correct (89%).
- Logic grids: 3/3 — including full Zebra Puzzle with correct reasoning trace
- Arithmetic: 4/5 — failed gsm8k_800 (got 417, expected 428; forgot +11 in "half plus 11")
- UNSAT detection: 1/1

**Key observation**: Sonnet's Zebra Puzzle response correctly translated all 14 NL constraints into logical deductions. The model is already a competent NL→formal translator — it just does the formalization implicitly in its reasoning trace rather than producing an explicit FRL.

**The failure was execution, not formulation.** gsm8k_800 error was an arithmetic slip (278/2 = 139, then forgot to add 11), not a constraint translation error. The model knew what to compute and got the calculation wrong.

**Implication**:
1. Fertility-as-diagnostic is dead for frontier models — they handle constraint-heavy problems fine
2. The value of FRL is not capability (Sonnet can solve these) but **reliability + verifiability**:
   - 89% isn't 100%. In high-stakes domains, the 11% matters.
   - FRL pipeline produces mathematical certificates. Sonnet produces plausible text.
   - FRL failures are debuggable (UNSAT cores with provenance). Sonnet failures are opaque.
3. LLMs are good constraint compilers but unreliable calculators — exploit this asymmetry

**Next step**: The paper framing shifts from "LLMs can't do this" to "LLMs can do this but can't prove they did it right."

---

## 2026-03-20: Why FRL over direct tool use?

**Question**: If LLMs can already call Z3/solvers directly via tool use (write Python, execute), why do we need FRL as an intermediate representation?

**Finding**: Direct tool use works for simple cases but lacks four properties FRL provides:

1. **Verification of formulation** — When LLM generates Z3 code directly, nothing checks that the code captures the NL constraints correctly. FRL + independent verifier traces every constraint back to its NL source.

2. **Structured repair** — Direct Z3 errors are raw. FRL UNSAT cores map back to specific NL constraints via provenance — the LLM can reason about *which constraint is wrong* in the same language it formulated in.

3. **Solver portability** — Z3 Python code doesn't work with Gurobi or MiniZinc. FRL is solver-agnostic; the compiler backend can change without touching the formulation.

4. **Trainable dataset** — Direct tool calls are opaque traces. FRL formulations are structured, inspectable, and produce verified (NL, FRL) pairs for training smaller models.

**The analogy**: FRL is to solvers what compiler IR is to machine code. You *could* go straight from source to machine code, but the IR gives you optimization, verification, and portability.

**Who benefits from FRL vs direct tool use**:
- Casual use → direct tool calls win (simpler)
- High-stakes domains (medical, legal, financial) → FRL wins (certificates)
- Training small models → FRL wins (structured data)
- Research → FRL wins (inspectable, reproducible)

**Implication**: FRL doesn't compete with tool use. It adds a typed, verifiable layer between the LLM and the solver. Position it as the "typed IR for reasoning" — not a replacement for tool use, but a layer that makes tool use provable.

### Template

```
## YYYY-MM-DD: [Experiment name]

**Config**: experiments/configs/[config_file].yaml
**Question**: What were we testing?
**Result**: What did we find?
**Implication**: What does this mean for the project?
**Next step**: What should we do based on this?
```
