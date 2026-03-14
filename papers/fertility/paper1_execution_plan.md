# Paper 1 Execution Plan: Formalization Fertility

**Working title:** Formalization Fertility: Why LLM Reasoning Fails at the Tokenization Boundary  
**Target venues:** ACL/EMNLP (main), ICML TokShop (workshop), NeurIPS (neuro-symbolic)

---

## Phase 0: Foundation (Days 1–3)

The goal here is to make the core idea concrete before writing any code. Everything downstream depends on getting the fertility definition right.

### Step 0.1 — Define formalization fertility precisely

Write a 1-page spec (`fertility_definition.md`) that answers:

- **What is a "constraint"?** You need a ground-truth unit. For this paper, a constraint is one atomic predicate in the FRL (e.g., `assign(Alice) != Weld`, `AllDifferent(...)`, `x + y <= 10`). Compound constraints (AND/OR) count their atomic children.
- **What are the "NL tokens"?** Use the tokenizer of the model you're evaluating (GPT-4's `cl100k_base`, Claude's tokenizer). You measure against the specific model's encoding.
- **The formula:** `fertility(problem, model) = NL_tokens(problem_text) / constraint_count(gold_FRL)`. Higher fertility = more tokens per constraint = harder for the model.
- **Edge cases:** What about problems with implicit constraints (e.g., non-negativity)? Count them — they're constraints the model must infer, which is exactly why they're hard. What about distractor sentences that add no constraints? They increase the numerator, which correctly signals higher difficulty.

**Deliverable:** `fertility_definition.md` — 1 page, with the formula, edge case decisions, and 3 worked examples.

### Step 0.2 — Draft Figure 4 (the worked example)

Before anything else, manually work through one problem end-to-end. Pick a medium-complexity logic grid puzzle (5 entities, ~8 constraints). Write out:

1. The original NL problem text
2. The BPE tokenization (show where tokens split constraint-bearing phrases)
3. The gold FRL (list of constraints with provenance to NL spans)
4. The fertility score
5. GPT-4/Claude's one-shot attempt (get the actual output — success or failure)
6. The pre-tokenized structured IR
7. The FRL after pre-tokenization
8. The solver result

This single example will expose every gap in your pipeline definition. If you can't do it by hand, you can't automate it.

**Deliverable:** A detailed worked example document with all 8 stages. This becomes Figure 4 in the paper.

### Step 0.3 — Set up the project repo

```
formalization-fertility/
├── data/
│   ├── raw/                  # downloaded datasets
│   ├── annotated/            # problems with gold FRL annotations
│   └── results/              # LLM outputs + fertility scores
├── src/
│   ├── fertility.py          # fertility computation
│   ├── tokenize_analysis.py  # BPE tokenization analysis
│   ├── frl_schema.py         # FRL data structures
│   ├── pretokenizer/         # constraint pre-tokenization pipeline
│   ├── solver/               # Z3 interface
│   └── eval/                 # evaluation scripts
├── notebooks/
│   ├── fertility_analysis.ipynb
│   └── figures.ipynb
├── paper/
│   └── main.tex
└── README.md
```

**Deliverable:** Repo initialized with directory structure and a `requirements.txt` (z3-solver, tiktoken, transformers, openai, anthropic, pandas, matplotlib, seaborn).

---

## Phase 1: Measure Fertility (Days 4–14)

This is the empirical core of the paper. You need to show that fertility predicts LLM failure. Everything else is motivated by this finding.

### Step 1.1 — Collect and prepare datasets

You need 3–4 datasets with different fertility profiles:

| Dataset | Expected fertility | Why include it |
|---------|-------------------|----------------|
| **GSM8K** (subset, ~200) | Low–medium | Well-known, LLMs do well → low fertility should correlate with high success |
| **Logic grid puzzles** (~100) | Medium–high | Multiple interacting constraints, implicit uniqueness assumptions |
| **NL4Opt** (~50–100) | High | Optimization problems with many constraints embedded in paragraphs |
| **FOLIO** (~50) | Variable | First-order logic, good for diversity |

For each dataset:
- Download raw problems
- Manually annotate 50 problems from each with gold FRL (this is the most labor-intensive step — budget 2–3 days)
- For the remaining problems, use an LLM to draft FRL annotations, then spot-check

**Key decision:** You don't need to annotate everything. 50 problems × 4 datasets = 200 annotated problems is enough for a strong correlation analysis. The rest can use approximate fertility (NL tokens / estimated constraint count from regex patterns or LLM extraction).

**Deliverable:** `data/annotated/` with 200 problems, each having: NL text, gold FRL, constraint count, provenance spans.

### Step 1.2 — Compute fertility scores

Write `src/fertility.py`:

```python
def compute_fertility(problem_text: str, gold_frl: FRL, tokenizer: str) -> float:
    """NL tokens / constraint count"""
    token_count = len(encode(problem_text, tokenizer))
    constraint_count = count_atomic_constraints(gold_frl)
    return token_count / constraint_count
```

Run this across all 200 annotated problems. Also compute:
- **Per-constraint fertility:** for each constraint, how many NL tokens encode it? (Some constraints are stated in 3 tokens, others in 30.)
- **Implicit constraint ratio:** what fraction of constraints have no explicit NL span? (These are the "sandhi" equivalent.)

**Deliverable:** A CSV with columns: `dataset, problem_id, nl_tokens, constraint_count, fertility, implicit_ratio`.

### Step 1.3 — Collect LLM baseline results

Run each of the 200 problems through:
- GPT-4 (one-shot, zero-shot)
- Claude Sonnet (one-shot, zero-shot)
- GPT-4 with CoT prompting
- (Optional) GPT-4 with PAL (program-aided language model)

For each, record:
- Whether the final answer is correct (binary)
- The generated reasoning trace (for error analysis later)
- Token count of the response

**Important:** Use the exact same prompt template for all problems within a dataset. Don't cherry-pick prompts.

**Deliverable:** `data/results/` with LLM outputs. Updated CSV with `correct_gpt4, correct_claude, correct_cot` columns.

### Step 1.4 — The key analysis: fertility ↔ failure correlation

This is Figure 2 and the central empirical claim. In `notebooks/fertility_analysis.ipynb`:

1. **Scatter plot:** fertility (x) vs. LLM accuracy (y), colored by dataset. If the correlation is real, you should see accuracy drop as fertility increases.
2. **Statistical test:** logistic regression of `correct ~ fertility + dataset`. Report odds ratio and p-value.
3. **Threshold analysis:** is there a fertility threshold above which LLMs reliably fail? (e.g., fertility > 15 → accuracy < 30%)
4. **Control for problem difficulty:** fertility might just correlate with "harder problems." Add controls: constraint count alone, NL length alone, number of entities. Show that fertility (the ratio) predicts failure *better* than either numerator or denominator alone.
5. **Per-constraint analysis:** which constraint types have highest fertility? (Implicit constraints, quantifier-heavy constraints, multi-hop constraints.)

**Go/no-go decision:** If the fertility–failure correlation is weak (r < 0.3 or p > 0.05), stop and refine the fertility definition before proceeding. The paper lives or dies on this plot.

**Deliverable:** Figure 2, correlation statistics, and a 1-paragraph summary of the finding.

---

## Phase 2: Build the Pre-Tokenizer (Days 15–25)

Now that you've shown fertility predicts failure, you build something that reduces fertility and show it helps.

### Step 2.1 — Design the constraint pre-tokenization pipeline

Based on your thesis discussion, the architecture is:

```
NL text
  → Entity/type extraction (NER-like)
  → Constraint relation extraction (classify constraint tuples)
  → Quantifier normalization ("at least 3" → ≥3, "no more than" → ≤)
  → Structured IR (JSON fact graph)
```

**Key design decision from my earlier feedback:** Skip AMR. It's a heavy dependency that introduces its own errors and isn't designed for constraint extraction. Instead, build a lighter-weight multi-head extractor:

- **Entity head:** extract entity sets and their types (people, tasks, days, numbers)
- **Relation head:** extract constraint tuples (FORBID, REQUIRE, ALLDIFF, IMPLIES, GEQ, LEQ, EQ)
- **Query head:** what's being asked (find assignment, count solutions, optimize)

### Step 2.2 — Implement the extractor (two options)

**Option A — LLM-based (faster to prototype, publishable):**

Prompt GPT-4/Claude with a structured output schema:

```json
{
  "entities": [{"name": "Alice", "type": "Person"}, ...],
  "variables": [{"name": "assign", "type": "Func(Person, Task)"}],
  "constraints": [
    {"type": "FORBID", "expr": "assign(Alice) != Weld", "source_span": "Alice cannot weld"},
    {"type": "ALLDIFF", "expr": "AllDifferent(assign(*))", "source_span": "each person does exactly one task"}
  ],
  "query": {"type": "SAT", "report": ["assign(Alice)", "assign(Bob)", "assign(Cara)"]}
}
```

Test this on your 200 annotated problems. Measure extraction accuracy vs. gold FRL.

**Option B — Trained model (stronger for the paper but slower):**

Fine-tune a smaller model (Flan-T5 or similar) on synthetic data:
1. Generate 10k synthetic constraint problems with gold FRL
2. Render to NL via templates + paraphrase
3. Train text → structured IR
4. Evaluate on held-out synthetic + your 200 real problems

For Paper 1, Option A is sufficient and faster. Option B is better if you have time and want a stronger contribution.

### Step 2.3 — Implement quantifier normalization

This is a focused module that catches a common failure mode:

| NL phrase | Normalized form |
|-----------|----------------|
| "at least 3" | ≥ 3 |
| "no more than 5" | ≤ 5 |
| "exactly one" | = 1 |
| "not fewer than" | ≥ |
| "at most" | ≤ |
| "cannot" / "must not" / "is prohibited from" | FORBID |
| "if ... then ..." | IMPLIES |
| "either ... or ..." (exclusive) | XOR |
| "... or ..." (inclusive) | OR |

Build a small rule-based normalizer + LLM fallback for ambiguous cases.

### Step 2.4 — Assemble: structured IR → FRL → solver

This is mostly plumbing from your thesis work:

1. **Structured IR → FRL:** Deterministic compilation. Map entity types to Z3 sorts, constraints to Z3 assertions.
2. **FRL → Z3:** Use tracked assertions so you can extract UNSAT cores if needed.
3. **Z3 → witness:** Extract model, format as answer.

**Deliverable:** An end-to-end pipeline: `NL text → pre-tokenizer → FRL → Z3 → answer`.

### Step 2.5 — Measure fertility reduction

Re-compute fertility on the structured IR output vs. the original NL:

- `fertility_original = NL_tokens / constraint_count`
- `fertility_pretokenized = IR_tokens / constraint_count`

The IR should be much more compact per constraint. Show this reduction across all 200 problems.

**Deliverable:** Figure showing fertility distributions before/after pre-tokenization.

---

## Phase 3: Experiments (Days 26–35)

### Step 3.1 — Define baselines and your system

| Method | Description |
|--------|-------------|
| **One-shot LLM** | Direct GPT-4/Claude answer (already collected in Phase 1) |
| **CoT LLM** | Chain-of-thought prompting (already collected) |
| **PAL** | LLM generates Python code to solve |
| **LLM → structured output** | LLM prompted to output JSON constraints directly (no pre-tokenizer) |
| **DECLARATIVE** | If available — Ye et al.'s approach |
| **Your system** | Pre-tokenizer → FRL → Z3 → answer |

The critical comparison is **your system vs. "LLM → structured output"** — this isolates whether the pre-tokenizer adds value beyond just asking the LLM for structured output.

### Step 3.2 — Run experiments

For each method × each of the 200 problems, record:
- Correct/incorrect (binary)
- If your system: fertility reduction achieved
- If your system: which pipeline stage failed (extraction error, constraint error, solver timeout)

### Step 3.3 — Robustness under paraphrase

This is where formalization-based approaches should shine:

1. Take 50 problems where baseline LLMs succeed
2. Paraphrase each 3 ways: (a) reorder sentences, (b) add distractor sentences, (c) rephrase quantifiers
3. Re-run all methods
4. Report: % of methods that stay correct under paraphrase

**Hypothesis:** One-shot LLMs will degrade; your system will be robust because the pre-tokenizer normalizes away surface variation.

### Step 3.4 — Ablation study

| Ablation | What you remove |
|----------|----------------|
| No pre-tokenizer | LLM generates FRL directly from NL |
| No constraint classifier | Pre-tokenizer extracts entities but doesn't classify constraint types |
| No quantifier normalization | Skip the normalization step |
| No solver (LLM solves from IR) | Pre-tokenize but let LLM reason over the structured IR instead of using Z3 |

**Deliverable:** Table 1 (solve rates) and Table 2 (ablations).

---

## Phase 4: Write the Paper (Days 36–45)

### Step 4.1 — Produce all figures first

Before writing prose, generate final versions of:

- **Figure 1:** The analogy diagram (Hindi BPE ↔ NL constraint tokenization). Make this in a drawing tool or TikZ. Side-by-side: a Hindi word fragmented by BPE with meaning loss, and an English constraint sentence fragmented by BPE with constraint loss.
- **Figure 2:** Fertility vs. LLM accuracy scatter plot (from Phase 1).
- **Figure 3:** Pipeline architecture diagram.
- **Figure 4:** Worked example end-to-end (from Phase 0).
- **Table 1:** Solve rates across methods × datasets.
- **Table 2:** Ablation results.

### Step 4.2 — Write sections in this order

1. **§5 Experiments** — Write this first. It forces you to be precise about what you measured.
2. **§3 Empirical Analysis** — The fertility correlation finding. This is your main result.
3. **§2 Formalization Fertility** — The definition and metric. Keep it tight — 1.5 pages max.
4. **§4 Constraint Pre-Tokenization** — The architecture. Focus on what's novel vs. standard semantic parsing.
5. **§1 Introduction** — Write this second-to-last. Lead with the finding, bring in the analogy, state the thesis.
6. **§7 Discussion** — What pre-tokenization can't fix, connection to Paper 2.
7. **§6 Related Work** — Three streams: multilingual tokenization, semantic parsing, NL-to-formal.
8. **Abstract** — Write this dead last. 250 words. Finding → metric → method → result.

### Step 4.3 — Key writing decisions

- **Tone the core claim:** Say "a significant and underappreciated failure mode" not "the primary failure mode." The correlation supports significance; exclusivity would require ruling out all alternatives.
- **Scope this paper clearly:** This paper is about *diagnosing* the fertility problem and showing pre-tokenization helps. It is NOT about the full verified reasoning stack (that's Paper 2). Be explicit in §7 about what comes next.
- **The Sarvam analogy:** Give it ~1 paragraph in the intro and the analogy table in §2. Don't let it dominate. The empirical finding is the contribution, not the analogy.

---

## Decision Points & Risks

| Risk | Detection | Mitigation |
|------|-----------|------------|
| Fertility–failure correlation is weak | Phase 1, Step 1.4 | Refine the fertility definition (per-constraint vs. global), try different tokenizers, add more datasets |
| Pre-tokenizer doesn't improve over "LLM → structured output" prompting | Phase 3, Step 3.1 | Focus the paper on the diagnostic finding (fertility as metric) rather than the system. The metric alone is a contribution. |
| Gold FRL annotation is too subjective | Phase 1, Step 1.1 | Annotate 30 problems with 2 annotators, compute inter-annotator agreement on constraint count |
| AMR/heavy NLP pipeline introduces too many errors | Phase 2, Step 2.1 | Already mitigated — we're using a lighter-weight approach, not AMR |

---

## Timeline Summary

| Phase | Days | Key deliverable |
|-------|------|----------------|
| 0: Foundation | 1–3 | Fertility definition, worked example, repo |
| 1: Measure fertility | 4–14 | 200 annotated problems, fertility–failure correlation, Figure 2 |
| 2: Build pre-tokenizer | 15–25 | Working pipeline: NL → structured IR → FRL → Z3 → answer |
| 3: Experiments | 26–35 | Tables 1 & 2, robustness results, ablations |
| 4: Write paper | 36–45 | Complete draft ready for internal review |

**Total: ~6–7 weeks to a submittable draft.**

---

## What to Do Today

1. Write `fertility_definition.md` (30 min)
2. Pick one logic grid puzzle and do the full worked example by hand (1–2 hours)
3. Set up the repo and install dependencies (30 min)
4. Start downloading GSM8K and hunting for logic grid puzzle datasets (30 min)

That's your Day 1. By end of day you should have a concrete, grounded understanding of whether the fertility metric captures something real, just from the single worked example.
