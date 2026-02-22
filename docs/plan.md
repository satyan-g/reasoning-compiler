# Plan: Formalization Fertility → Verified Reasoning via Compilation

## Overview

Two papers, one system. Paper 1 (the tokenization/fertility paper) identifies and diagnoses the bottleneck. Paper 2 (the full FRL+runtime paper) solves it. Both share infrastructure. Build them in parallel but publish Paper 1 first — it's smaller, more novel in framing, and creates the problem that Paper 2 answers.

---

## Paper 1: "Formalization Fertility"

**Working title**: *Formalization Fertility: Why LLM Reasoning Fails at the Tokenization Boundary*

**Core claim**: The NL→formal compilation problem is structurally analogous to the multilingual tokenization problem (Sarvam/MorphTok). Just as BPE shreds morphological units in Indic languages, standard LLM processing shreds semantic-structural units in problem descriptions — and this is the primary failure mode, not lack of reasoning capacity.

**Target venues**: ACL/EMNLP (main), ICML TokShop (workshop), NeurIPS (neuro-symbolic track)

### Contributions

1. **Formalization fertility** as a metric: NL tokens per FRL constraint, measured across datasets
2. **Empirical diagnosis**: high fertility predicts LLM reasoning failure
3. **Constraint pre-tokenization**: a structured extraction pass (AMR/DRS → constraint classification → quantifier normalization) that reduces fertility
4. **Demonstration**: pre-tokenizer + FRL + solver vs. one-shot LLM, measured on solve rate and robustness

### Paper 1 Outline

```
Abstract (250 words)
1. Introduction
   - The Sarvam analogy: fertility in Indic tokenization → fertility in formalization
   - Thesis: problem-solving bottleneck is encoding, not reasoning
2. Formalization Fertility
   - Definition and measurement
   - Analogy table: morpheme↔constraint, sandhi↔implicit assumptions, etc.
3. Empirical Analysis
   - Datasets: GSM8K, logic grid puzzles, NL4Opt, assignment puzzles
   - Measure fertility per problem
   - Correlate with LLM failure rate (one-shot GPT-4/Claude)
   - Show: high fertility ⟹ low solve rate
4. Constraint Pre-Tokenization
   - Architecture: AMR parse → constraint type classifier → quantifier normalizer → structured IR
   - Training the classifier on synthetic data
5. Experiments
   - Baselines: one-shot LLM, CoT, PAL, DECLARATIVE
   - System: pre-tokenizer → FRL → Z3 → certificate
   - Metrics: solve rate, robustness under paraphrase, fertility reduction
   - Ablations: no pre-tokenizer, no constraint classifier, no quantifier normalization
6. Related Work
   - Multilingual tokenization: Sarvam, MorphTok, IndicSuperTokenizer
   - Semantic parsing: AMR, DRS, text-to-SQL
   - NL to formal: autoformalization, DECLARATIVE, CP-LLMs-ICL, HERMES
   - Math word problem solving: seq2seq, graph-based, LLM-based
7. Discussion
   - What pre-tokenization cannot fix (problems without clean subdomain membership)
   - Connection to verified reasoning (teaser for Paper 2)
8. Conclusion
```

### Key Figures

- **Figure 1**: The analogy diagram. Side-by-side: Hindi word → BPE fragments → meaning loss | English problem → LLM tokens → constraint loss. Visual.
- **Figure 2**: Fertility distribution across datasets, colored by LLM success/failure.
- **Figure 3**: Pre-tokenization pipeline architecture.
- **Figure 4**: Worked example — one problem through the full pipeline, showing fertility at each stage.
- **Table 1**: Solve rates across methods × datasets.
- **Table 2**: Ablation results.

---

## Paper 2: "Verified Reasoning via Compilation"

**Working title**: *Verified Reasoning via Compilation: A Formal Language and Runtime for Natural Language Constraint Problems*

**Core claim**: A compile-check-repair loop (NL → FRL → solver → certificate → explanation) outperforms one-shot LLM reasoning in correctness, robustness, and explanation faithfulness.

**Target venues**: NeurIPS, ICLR, AAAI

*(This is the system from your thesis doc. Paper 1's pre-tokenizer becomes the front-end.)*

---

## Phases

### Phase 0: Foundation (Week 1-2)

**Goal**: Get the measurement infrastructure working so you can compute formalization fertility.

#### 0.1 Dataset collection and annotation
- [ ] Download and prepare: GSM8K, MATH (algebra subset), logic grid puzzles (from CP-LLMs-ICL paper), NL4Opt
- [ ] For each dataset, obtain or create gold formal representations (equations, constraints, FRL-equivalent)
- [ ] Write a script to count: NL tokens (using tiktoken/sentencepiece), formal constraints, entities, and relations per problem

#### 0.2 Fertility measurement
- [ ] Define formalization fertility precisely:
  - `fertility = NL_tokens / formal_constraints` (basic)
  - `entity_fertility = NL_tokens / entities_extracted`
  - `constraint_density = constraints / sentences`
- [ ] Compute across all datasets
- [ ] Run baseline LLMs (GPT-4, Claude, open-weight model) on each problem, record success/failure
- [ ] Statistical analysis: correlation between fertility and failure rate

#### 0.3 AMR/DRS baseline
- [ ] Set up amrlib (Python, spaCy integration) — parse all problems to AMR graphs
- [ ] Set up DRS parser (Parallel Meaning Bank tools) — parse a subset
- [ ] Measure: do AMR/DRS nodes correspond to FRL entities/constraints? How lossy is the mapping?

**Deliverable**: A notebook/report with fertility statistics and correlation plots. This becomes Section 2-3 of Paper 1.

---

### Phase 1: Backend (Week 2-4)

**Goal**: Build the solver backend that both papers need.

#### 1.1 Z3 runner with tracked constraints
- [ ] Python wrapper around Z3 that:
  - Accepts typed FRL (JSON schema)
  - Compiles FRL → SMT-LIB (or Z3 Python API directly)
  - Returns: SAT model (witness) or UNSAT core
  - Tracks constraint provenance (which NL span → which constraint)
- [ ] Independent verification: re-check witness against FRL constraints

#### 1.2 FRL v0 schema
- [ ] Define JSON schema:
  ```
  sorts: Enum, Int, Real, Bool
  vars: name → sort
  constraints: list of {expr, provenance: {sentence_index, span, original_text}}
  query: SAT | OPT(minimize/maximize expr)
  report: list of var names to output
  ```
- [ ] Typechecker: validate FRL before compilation
- [ ] Canonicalization: sort constraints, normalize variable names

#### 1.3 Synthetic data generator v0
- [ ] Assignment puzzle generator:
  - Random entities (people, tasks, colors, days)
  - Random constraints (forbidden pairs, exactly-one, if-then)
  - Ensure SAT (solve, verify, keep only solvable instances)
  - Template NL rendering
- [ ] Output: `{nl_text, frl_gold, witness, provenance_map}`
- [ ] Generate 10k instances for initial experiments

**Deliverable**: A working `nl_text → [manual FRL] → Z3 → witness` pipeline. The synthetic generator provides unlimited training/eval data.

---

### Phase 2: Constraint Pre-Tokenizer (Week 4-7)

**Goal**: Build the novel component for Paper 1.

#### 2.1 Entity extractor
- [ ] Use AMR parser output + NER to identify problem entities
- [ ] Map AMR nodes to FRL entity declarations
- [ ] Evaluate: entity extraction F1 on synthetic data

#### 2.2 Constraint type classifier
- [ ] Define constraint taxonomy:
  - `EXCLUSION` ("cannot", "must not", "is not allowed")
  - `ASSIGNMENT` ("must do", "is assigned to", "gets")
  - `UNIQUENESS` ("each ... different", "no two ... same")
  - `CONDITIONAL` ("if ... then", "only if", "whenever")
  - `CARDINALITY` ("at least N", "at most N", "exactly N")
  - `OBJECTIVE` ("minimize", "maximize", "find")
  - `BACKGROUND` (distractor / scene-setting)
- [ ] Train on synthetic data (you have gold labels from the generator)
- [ ] Model options (in order of complexity):
  1. Rule-based (regex + dependency parse) — baseline
  2. Fine-tuned span classifier (BERT/DeBERTa on synthetic data)
  3. LLM structured extraction with JSON schema

#### 2.3 Quantifier normalizer
- [ ] Map NL quantifier phrases to formal operators:
  - "at least N" → `≥ N`
  - "no more than" → `≤`
  - "exactly" → `==`
  - "not ... both" → cardinality constraint `≤ 1`
  - "either ... or" → disjunction
- [ ] Handle negation scope (DRS helps here)
- [ ] Evaluate: quantifier extraction accuracy on synthetic + real data

#### 2.4 Assembled pre-tokenizer pipeline
- [ ] Chain: raw NL → AMR parse → entity extraction → constraint classification → quantifier normalization → structured IR (close to FRL)
- [ ] Measure fertility *before and after* pre-tokenization
- [ ] Compare: pre-tokenized IR → FRL (should be much easier than raw NL → FRL)

**Deliverable**: A working pre-tokenizer that reduces formalization fertility measurably. This is the method section of Paper 1.

---

### Phase 3: End-to-End Experiments (Week 7-10)

**Goal**: Run the experiments for Paper 1.

#### 3.1 Full pipeline
- [ ] System: NL → pre-tokenizer → LLM/seq2seq → FRL → Z3 → witness/certificate
- [ ] With K candidates + verifier-driven repair (try up to K=10 formalizations)

#### 3.2 Baselines
- [ ] One-shot LLM answer (GPT-4, Claude, Llama-3)
- [ ] Chain-of-Thought (CoT)
- [ ] Program-Aided Language model (PAL)
- [ ] DECLARATIVE (equations + sympy)
- [ ] LLM → Z3 directly (no FRL, no pre-tokenizer)
- [ ] Rule-based semantic parser (for synthetic language subset)

#### 3.3 Evaluation
- [ ] Metrics:
  - Verified solve rate (solve@1, solve@K)
  - Compilation accuracy (exact match + equivalence via solver)
  - Robustness under paraphrase
  - Robustness under distractors (add irrelevant sentences)
  - Fertility reduction (before/after pre-tokenization)
- [ ] Ablations:
  - No pre-tokenizer (raw NL → FRL)
  - No constraint classifier (entities only)
  - No quantifier normalizer
  - No verifier feedback (K=1, no repair)
  - No provenance tracking

#### 3.4 Analysis
- [ ] Error categorization: where does each component fail?
- [ ] Fertility-failure correlation with and without pre-tokenization
- [ ] Case studies: 3-5 worked examples showing the pipeline

**Deliverable**: All experimental results for Paper 1. Write up results + analysis sections.

---

### Phase 4: Paper 1 Writing (Week 10-12)

#### 4.1 Draft
- [ ] Write all sections per outline above
- [ ] Create all figures and tables
- [ ] Related work: cite Sarvam-1, MorphTok, AMR, DRS, DECLARATIVE, CP-LLMs-ICL, HERMES, autoformalization papers

#### 4.2 Internal review
- [ ] Self-review: does the fertility claim hold up empirically?
- [ ] Check: is the Sarvam analogy earning its keep or just a metaphor?
- [ ] Tighten novelty claim: what exactly is new vs. semantic parsing?

#### 4.3 Submit
- [ ] Target: ACL/EMNLP rolling review, or workshop (ICML TokShop if timing works)

---

### Phase 5: Runtime + Explanations — Paper 2 (Week 8-16, overlapping)

**Goal**: Build the full verified reasoning system. Starts during Phase 3.

#### 5.1 Formulation-graph search
- [ ] Implement best-first search over candidate formalizations
- [ ] Nodes = (FRL + assumptions + provenance + backend)
- [ ] Edges = refine/add/remove constraints, switch backend, ASK for implicit constraints
- [ ] Cost = solver calls + tokens + user questions

#### 5.2 Constraint acquisition (ASK step)
- [ ] Multi-model detection: if multiple witnesses exist, identify which constraint is underspecified
- [ ] Generate minimal clarifying question
- [ ] Value-of-information heuristic: only ask if it's worth it

#### 5.3 Explanation IR (EIR) + checker
- [ ] Deterministic EIR generation from witness + constraint provenance
- [ ] Step types: FROM_CONSTRAINT, ELIMINATE, DEDUCE_SINGLETON, APPLY_ALLDIFF, CONCLUDE
- [ ] Step checker: each step verified against FRL + witness
- [ ] English renderer: EIR → human-readable explanation

#### 5.4 Training data (expanded)
- [ ] Scale synthetic generator to 50k-500k instances
- [ ] Add paraphrase augmentation (LLM-based paraphrasing of templates)
- [ ] Add distractor noise
- [ ] Curriculum: start with unary constraints, add disjunction, implication, numeric

#### 5.5 NL → FRL model
- [ ] Baseline ladder:
  1. Rule/template parser (validates pipeline)
  2. T5/seq2seq fine-tuned on synthetic data
  3. LLM structured output (JSON schema + repair loop)
  4. Two-stage: pre-tokenizer extractions → deterministic FRL assembler
- [ ] Train and evaluate each rung

#### 5.6 Paper 2 experiments
- [ ] Full system vs. baselines (including Paper 1 system as an ablation)
- [ ] Metrics: solve@K, robustness, explanation faithfulness (EIR checker pass %), backtracking efficiency
- [ ] Ablations: no search, no ASK, no EIR checker, no provenance

**Deliverable**: Paper 2 draft.

---

## Dependency Graph

```
Phase 0 (measurement)
  ├─→ Paper 1, Sections 2-3 (fertility analysis)
  └─→ Phase 1 (backend) ─→ Phase 2 (pre-tokenizer) ─→ Phase 3 (experiments) ─→ Phase 4 (write Paper 1)
                           └─→ Phase 5 (runtime + explanations, Paper 2)
```

Paper 1 needs: Phase 0 + Phase 1 (partial) + Phase 2 + Phase 3.
Paper 2 needs: everything in Paper 1 + Phase 5.

---

## Key Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fertility doesn't correlate with LLM failure | Kills Paper 1's thesis | Measure early (Phase 0). If weak, pivot to "compilation accuracy" framing instead of fertility |
| AMR/DRS parsers too inaccurate on problem text | Pre-tokenizer doesn't help | Fall back to LLM-based extraction (option 2.2.3). AMR is a starting point, not required |
| Synthetic data doesn't transfer to real problems | Experiments look artificial | Include real benchmarks (GSM8K, logic grids) alongside synthetic. Even partial transfer is publishable |
| Pre-tokenizer adds latency but not accuracy | System is slower with no benefit | Measure carefully. If accuracy doesn't improve, the fertility *diagnosis* is still a paper — just not the system |
| Sarvam analogy is seen as "just a metaphor" | Reviewers dismiss framing | Ground it empirically. The analogy motivates the metric; the metric must stand on its own data |

---

## Tools and Infrastructure

### Required
- Python 3.10+, Z3 (pip install z3-solver)
- amrlib (pip install amrlib) + spaCy
- tiktoken or sentencepiece (for token counting)
- Standard ML: torch, transformers, datasets

### Datasets
- GSM8K: https://github.com/openai/grade-school-math
- MATH: https://github.com/hendrycks/math
- NL4Opt: https://nl4opt.github.io/
- Logic grid puzzles: from CP-LLMs-ICL paper (Michailidis et al., CP 2024)
- Synthetic: self-generated

### Models (for baselines and extraction)
- GPT-4 / Claude API (baselines + paraphrase generation)
- Open-weight: Llama-3, Mistral (for reproducible baselines)
- T5-base or T5-large (for seq2seq FRL generation)
- DeBERTa-v3 (for constraint type classifier)

---

## What to Do Monday

1. **Set up the measurement pipeline** (Phase 0.1-0.2). Download GSM8K. Write a script to count tokens per problem and manually annotate 50 problems with their formal constraints. Compute fertility. This takes one day and tells you immediately whether the core thesis holds.

2. **Run AMR on those 50 problems** (Phase 0.3). See if AMR nodes map to entities/constraints. This takes an hour and tells you whether the pre-tokenizer idea is viable.

3. **If fertility correlates with failure**: you have a paper. Proceed to Phase 1.
4. **If it doesn't**: the FRL+runtime thesis (Paper 2) still holds. Drop the fertility framing and lead with verified compilation directly.

---

## Success Criteria

### Paper 1 is done when:
- Fertility is defined, measured, and correlated with failure across ≥2 datasets
- Pre-tokenizer demonstrably reduces fertility
- System (pre-tokenizer + FRL + solver) beats one-shot LLM on at least one dataset
- Paper is written and submitted

### Paper 2 is done when:
- Full pipeline (NL → FRL → solver → certificate → EIR → explanation) works end-to-end
- Formulation-graph search with backtracking improves over single-shot compilation
- Explanation faithfulness is verified (EIR checker pass rate >95%)
- Robustness under paraphrase/distractors is demonstrated
- Paper is written and submitted

### Thesis is done when:
- Both papers are accepted or under review
- System handles assignment puzzles + at least one additional domain (linear algebra or scheduling)
- Constraint acquisition (ASK step) is demonstrated
