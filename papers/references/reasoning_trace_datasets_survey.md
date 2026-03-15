# Survey: Reasoning Trace Datasets

**Purpose:** Map existing datasets that capture how logical problems are formulated, planned, and solved. Identify gaps relevant to the reasoning-compiler project.

**Date:** 2026-03-14

---

## Key Finding

No single dataset captures ground-truth at all three levels: formulation (NL → formal), planning (strategy selection), and execution (solver traces). This is a gap and a dataset opportunity.

---

## Tier 1: NL → Formal Formulation Pairs

| Dataset | Formal Lang | Size | Verified? | Source |
|---|---|---|---|---|
| FOLIO | FOL | 1,430 | Human-annotated | Han et al., EMNLP 2024, arxiv 2209.00840 |
| NL4Opt | LP/MILP | 1,101 | Expert-verified | NeurIPS 2022 Competition, arxiv 2303.08233 |
| Planetarium | PDDL | 132K | Ground-truth | BatsResearch 2024, github.com/BatsResearch/planetarium |
| Herald | Lean 4 | 580K | Type-checked | ICLR 2025(?), arxiv 2410.10878 |
| MALLS | FOL | 28K | Partial (GPT-4 generated) | Yang et al., 2024 |
| LogiQA 2.0 | Reasoning type labels | 35K | Expert exam questions | Liu et al., 2023 |

## Tier 2: Proof/Reasoning Traces

| Dataset | Trace Type | Size | Verified? | Source |
|---|---|---|---|---|
| ProofWriter | NL proof trees (D0-D5) | ~10K+ | Synthetic, guaranteed | Tafjord et al., ACL Findings 2021 |
| EntailmentBank | Human entailment trees | 1,840 | Human expert | Dalvi et al., EMNLP 2021, arxiv 2104.08661 |
| PrOntoQA | FOL proof chains | Configurable | Synthetic | Saparov & He, ICLR 2023 |
| ProverQA | Symbolic + NL chains | 6,500 | Prover9-verified | ICLR 2025, github.com/opendatalab/ProverGen |
| BoardgameQA | Defeasible reasoning | Configurable | Synthetic | Kazemi et al., NeurIPS 2023, arxiv 2306.07934 |

## Tier 3: Solver-Integrated Traces

| Dataset | Pipeline | Size | Source |
|---|---|---|---|
| ZebraLogic | NL → CSP → solver | 1,000 | Lin et al., 2025, arxiv 2502.01100 |
| Logic.py | NL → DSL → constraint solver | (eval on ZebraLogic) | arxiv 2502.15776 |
| SATBench | CNF/NL → SAT/UNSAT | 2,100 | arxiv 2505.14615 |
| SatLM | NL → SAT → solver | Framework | Ye et al., 2023, arxiv 2305.09656 |
| Logic-LM | NL → symbolic → solver + self-refine | Framework | Pan et al., EMNLP 2023, arxiv 2305.12295 |
| Faithful CoT | NL → symbolic → deterministic exec | Framework | Lyu et al., 2023, arxiv 2301.13379 |

## Tier 4: Closest to Full Pipeline (but none complete)

| Dataset | What it has | What it lacks |
|---|---|---|
| Faithful CoT | Formulation + NL decomposition + solver exec | Formulations are LLM-generated, not ground-truth |
| Logic-LM | Formulation + solver + self-refinement loop | Formulations LLM-generated, no planning trace |
| SymbCoT | Formulation + step plan + verification | Formulations LLM-generated |

---

## Most Relevant for Our Project

1. **ZebraLogic** — logic grid puzzles, our domain, LLMs still fail (33% best). Good test bed.
2. **FOLIO** — highest quality NL→FOL pairs. Could adapt annotations to FRL.
3. **ProverQA** — newest, dual symbolic+NL traces, prover-verified.
4. **NL4Opt** — for optimization domain extension later.
5. **Logic-LM** — closest competitor architecture, useful for comparison.

---

## The Gap: Full Pipeline Trace Dataset

Nobody has ground-truth annotations at all three levels:
- **Formulation:** NL → formal with provenance (which span → which constraint)
- **Planning:** strategy selection with rationale
- **Execution:** solver calls + results in formal language, backtracking, certificates

This is an opportunity for a dataset contribution. See spark in docs/sparks.md.
