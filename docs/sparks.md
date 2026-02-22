# Sparks

A running log of ideas and key decisions for the "reasoning-as-compilation" direction.

---

## Core thesis

Reasoning can be made reliable by treating it as **compilation**. The full pipeline:

```
NL problem text
  │
  ▼
(1) DOMAIN ROUTER — LLM/SLM classifies: "what kind of problem is this?"
    Output: ranked domain candidates (scheduling, algebra, logic, optimization...)
  │
  ▼
(2) MULTI-VIEW ANALYSIS — independent, queryable views of the text
    AMR parser → semantic graph
    NER → entities and types
    Constraint detector → span tags
    Quantifier normalizer → standardized quantities
    Conditional extractor → cause-effect trees
    (Each view runs independently. Errors don't cascade.)
  │
  ▼
(3) ASSEMBLER — queries views, cross-references, builds structured IR
    Like a compiler querying lexer + symbol table + type env
    Disagreement between views = signal, not error
  │
  ▼
(4) DOMAIN-SPECIFIC FRL COMPILER — structured IR → typed FRL with provenance
    Uses existing formal languages (Z3/SMT-LIB, MiniZinc, sympy, AMPL, Lean...)
    No universal IR needed — the domain choice IS the latent variable
  │
  ▼
(5) SOLVER + VERIFIER — Z3/MiniZinc/sympy/Gurobi/Lean → certificate
    Certificate = satisfying model, UNSAT core, optimality proof
    Independently checkable in polynomial time
  │
  ▼
(6) FAITHFUL EXPLANATION — EIR derived from certificate + constraint provenance
    Every explanation step is machine-checkable
    Faithful by construction, not by hope

LOOPS:
  Inner: compile-check-repair within a domain (structured error → fix → re-solve)
  Outer: try different domain if solver fails (CHANGE_DOMAIN edge in formulation graph)
  ASK:   detect underspecification → request minimal clarifying info
```

**Core claim**: For a broad class of reasoning tasks, the hardest part is semantic compilation (steps 1-4). Once formalized, classical computation produces correct answers with small token budgets and strong guarantees. Reliability comes from the compile-check-repair loop, not from scaling up language models.

**Why this matters**: Current LLM reasoning is brittle under paraphrase, distractors, and missing implicit assumptions. A verified compilation stack replaces persuasive narratives with checkable artifacts: the answer has a certificate, the explanation is grounded in the certificate, and failures are diagnosable and repairable.

---

## Key insights captured

- **Classical computation is strong at formal reasoning**: once a task is in a precise representation (logic/circuits/constraints/programs), deterministic search/backtracking and verification work extremely well.

- **Therefore the bottleneck is semantic compilation**: NL → FRL (handling ambiguity/implicit assumptions). Steps 1-4 above are where intelligence lives.

- **Domain classification IS the latent variable**: the recurring pull toward diffusion/latent spaces was pointing at a real question ("where does the IR come from?"). The answer: you don't learn a universal IR, you classify into an existing domain-specific formal language. The discrete domain choice replaces the elusive continuous latent space.

- **Multi-view assembly, not pipeline**: run all NLP analyses independently (AMR, NER, constraint detection, quantifiers), each producing its own queryable view. The assembler cross-references views to build FRL — like a compiler querying lexer, symbol table, and type environment. Errors in one view don't cascade. Disagreements are informative.

- **NL → FRL should be a compile-check-repair loop**, not a one-shot translation: propose → typecheck/solve/verify → structured errors/cores → repair. Two levels: inner loop (refine within domain), outer loop (try different domain).

- **Formalization fertility predicts failure**: NL tokens per formal constraint. High fertility = hard to formalize = LLM likely to fail. Analogous to BPE fertility in multilingual tokenization (Sarvam AI). Measurable, testable, publishable as a diagnostic.

- **Constraints are objects**: constraint extraction maps structurally to object detection in vision. DETR-style set prediction, anchor boxes as constraint templates, FPN for multi-scale constraints, NMS via solver equivalence checking. Nobody has made this connection.

- **Text-to-SQL is the closest existing work**: schema linking is the most important predictor of text-to-SQL success. Our multi-view assembly IS schema linking, generalized to problems where the schema must be inferred from text. Our formal verification is stronger than SQL execution-based checking.

- **Missing implicit constraints** are a first-class runtime event: detect underspecification (multiple models, unbounded solutions, domain invariant violations), then trigger constraint acquisition via ASK step.

- **Faithful explanations by construction**: EIR (Explanation IR) derived from solver certificates + constraint provenance. Every step is checkable. Counterfactuals are exact (re-solve with modified constraints). This solves the XAI problem for reasoning — not by post-hoc analysis of a black box, but by making the computation transparent.

- **Toward AGI**: the persistent agent needs identity (memory, indexed experience, growing skill toolkit, metacognition). The LLM is a component, not the agent. Open-ended reasoning is tractable given a sufficiently large, well-indexed repository of structured reasoning traces. The internet already contains billions of these traces — LLMs can extract and structure them.

- **"Why" questions become tractable** when reframed as hypotheses + constraints, with the runtime either selecting a consistent hypothesis or returning the minimal extra observation needed to decide.

---

## The Tokenization Insight (NEW — Feb 2026)

### Formalization Fertility: the Sarvam analogy

**Core observation**: The NL→FRL compilation problem is structurally analogous to the multilingual tokenization problem that Sarvam AI / MorphTok solved for Indic languages.

- **Sarvam's problem**: Standard BPE tokenizers shred Hindi words into 4-8 meaningless subword pieces (vs. 1-2 for English), destroying morphological units and degrading downstream performance. Fix: custom tokenizer respecting morphological boundaries, achieving fertility of 1.4-2.1 tokens/word.

- **Our problem**: Standard LLM processing shreds semantic-structural units in problem descriptions (entities, constraints, objectives, implicit assumptions). The model then spends capacity reconstructing meaning that was present in the original text but got fragmented. Fix: constraint pre-tokenization.

### The analogy table

| Sarvam / Indic tokenization | NL → FRL compilation |
|----------------------------|---------------------|
| Morpheme | Constraint / entity / relation |
| Sandhi (fusion of morphemes) | Implicit assumptions fused into natural phrasing |
| Dependent vowels (script artifacts) | Syntactic sugar ("at least," "no more than") |
| Fertility rate (tokens per word) | **Formalization fertility** (NL tokens per formal constraint) |
| MorphTok pre-tokenization | Constraint pre-tokenization |
| BPE shredding morphological units | LLM tokenization shredding semantic-structural units |

### Formalization fertility as a metric

- `fertility_basic = NL_tokens / num_constraints`
- `fertility_entity = NL_tokens / num_entities`
- `constraint_density = num_constraints / num_sentences`
- `implicit_ratio = implicit_constraints / total_constraints`

**Hypothesis**: High formalization fertility predicts LLM reasoning failure. This is testable.

### Constraint pre-tokenizer pipeline

1. **Entity extraction** (AMR nodes + NER)
2. **Constraint type classification** (EXCLUSION, CONDITIONAL, CARDINALITY, UNIQUENESS, OBJECTIVE, BACKGROUND)
3. **Quantifier normalization** ("at least 3" → ≥3, "no more than" → ≤)
4. **Implicit constraint surfacing** (the hard part — detect unstated but implied constraints)

### This is a paper by itself

**Working title**: *"Formalization Fertility: Why LLM Reasoning Fails at the Tokenization Boundary"*

Contributions: (1) formalization fertility as a metric, (2) empirical diagnosis showing fertility predicts failure, (3) constraint pre-tokenization architecture, (4) demonstration that pre-tokenizer + FRL + solver beats one-shot LLM.

Paper 1 in the two-paper plan. Paper 2 is the full verified reasoning system.

---

## The Object Detection Insight (NEW — Feb 2026)

### Constraints are objects. Detection is the right paradigm.

**Key realization**: The constraint extraction problem maps structurally to object detection in computer vision. Nobody has made this connection explicitly.

### The structural mapping

| Computer Vision | NL → FRL |
|----------------|----------|
| Pixels | Tokens/characters |
| Edges/textures (early layers) | Keywords, phrases ("cannot," "at least," "each") |
| Parts (mid layers) | Constraint fragments ("Alice cannot weld" = entity + exclusion + entity) |
| Objects (high layers) | Complete constraints (full formal constraint with all arguments) |
| Detection (output) | Constraint extraction with provenance (what + where in text) |
| Bounding box | Text span (provenance linking) |
| Class label | Constraint type (EXCLUSION, CONDITIONAL, CARDINALITY...) |
| Scene understanding | Full FRL (all constraints + relationships) |

### Specific architectural ideas that transfer

1. **Anchor boxes → Constraint templates**: YOLO/Faster-RCNN use anchor boxes as priors over object location/shape. Equivalent: constraint templates ("ENTITY cannot VERB ENTITY" → EXCLUSION) serving as priors over constraint structure. The synthetic data generator already builds these.

2. **DETR set prediction → Constraint set prediction**: DETR's key insight is predicting a *set* of objects, not a sequence. A problem's constraints ARE a set — order doesn't matter, you need exactly the right number, no duplicates. A DETR-style architecture for constraint extraction would use learned "constraint queries" that each attend to one constraint in the text.

3. **Feature Pyramid Networks → Multi-scale constraint detection**: Some constraints are one phrase ("Alice can't weld"), others span multiple sentences (three sentences that together imply AllDifferent). FPN naturally handles objects at multiple scales; the constraint equivalent handles constraints at multiple textual spans.

4. **Non-maximum suppression → Constraint deduplication**: When a constraint is expressed redundantly, suppress duplicates. In our case, we can use the solver to check semantic equivalence — a stronger form of NMS.

### ConstraintDETR: a concrete architecture

```
Input:  NL text (tokenized)
Encoder: Transformer encoder over text tokens
Decoder: N learned "constraint queries" (like DETR's object queries)
         Each query cross-attends to the encoded text
Output per query:
  - constraint_type: softmax over {EXCLUSION, CONDITIONAL, CARDINALITY, UNIQUENESS, OBJECTIVE, NO_CONSTRAINT}
  - arguments: pointer/span heads over input text (which entities)
  - quantifier: {≥, ≤, ==, ≠} + value
  - confidence: scalar
Loss: Hungarian matching between predicted and gold constraint sets
```

### Why this hasn't been done

1. Vision and NLP-reasoning communities don't talk to each other
2. No training data existed — but our synthetic generator produces (text, constraint set with spans) pairs for free
3. The framing hasn't been articulated: "constraints are objects, detection is the paradigm"

### Strategic placement

- **Paper 1**: Use AMR + classifier pipeline (simpler, validates thesis). Note ConstraintDETR as future work.
- **Paper 3 (or Paper 2 extension)**: Build ConstraintDETR, show it replaces the entire pre-tokenizer pipeline with a single end-to-end model. Strong standalone contribution.
- **Possible CVPR/ICLR angle**: "What vision taught us about semantic parsing" — cross-pollination framing.

---

## Multi-View Semantic Assembly (NEW — Feb 2026)

### The compiler insight: don't chain, query

**Key realization**: The pre-tokenizer should NOT be a pipeline where AMR feeds into a classifier which feeds into a normalizer (errors cascade). Instead, run all analysis tools independently, each producing its own representation of the source text, and have an assembler that QUERIES these representations on demand — exactly like how a compiler builds an AST by querying the lexer, symbol table, type environment, and scope resolver as independent data structures.

### The compiler analogy, precisely

```
COMPILER                              NL → FRL
───────                               ───────
Source code = one artifact             NL text = one artifact

Lexer → token stream     (queryable)  AMR parser → semantic graph    (queryable)
Symbol table → decls     (queryable)  NER → entity annotations       (queryable)
Type environment → types (queryable)  CiRA → conditional structures  (queryable)
Scope stack → nesting    (queryable)  Kiziltan → constraint spans    (queryable)
                                      Dep parser → syntax trees      (queryable)
                                      Quantifier detector → patterns (queryable)

Parser QUERIES these subsystems        Assembler QUERIES these views
to build the AST incrementally         to build the FRL incrementally
```

No subsystem's output feeds into another subsystem. They are all independently computed views of the same source text. The assembler is the orchestrator that knows what questions to ask and when.

### Why this is fundamentally better than pipeline chaining

**Error independence**: If AMR misparses sentence 3 but CiRA correctly identifies it as a conditional, the assembler can still build the right constraint by querying CiRA for structure and NER for entities, bypassing the bad AMR parse. Each tool's errors are independent; the assembler cross-references to resolve ambiguity.

**Disagreement as signal**: When AMR says a sentence is a simple predicate but Kiziltan tags it as a constraint span, that disagreement is *information* — it tells the assembler this sentence needs more careful handling. In a pipeline, disagreement just means one tool overrides another.

**Representation fidelity**: AMR stays a graph (you traverse it), CiRA stays a tree (you query cause/effect), Kiziltan stays span annotations (you check membership). Nothing gets flattened into a token sequence or linearized into text.

### How the assembler builds the FRL

```
Step 1: Identify domain
  Query: NER → entity types, AMR → predicates
  Decision: assignment problem (people → tasks)

Step 2: Extract entity sets  
  Query: NER → names, AMR → concept nodes
  Cross-reference: NER says {Alice, Bob, Cara}, AMR agrees
  Decision: People = {Alice, Bob, Cara}, Tasks = {Weld, Paint, Pack}

Step 3: For each sentence, determine its role
  Query multiple views simultaneously:
    Kiziltan: is this a constraint span?
    CiRA: is this a conditional? what structure?
    AMR: what's the predicate-argument structure?
    Quantifier detector: any quantifier phrases?

  Example — "Alice cannot weld":
    Kiziltan: yes, constraint    | CiRA: not conditional
    AMR: (possible :pol - :ARG0 Alice :ARG1 weld)
    → EXCLUSION: assign(Alice) ≠ Weld

  Example — "If Bob welds, then Cara paints":
    Kiziltan: yes, constraint    | CiRA: conditional (cause→effect)
    AMR: two linked propositions
    → CONDITIONAL: assign(Bob)=Weld → assign(Cara)=Paint

  Example — "Everyone has a different task":
    Kiziltan: yes, constraint    | Quantifier: "everyone" = universal
    AMR: (have :ARG0 everyone :ARG1 (task :mod different))
    → UNIQUENESS: AllDifferent(assignments)

Step 4: Check for implicit constraints
  Query: NER → |People|=3, |Tasks|=3
  Query: existing constraints → no explicit bijection stated
  Decision: likely implicit bijection → flag for ASK step

Step 5: Assemble typed FRL from all decisions
```

### What the assembler IS, architecturally

The assembler can be implemented as:

**Option A — LLM with tool-use**: Each "tool" is a query against a pre-computed representation. The LLM decides what to query, gets structured results, makes decisions. This is an agent loop where tools are pre-computed linguistic analyses, not external APIs.

**Option B — Cross-attention over heterogeneous representations**: For each decision the assembler needs to make, a query vector cross-attends over multiple source representations (AMR subgraph, CiRA tree, NER entities, Kiziltan tags, quantifier features). Each source is encoded in its native form. The fused evidence vector feeds a classification head.

**Option C — ConstraintDETR on multi-view input**: DETR-style constraint queries, but instead of attending over raw text, they attend over the multi-view representations. Combines the object detection insight with the multi-view assembly insight.

### Honest assessment of pre-tokenizer + small model vs big LLM

The claim "pre-tokenizer + small model beats big LLM" is probably wrong on clean inputs. Modern LLMs likely perform implicit pre-tokenization internally — GPT-4's attention heads are doing something functionally similar to AMR parsing. The pre-tokenizer's real value is:

1. **Robustness, not peak accuracy**: The multi-view assembly is more invariant to surface perturbations (paraphrase, reorder, distractors) because it extracts structure before surface variation hits. The testable claim: smaller robustness gap under perturbation.

2. **Diagnosability**: When the system fails, you can see exactly which view was wrong and which decision was affected. This enables targeted repair. A failed LLM just gives you wrong output.

3. **Composability with verification**: The assembler's decisions have provenance (which view provided the evidence). When the solver returns UNSAT, you can trace back through the assembler's decisions to find which constraint was wrong and which view misled the assembler.

4. **Data efficiency**: A small model trained on pre-tokenized multi-view input may match a large LLM with less training data, because the views do much of the feature engineering.

5. **The measurement contribution stands regardless**: Even if the multi-view assembly doesn't improve accuracy, the formalization fertility metric and the correlation with failure is publishable as a diagnostic tool.

### Why this is architecturally novel

No existing NLP system treats multiple semantic analyses as independently queryable databases that an assembler cross-references to build a formal representation. Existing approaches either:
- **Chain tools in a pipeline** (errors cascade, no recovery)
- **Feed everything to one big model** (no interpretability, no robustness guarantee)
- **Ensemble outputs** (vote/average, but don't query structurally)

Multi-view semantic assembly is a third paradigm: independent views, structured queries, incremental assembly with cross-referencing. This may be the core architectural contribution of Paper 1.

### Related prior art to position against

- **Multi-view learning** (Xu et al., 2013): learns from multiple feature sets but typically for classification, not structured output assembly
- **Mixture of experts**: routes inputs to different experts but doesn't query multiple experts per decision
- **Retrieval-augmented generation**: retrieves from a single knowledge source, not multiple heterogeneous structured views
- **Compiler architecture**: the closest analogy, but applied to formal languages, not NL

---

## Existing Work on Constraint/Conditional Extraction (Literature — Feb 2026)

### Three communities, barely citing each other

1. **Requirements Engineering — CiRA** (Fischbach et al., 2020–2023): Detects conditionals in requirements, extracts fine-grained cause-effect trees using Recursive Neural Tensor Networks. CATE tool achieves ~74% F1. Generates test cases automatically (71.8% coverage). Limitation: no constraint type classification, no quantifiers, software requirements domain only.

2. **Constraint Programming — Kiziltan, Lippi, Torroni (IJCAI 2016)**: "Constraint Detection in Natural Language Problem Descriptions." SVM-HMM sequence labeler, binary classification (constraint span vs. not). 110 annotated CP problem descriptions. Works well on known problem types. Limitation: span detection only, no structure extraction.

3. **Optimization NLP — NL4Opt** (NeurIPS 2022 Competition): Entity extraction for LP problems (constraint direction, limit, objective, parameters, variables). OptiMUS (2024) adds modular state: parameters, objective, background, constraints. Limitation: linear programming only, LLM-based.

### Also relevant
- **LexNLP** (LexPredict): regex-based extraction of conditionals and constraints from legal text
- **NL → OCL** (Imran & Bajwa): NL to Object Constraint Language via SBVR, handles quantifiers and logical operators
- **Cond-NLI** (Kim et al., EMNLP 2023): Extracts contradictory conditions from sentence pairs

### The gap we fill
Nobody has combined these into a unified system for reasoning problems. Our multi-view assembly queries all of them (plus AMR, NER, quantifier patterns) and lets the assembler cross-reference to build the FRL. The two genuinely novel pieces: constraint type classification (7-type taxonomy) and implicit constraint detection.

---

## Domain choice for highest probability of success

- Start with solver-verifiable domains.
- Best initial target: constraint/logic word problems compiled to SAT/SMT.
- Two backends: SAT (CNF) for combinatorial puzzles; SMT (Z3) for broader coverage.

---

## Framework direction

- Build a general solver framework (not domain-specific).
- Domain choice / backend routing as scoring + search (learning-to-rank) with verifier feedback.
- Formulation-graph search: nodes = (FRL + assumptions + provenance + backend), edges = refine/add/remove constraints, switch backend, ASK.
- Goal = verified certificate + optional faithful explanation.
- "Shortest path" = minimize cost (solver calls, tokens, user questions) via best-first / A*.

---

## Evaluation ideas (paper-ready)

### Metrics
- Verified solve rate (solve@1, solve@K)
- Semantic compilation accuracy (exact or equivalence checks)
- Robustness under paraphrase/distractors
- Explanation faithfulness rate (EIR checker pass %)
- Backtracking efficiency (candidates tried, solver calls)
- **Formalization fertility** (before/after pre-tokenization)

### Baselines
- One-shot LLM answers
- Chain-of-Thought (CoT)
- Program-Aided Language model (PAL)
- DECLARATIVE (equations + sympy)
- Direct LLM-to-SMT without typed IR
- Rule-based semantic parser

---

## Open questions

- Best representation for FRL: JSON AST vs compact DSL vs multiple IR tiers.
- How to incorporate diffusion-style sampling/guidance effectively for formulation search.
- How much clarification dialogue is needed for ambiguity, and how to trigger it reliably.
- Whether ConstraintDETR should replace or augment the AMR-based pre-tokenizer.
- How formalization fertility relates to existing complexity measures (e.g., problem difficulty ratings, number of reasoning steps).

---

## Text-to-SQL Parallel (NEW — Feb 2026)

### NL→FRL is a generalization of text-to-SQL

Text-to-SQL is the most mature instance of NL → formal language compilation. The field has converged on multi-agent architectures (MAC-SQL, CHASE-SQL, SQL-of-Thought) that mirror our design: decomposition → schema linking → multi-candidate generation → execution-based verification → error-guided repair.

### Direct mapping

```
TEXT-TO-SQL                    NL → FRL
──────────                     ─────────
Database schema (given)        Domain structure (must be INFERRED)
Schema linking                 Entity/constraint extraction
SQL skeleton generation        FRL skeleton generation
Value filling                  Argument binding
Execution-based verification   Solver-based verification (stronger: certificates)
Error correction loop          Compile-check-repair loop
```

### Key finding from text-to-SQL
Accurate schema linking is the single most significant predictor of success — improving it by 15-20% improves end-to-end accuracy by similar margins. Our multi-view assembly IS schema linking, generalized to problems where the schema must be inferred from text.

### What makes our problem harder
1. **No given schema** — entity/constraint structure must be inferred, not linked to a known database
2. **Implicit constraints** — no SQL equivalent; databases declare everything explicitly
3. **The "query" is implicit** — problem text mixes constraints and the question; query type (SAT? OPT? counting?) must be inferred

### What makes our problem have a stronger result
1. **Formal verification** — Z3 certificates vs. SQL execution checks (which can miss semantic errors)
2. **Faithful explanations** — EIR derived from certificates, not just "the query ran successfully"

### Paper positioning
"Text-to-SQL showed that NL→formal language requires schema linking + decomposition + verification. We generalize this to problems where the schema itself must be inferred from text, using multi-view semantic assembly as the generalization of schema linking, and formal verification as the generalization of execution-based checking."

---

## LLM-as-Router: Domain-First Formalization (NEW — Feb 2026)

### The insight that resolves the diffusion/latent tension

Throughout this project, there's been a recurring pull toward "finding the latent reasoning space" — some continuous, learnable representation between NL and formal languages (the LLVM IR of reasoning, the diffusion-over-formalizations idea). It never concretizes because **there is no single universal reasoning IR**. Scheduling constraints, algebraic equations, logical proofs, and optimization objectives have fundamentally different mathematical structures. They're not points on a continuum.

### The resolution: domain classification IS the latent variable

Instead of learning a universal latent space, **use an LLM/SLM to identify the problem domain, then let the domain dictate the formal language.** The LLM does classification and routing. The formal language — which already exists for each domain — handles precision and verification.

The "latent variable" isn't continuous and differentiable. It's a discrete choice: {scheduling, algebra, logic_puzzle, optimization, counting, ...}. That's fine. Once you make that discrete choice, everything downstream is well-defined and well-tooled.

### Why this kills the diffusion temptation

Diffusion over a latent reasoning space would try to smoothly interpolate between "scheduling problem" and "algebra problem." But those aren't points on a continuum — they're categories with different mathematical structures. The topology is wrong.

What "iterative refinement" actually looks like here: the router says "probably scheduling." Compile to scheduling IR. Z3 says UNSAT. Router revises: "maybe optimization with soft constraints." Recompile. Solver succeeds. That's iterative refinement of a **discrete** latent variable (domain choice) guided by verification feedback. It's exactly the formulation-graph search, where CHANGE_DOMAIN is a high-level edge.

### Architecture

```
NL text
  │
  ▼
LLM/SLM Router: "What kind of problem is this?"
  │
  ├── scheduling/assignment  → CSP formalism (Z3 enums + AllDifferent)
  ├── system of equations    → algebraic formalism (sympy / Z3 reals)
  ├── logical deduction      → propositional/FOL (SMT-LIB)
  ├── optimization           → LP/MIP (AMPL / Gurobi format)
  ├── theorem proving        → proof assistant (Lean / Coq)
  └── mixed / uncertain      → try multiple, let verification pick winner

For each candidate domain (best-first):
  Domain-Specific Compiler: NL → domain FRL (using domain's entity types,
                            extraction rules, constraint patterns)
  Domain-Specific Solver: Z3 / MiniZinc / sympy / Gurobi / Lean
  Verifier: certificate or structured error
  
  Success → return (answer, certificate, explanation)
  Failure → try next domain or refine within current domain or ASK
```

### Why SLM for routing is smart

- Fast and cheap (milliseconds, not seconds)
- Fine-tunable on synthetic data (we generate problems per domain = perfect labels)
- Inspectable (confidence scores visible)
- Error-tolerant (wrong routing = try wrong domain first, solver catches it, try next)
- Could even be a BERT-base classifier, not even a generative model

### The multi-view assembly still applies — but scoped by domain

AMR/CiRA/NER views help the scheduling compiler extract assignments and exclusions. The same tools help the algebra compiler extract equations and unknowns. Same views, different interpretation based on domain context. The domain choice tells each view what to look for.

### How this changes the thesis

**Before**: NL → FRL (one universal language) → solver → certificate → explanation

**After**: NL → domain classification → domain-specific FRL → domain-specific solver → certificate → explanation

The compile-check-repair loop gets two levels:
- **Outer loop**: try different domains (high-level formulation-graph edges)
- **Inner loop**: refine formalization within a domain (low-level edges)

### Why this is more publishable than "universal reasoning IR"

"We invented a new formal language" is a hard sell — reviewers ask why not use existing languages. "We show that reasoning-as-compilation works when LLMs do domain recognition and existing formal tools do verification, connected by domain-specific formal languages that already exist" is a much easier sell. You're composing existing pieces smartly, not inventing from scratch.

### The LLVM analogy, revised

You don't need LLVM IR if you have a good compiler for each target architecture and a smart linker. The LLM router is the linker — it decides which compiler to invoke. Each domain-specific compiler is small, well-understood, and well-tooled. The system contribution is the orchestration, not any single component.

### Existing formal languages per domain (already available)

| Domain | Formal language | Solver | What exists |
|--------|----------------|--------|-------------|
| Assignment/scheduling | Z3 enums + constraints | Z3 | SMT-LIB standard |
| Linear algebra / equations | Equation systems | sympy, Z3 reals | Well-studied |
| Logic puzzles | Propositional / FOL | SAT solvers, Z3 | DIMACS, SMT-LIB |
| Optimization (LP/MIP) | Linear programs | Gurobi, CPLEX, OR-Tools | AMPL, MPS format |
| Constraint satisfaction | CSP | MiniZinc, OR-Tools | ESSENCE, MiniZinc |
| Theorem proving | Proof terms | Lean, Coq, Isabelle | Lean 4, Coq |
| Counting / combinatorics | Generating functions / enumeration | Custom | Less standardized |

We don't need to invent ANY of these. We need to: (1) route to the right one, (2) compile NL to it, (3) verify the result, (4) explain the result.

---

## Toward AGI: Reasoning Repository + Persistent Agent (NEW — Feb 2026)

### The explainability connection

Current LLM explanations are fundamentally unfaithful: the explanation is generated by the same process that generated the answer. There's no way to know if the reasoning actually produced the answer or if the model confabulated a justification. Our system separates these completely:

- **FRL is inspectable** — you can read the formalization and check it against the problem
- **Certificate is verifiable** — the solver's witness is independently checkable in polynomial time
- **Explanation is faithful by construction** — EIR steps are derived from the certificate, not invented by a language model
- **Counterfactuals are exact** — "why not alternative X?" is answered by re-solving with modified constraints, not by hallucinating

This provides the XAI properties that post-hoc methods (SHAP, LIME, attention viz) only approximate: faithfulness, completeness, soundness, contrastiveness, minimality, traceability — all by construction, not by analysis.

### Open-ended reasoning IS tractable — with a method repository

The claim that "open-ended reasoning can't be formalized" rests on the assumption that open-ended problems are fundamentally different in kind from formal problems. The counter-argument: **they differ in library size, not in kind.**

A scheduling problem draws from a small library of methods (constraint propagation, AllDifferent, backtracking). An open-ended question like "should we hire Alice?" draws from a larger library (multi-criteria scoring, reference class forecasting, stakeholder analysis, risk assessment). But each method is itself a reasoning pattern that can be captured as a structured trace:

```
Trace #4271:
  Problem type: hiring decision
  Method: multi-criteria weighted scoring
  Steps:
    1. Extract criteria from job description (compilation)
    2. Weight criteria by stakeholder priorities (formalization)  
    3. Score candidate against criteria (evaluation)
    4. Compare to threshold / other candidates (verification)
    5. Identify weakest criterion (explanation)
  Outcome: successful — validated 6 months later
  Applicable when: structured decision with identifiable criteria
```

The repository isn't answers. It's **reasoning strategies with recorded outcomes**, indexed by problem type, method used, success/failure, and similarity features. New problems get solved by searching the repository for applicable methods, executing them, verifying results, and recording the new trace.

Even "soft" reasoning decomposes into steps with structure — not always into Z3 constraints, but into identifiable patterns with checkable intermediate results.

### Learning from experience requires the "I" — persistent agent identity

A model can't learn from experience because:

- **Stateless**: GPT-4 doesn't remember last Tuesday's failed approach on a similar problem
- **No structured index**: even with RAG, a model doesn't have "what methods have I tried, on what problem types, with what success rates"
- **Can't update capabilities**: when a model discovers a new reasoning pattern that works, it can't add it to its toolkit — the toolkit is frozen at training time

What's needed is a **persistent agent**, not a model:

```
The "I" = persistent process with:
  IDENTITY:      continuous thread of experience across problems
  MEMORY:        structured store of past reasoning traces, indexed and searchable
  SKILLS:        toolkit that GROWS (new domain compilers, methods, heuristics)
  METACOGNITION: knows what it's good at, where it's failed, when to ask for help
  AGENCY:        decides what to try, when to backtrack, when to ask
```

The LLM is a COMPONENT of this agent — providing language understanding and generation. The LLM isn't the agent. The agent is the persistent process that uses the LLM as one tool among many.

### How our current system maps to the agent architecture

```
CURRENT SYSTEM                    →  THE AGENT
──────────────                       ─────────
Multi-view analyzers              →  Perception skills
Domain router (LLM/SLM)          →  Pattern recognition + memory lookup
Domain-specific compilers         →  Reasoning skills (expandable toolkit)
Formulation-graph search          →  Strategic planning (method selection)
Solvers + verifiers               →  Execution + verification
EIR + explanation                 →  Self-explanation + communication
ASK step                          →  Knowing what it doesn't know
Compile-check-repair loop         →  Learning from immediate feedback

WHAT'S MISSING (future work):
Persistent memory across problems →  Identity + experience accumulation
Reasoning method repository       →  Skill library that grows over time
Meta-learning (which methods      →  Self-improvement loop
  work for which problems)
```

The reasoning architecture is already right. What's missing is the infrastructure for persistence, accumulation, and self-improvement.

### The AGI-relevant argument

**Current AI conflates competence with performance.** An LLM that's right 95% of the time appears competent but has no mechanism to distinguish reliable from unreliable outputs.

Our work separates these: the LLM provides *competence* (language understanding, domain recognition, candidate formalization). The formal stack provides *performance guarantees* (verification, certificates, faithful explanation). Together they produce something qualitatively different: **reasoning you can trust, with explanations you can check, and explicit acknowledgment of uncertainty.**

One-line version: **AGI won't be a bigger LLM. It'll be a persistent agent that knows when to call a solver, remembers what worked before, and can prove its conclusions.**

### Research program staging

```
Papers 1-2 (now):     Reasoning-as-compilation architecture
                      Each run produces a structured trace that COULD be stored

Papers 3-4 (near):    Reasoning repository
                      Retrieve past traces to improve routing/formalization
                      = few-shot learning with structured reasoning traces

Thesis extension:      Persistent agent
                      Memory + indexing + meta-learning loop
                      Agent improves over time

Long-term vision:      "Open-ended reasoning" = pattern matching against 
                      a sufficiently large, well-indexed library of 
                      structured reasoning methods, with composition 
                      across domains
```

---

## Context Check (Feb 2026)

### Are we on track?

YES. The thesis has six stages:
1. Domain routing (LLM/SLM classification)
2. Multi-view analysis (AMR, NER, constraint detection, quantifiers — independent views)
3. Assembly (query views, cross-reference, build structured IR)
4. Domain-specific FRL compilation (structured IR → typed FRL with provenance)
5. Solver + verification (Z3/MiniZinc/sympy → certificate)
6. Faithful explanation (EIR from certificate + provenance)

Our exploration deepened stages 1-4 (the hard part). Stages 5-6 are engineering we haven't built yet but know how to build.

### Risk
Over-designing the extractor before having a working end-to-end system. The original plan wisely says: stub the extractor, build the backend first, then make the front-end smart.

### Monday priorities (unchanged)
1. Annotate 50 problems → validate fertility thesis
2. Build Z3 runner + FRL schema + verifier → make the system real
3. Stub the NL→FRL extractor (rule parser or LLM prompt)
4. THEN enrich the extractor with multi-view assembly

---

## Research program arc

```
Paper 1: Formalization Fertility + Multi-View Semantic Assembly
         (diagnosis + architecture + pre-tokenizer as queryable views)
    ↓
Paper 2: Verified Reasoning via Compilation 
         (full FRL + runtime + formulation-graph search + explanations)
    ↓
Paper 3: ConstraintDETR on Multi-View Input
         (end-to-end learned constraint detection, replaces assembler heuristics)
    ↓
Paper 4: Reasoning Trace Mining at Scale
         (LLM-powered extraction of structured traces from internet text,
          building the reasoning method repository)
    ↓
Thesis: The full stack — from tokenization diagnosis to verified reasoning,
        with multi-view assembly as the bridging architecture, toward a
        persistent reasoning agent with growing skills and indexed experience
```

### Blog post sequence (public flag planting)
```
Post 1: Formalization fertility (the measurement — data, not claims)
Post 2: The text-to-SQL connection (positioning in established literature)
Post 3: Domain routing kills the universal IR problem (architectural insight)
Post 4: Faithful explanations from certificates (XAI angle, broader audience)
arXiv preprint drops after post 2 or 3, tying everything together
```

