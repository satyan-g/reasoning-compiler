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

## Flowcharts as Trace Representation for the Reasoning Repository (NEW — Feb 2026)

### The problem: how do you represent mined reasoning traces?

The AGI section (below) argues that open-ended reasoning is tractable given a sufficiently large, well-indexed repository of structured reasoning traces — and that the internet already contains billions of these traces that LLMs can extract and structure.

**But what's the representation?** If you mine a Stack Overflow answer, a textbook solution, a forum debate, or an LLM-generated walkthrough, and you want to store the *reasoning strategy* (not just the answer), you need a trace format that captures the actual structure of problem-solving.

### Problem-solving is rarely linear

Real problem-solving traces — the kind you'd mine from text — have:

- **Decision points**: "First check if it's a permutation problem or a combination problem"
- **Branches**: "If the system is overdetermined, try least-squares; otherwise, solve directly"
- **Loops**: "Keep adding constraints until the solution is unique"
- **Dead ends and backtracking**: "I tried dynamic programming but the state space was too large, so I switched to greedy with a proof of correctness"
- **Conditional steps**: "If the graph is acyclic, topological sort; otherwise, detect cycles first"

Linear trace formats (step 1, step 2, step 3...) flatten this structure and lose exactly the information that makes traces reusable: **when to branch, what to try first, what to do when something fails**.

### Flowcharts are the right representation — and they're solved

Flowchart description languages (Mermaid, Graphviz DOT, BPMN, PlantUML) already handle decisions, branches, loops, parallel paths, and join points. They're a solved problem with mature tooling for storage, rendering, diffing, and querying.

A mined reasoning trace stored as a flowchart captures the **strategy graph**, not just the execution path:

```
{Permutation or combination?}
  ├─ permutation → [Check for repetition allowed?]
  │                  ├─ yes → [Use n^r formula]
  │                  └─ no  → [Use n!/(n-r)! formula]
  └─ combination → [Check for repetition allowed?]
                     ├─ yes → [Stars and bars]
                     └─ no  → [Use C(n,r) formula]
```

This isn't just one trace — it's a **family of traces** that covers the decision space. One flowchart replaces many linear traces.

### Why this matters for the reasoning repository (Papers 3-4)

1. **Richer indexing**: a flowchart trace can be indexed by its decision nodes ("what questions does this strategy ask?"), not just by problem type. Retrieval becomes: "find me a strategy that handles the case where X is true but Y is false."

2. **Trace similarity is graph similarity**: comparing two reasoning strategies = graph matching. Well-studied problem. Much more meaningful than sequence alignment on linear traces.

3. **Composability**: strategies from different domains can share subgraphs. "Check if problem has unique solution" is a decision node that appears across combinatorics, linear algebra, constraint satisfaction. Flowchart representation makes this shared structure explicit and reusable.

4. **LLM extraction is natural**: when mining reasoning traces from text, an LLM can be prompted to extract the decision structure, not just the steps. "What decisions did the author make? What alternatives did they consider? What conditions determined each choice?" → flowchart.

### Connection to formulation-graph search

The formulation-graph search (described in Framework direction, below) is already a graph over reasoning states. Flowchart traces from the repository would be *templates* for that search — prior knowledge about which paths tend to work for which problem types. The repository doesn't just store answers; it stores **navigation strategies** for the formulation graph.

---

## Open questions

- Best representation for FRL: JSON AST vs compact DSL vs multiple IR tiers.
- How to incorporate diffusion-style sampling/guidance effectively for formulation search.
- How much clarification dialogue is needed for ambiguity, and how to trigger it reliably.
- Whether ConstraintDETR should replace or augment the AMR-based pre-tokenizer.
- How formalization fertility relates to existing complexity measures (e.g., problem difficulty ratings, number of reasoning steps).
- What's the right flowchart description language for storing mined reasoning traces (Mermaid, DOT, BPMN subset, or something more semantic)?

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

## The Fertility Spectrum: Extraction vs. Generation (NEW — Feb 2026)

Paper 1 focuses on problems where constraints exist in the NL but get lost (high fertility). There's a qualitatively different class — Fermi estimation, interview puzzles — where constraints don't exist in the text at all. Fertility is effectively infinite: the reasoning IS constraint generation from world knowledge, not extraction. This suggests a "constraint generation" module alongside extraction, where each generated assumption is a constraint with provenance = "assumed, not stated." Sensitivity analysis (re-solve with perturbed assumptions) identifies which assumptions drive the answer — something current LLMs can't do. Phase 3+ extension; not actionable until single-domain pipeline works.

---

## UNSAT Cores as Discrete Gradients (NEW — Feb 2026)

Backprop distributes blame via chain rule over continuous parameters. UNSAT cores distribute blame via minimal infeasible subsets over discrete constraints. Both answer "which earlier decisions caused the bad outcome?" — making UNSAT cores a discrete analogue of gradients. The analogy holds for blame attribution but breaks for repair direction: gradients say how much to change each parameter, while cores only say which constraints conflict, not which one is wrong. Implication: training reasoning models on search episodes with structured failure signals (not just correct traces) could teach backtracking heuristics, with the external verifier remaining source of truth. Theoretical observation for Papers 3-4.

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

---

## Novelty risk — literature check needed (2026-03-01)

**Concern:** The "compilation framing for LLM reasoning" space is already in silent motion. PAL (Program-Aided Language Models), Parsel, and similar work are adjacent. Need to establish what's genuinely novel before investing heavily in the research timeline.

**Potentially differentiating angles:**
- Formalization fertility as a *metric* (measuring compilability of NL problems)
- Domain routing to multiple formal backends (not just Python/code)
- Full certificate-based verification with provenance-traced explanations
- The compiler metaphor taken seriously (multi-view analysis, assembler, typed IR)

**Action:** Literature search to map what exists, identify clear water, and sharpen the contribution claims. Results go below.

### Literature search results (2026-03-01)

**Closest competitor: Logic-LM** (Pan et al., 2023, arxiv 2305.12295)
- Does NL → symbolic formulation (FOL, CSP) → solver (Prover9, Z3) → answer
- Has a self-refinement loop (solver errors fed back to LLM)
- Lacks: domain routing, structured pre-tokenization, fertility metric, UNSAT-core repair, certificate explanations

**Other key related work:**
- **SatLM** (Ye et al., 2023, 2305.09656) — NL → SAT → solver. Propositional only.
- **PAL** (Gao et al., 2023, 2211.10435) — NL → Python → execute. No verification.
- **Faithful CoT** (Lyu et al., 2023, 2301.13379) — NL → symbolic (Python/Datalog/PDDL) → deterministic exec. Similar motivation but no certificates/fertility.
- **OptiMUS** (AhmadiTeshnizi et al., 2024, 2402.10172) — NL → LP/MIP → Gurobi. Single formal backend.
- **LINC** (Olausson et al., 2023, 2310.15164) — NL → FOL → Prover9/Mace4. Narrow (entailment only).
- **ToRA** (Gou et al., 2024, 2309.17452) — Interleaves reasoning + tool calls (Python, sympy).
- **Parsel** (Zelikman et al., 2023, 2212.10561) — Hierarchical program synthesis, not formal reasoning.
- **NL4Opt** (2022) — NL → optimization. Competition track.

**What's genuinely novel (clear water):**
1. Formalization fertility as a predictive metric — NOBODY has this
2. Constraint pre-tokenization as structured extraction before formalization
3. Domain routing as discrete latent variable with verification-guided backtracking
4. Certificate-based faithful explanations (EIR) with provenance tracking
5. Multi-view semantic assembly (compiler-style independent analyses)

**Gray zone (partially explored, our angle is fresher):**
- Compile-check-repair with UNSAT cores (vs Logic-LM's raw error feedback)
- Full end-to-end pipeline completeness

**Verdict:** Green light. Fertility + pre-tokenization are unoccupied. Differentiate carefully vs Logic-LM.

**TODO:** Search AAAI/ICLR/ACL 2025 proceedings and late-2025 arxiv for "formalizability metric", "NL2SMT", "compilability reasoning" to verify no scooping.

---

## Percepta: "Can LLMs Be Computers?" — positioning note (2026-03-14)

**Source:** [percepta.ai/blog/can-llms-be-computers](https://www.percepta.ai/blog/can-llms-be-computers) (Christos Tzamos et al., Mar 11, 2026)

**What they do:** Build a computer inside a transformer. Compile C → WebAssembly → tokens, then execute the program within the transformer's own inference loop (no external tool call). Key technical unlock: restrict attention heads to 2D, which turns KV lookup into a convex-hull query answerable in O(log t) instead of O(t). Demos: Hungarian algorithm (300K tokens, 33K tok/s), Arto Inkala Sudoku (3.5M tokens, solved in ~3 min). 100% accuracy on Sudoku benchmarks.

**Same diagnosis, different layer:**
- Both projects start from "LLMs fail at structured reasoning"
- Percepta targets the **execution** bottleneck (can't run algorithms reliably)
- We target the **encoding** bottleneck (can't extract constraints from NL)
- Their demos all start with already-formalized inputs (cost matrices, Sudoku grids) — the NL→formal gap is untouched

**Why this is NOT a threat to Paper 1:**
- They don't address fertility, NL-to-formal compilation, or constraint pre-tokenization
- Even with a perfect in-model executor, you still need to correctly translate "Alice can't weld" into constraints — that's our problem
- Our work is upstream: encoding must happen before execution

**Why this STRENGTHENS our motivation:**
- If execution is solvable (Percepta shows it is), then encoding becomes the clearly remaining hard problem
- Their correctness guarantee ("if compiled solver is correct, execution is correct") still requires correct problem formulation — which is exactly what fertility measures
- Paper 1 can cite this as evidence that the execution layer is increasingly solved, sharpening focus on the encoding layer

**Philosophical tension worth noting in Paper 2 / related work:**
- Percepta internalizes computation into the transformer; we externalize it to a verified solver
- They claim correctness via compiler correctness; we claim it via mathematical certificates
- Open question: which is more robust under distribution shift or adversarial NL inputs? (Our approach has the advantage of independent verification — the certificate doesn't depend on the model being right)

**Potential future integration (speculative, post-Paper 2):**
- NL → pre-tokenizer → FRL → compiled WASM → in-model execution via Percepta-style executor
- Would eliminate the external solver dependency while keeping the encoding/verification story
- Only worth exploring if their 2D-head models can be trained at scale

---

## Spark: Compile a reasoning compiler into LLM weights (2026-03-14)

**Triggered by:** Percepta's "compile programs into weights" vision applied to our core problem.

**The insight:** Percepta compiled an *interpreter* (executor) into transformer weights. We don't need an in-model solver — external solvers (Z3, Gurobi) are better at that and always will be. What we need is an in-model *compiler*: the ability to reliably translate NL into correct formal constraint representations (FRL). That's the encoding gap. That's what fertility measures. That's literally the name of this repo.

**The one-liner:** Percepta coded for a virtual WebAssembly machine that executes inside the transformer. We want to code for a virtual FRL machine that dispatches to external solvers. Same pattern — make the model natively speak a formal language — different target machine.

| | Percepta | Reasoning Compiler |
|---|---|---|
| **Virtual machine** | WebAssembly interpreter | FRL execution engine |
| **Instruction set** | WASM opcodes | FRL constraints, queries, trace responses |
| **Where it runs** | Inside the transformer | Delegated to external solvers |
| **What's compiled into weights** | The interpreter | The compiler (NL → FRL) |
| **Traces** | Model generates execution tokens | Model reads solver results in FRL |

**The reframe:**
- Percepta: compile an interpreter into weights → model can execute programs
- Us: compile a *compiler* into weights → model can formalize reasoning
- Both use the same mechanism (structured behavior baked into weights) for different purposes
- We keep external solvers for execution (they're better), but the NL→FRL step becomes reliable because it's compiled in, not prompted for

**Three-stage architecture:** Formulation, Planning, and Execution are separate concerns.

### Stage 1: FORMULATE — NL → FRL (where weight compilation applies)

Faithful translation of natural language into formal representation. Capture all entities, constraints, relationships, implicit assumptions. Zero information loss is the goal. Fertility measures how hard this step is. This is where "compile into weights" helps — make the LLM natively produce correct FRL.

```
Today:     NL → [LLM + prayer] → FRL
Goal:      NL → [LLM with compiled formalization] → FRL
```

**What gets compiled (deterministic, rule-based):**
- Quantifier phrases → operators ("no more than" → ≤, "at least" → ≥, "exactly one" → =1)
- Negation patterns → FORBID ("cannot", "must not", "prohibited from")
- Uniqueness patterns → AllDifferent ("each", "no two", "exactly one of")
- Numeric extraction ("three" → 3, "a dozen" → 12)

**What gets trained (fuzzy, context-dependent):**
- Entity typing (is "welding" a task or a skill? depends on the domain)
- Pragmatic constraint inference ("morning is too early for Bob" → FORBID(assign(Bob, morning)))
- Ambiguity resolution (inclusive vs exclusive "or")

**The hybrid: compiled + learned in one module.**
Deterministic parts are constructed directly into weights (correct by construction, no training needed). Fuzzy parts are learned via training on the base LLM's representations. This is "firmware + software" in a single neural module.

### Stage 2: PLAN — FRL → execution flowchart

Given the FRL, the LLM reasons about *how* to solve it. Decompose into subproblems? Solve directly? Relax and tighten? This is macro-level strategy — the flowchart, not the execution. This stage stays as LLM reasoning (not compiled) because it's inherently dynamic and problem-dependent.

### Stage 3: EXECUTE — run solvers, feed FRL traces back to LLM

The LLM issues solver calls and receives results. Critically: **traces are returned TO the LLM, not generated BY the LLM** (unlike Percepta where traces are inside the model). And traces are expressed in FRL — the same formal language the LLM used to formulate — so there's no lossy translation.

```
LLM                                    External Solvers
 │                                          │
 │──── FRL (subproblem A) ────────────────►│
 │                                          │── Z3 solves
 │◄─── FRL trace (UNSAT, core={c3,c7}) ───│
 │                                          │
 │ reads trace in FRL, decides: relax c3    │
 │                                          │
 │──── FRL (subproblem A', c3 relaxed) ───►│
 │                                          │── Z3 solves
 │◄─── FRL trace (SAT, witness={...}) ────│
 │                                          │
 │ reads trace, moves to subproblem B       │
```

**Why FRL as the trace language matters:**
- LLM formulated in FRL, so it reads results in the same notation — no translation loss
- UNSAT cores reference FRL constraint IDs — model knows exactly which constraints conflict
- Witnesses map to FRL variables — model can verify partial solutions against remaining constraints
- The feedback loop stays formal, avoiding a lossy NL round-trip

**Key contrast with Percepta:** They generate execution traces inside the model (model as executor). We receive solver traces from outside (model as controller). The LLM never executes — it reads, decides, and dispatches. External solvers do the heavy lifting.

### Full architecture sketch:

```
┌──────────────────────────────────────────────────────┐
│  Base LLM (frozen, any version)                      │
│  ...transformer layers...                            │
│  final hidden states                                 │
└─────────┬────────────────────────────────────────────┘
          │ read-only
┌─────────▼────────────────────────────────────────────┐
│  Reasoning compiler module (yours, small, portable)  │
│  - compiled: quantifier norm, negation, numerics     │
│  - learned: entity typing, relation classification   │
│  Output: FRL                                         │
└─────────┬────────────────────────────────────────────┘
          │ FRL
          ▼
┌──────────────────────────────────────────────────────┐
│  LLM as controller                                   │
│  - reads FRL                                         │
│  - plans execution strategy (flowchart)              │
│  - dispatches subproblems to solvers                 │
│  - reads FRL traces back from solvers                │
│  - decides next step (continue / backtrack / done)   │
└─────┬──────────────────────────────────▲─────────────┘
      │ FRL subproblem                   │ FRL trace
      ▼                                 │
┌─────────────────────────────────────────┐
│  External solvers (Z3, Gurobi, etc.)    │
│  - solve                                │
│  - return witness or UNSAT core in FRL  │
│  - return certificates                  │
└─────────────────────────────────────────┘
```

### Portability

**Can the reasoning compiler module survive base model upgrades?**

LoRA modifies internal weights — deltas break when the base changes. Better: add layers on top, don't modify existing ones. Freeze the base LLM, add your own trainable + compiled layers that read from its representations.

**Why this is more portable:**
- Final-layer representations are more stable across versions (anchored by same pretraining objective)
- You're reading from representations, not modifying them
- Retraining cost on new base: quick fine-tune of learned parts; compiled parts don't change

**Candidate architectures (most to least separable):**
1. **Adapter heads** — task-specific decoders on final hidden states, output FRL directly
2. **Side-tuning** (Zhang et al., 2020) — parallel side network, completely decoupled
3. **Cross-attention layers** (Perceiver-style) — cross-attend to frozen model's hidden states
4. **LLaMA-Adapter** (Zhang et al., 2023) — learned prompts prepended to top K layers

**Testable hypothesis:** Train a constraint formalization adapter on Llama 3 70B, evaluate on Llama 3.1/3.2/3.3 without retraining. If FRL extraction accuracy stays within 5%, portability is viable.

### Why this matters

If you can compile a reasoning compiler into portable weight modules, you ship a capability that rides the frontier. As base models improve at language understanding, your compiled formalization gets better inputs for free. This is "linking" for neural networks — compiled libraries that survive model upgrades.

**Timeline:** Post-Paper 1. Could be standalone investigation or Paper 3 direction.

**Related work to check:** Percepta (weight compilation), model stitching, representation similarity (CKA, SVCCA), adapter portability, LLaMA-Adapter, side-tuning.

---

## Spark: Full Pipeline Trace Dataset (2026-03-14)

**Triggered by:** Survey of existing reasoning trace datasets reveals a clear gap.

**The gap:** No dataset captures ground-truth annotations at all three levels of reasoning:
1. **Formulation** — NL → formal representation with provenance (which NL span → which constraint, implicit constraints flagged)
2. **Planning** — strategy selection (solve directly / decompose / relax-and-tighten) with rationale
3. **Execution** — solver calls and results in formal language, backtracking decisions, certificates

Existing datasets cover at most two levels, and formulations are usually LLM-generated (not ground-truth). See `papers/references/reasoning_trace_datasets_survey.md` for full survey.

**What the dataset would contain per problem:**
- NL problem text
- FRL formulation with per-constraint provenance to NL spans
- Implicit constraint annotations (constraints inferred, not stated)
- Planning trace: strategy chosen, decomposition if any
- Execution trace: sequence of FRL solver calls, FRL responses (witness/UNSAT core), backtracking decisions
- Final answer + independently verified certificate
- Fertility score (tokens per constraint)

**Why this is publishable on its own:**
- NeurIPS Datasets & Benchmarks track, or ACL resource paper
- Establishes FRL as an annotation standard others can adopt
- Provides the first ground-truth benchmark for evaluating full reasoning pipelines (not just final answers)
- Natural precursor to the compiler paper — "here's the data, here's what we learned, here's what a compiler needs to handle"

**Build path:**
1. Start from existing problems: ZebraLogic (1K logic grids), FOLIO (1.4K FOL), NL4Opt (1.1K optimization)
2. Phase A: Hand-annotate 50 problems with full FRL + solver traces (validates schema)
3. Phase B: LLM-draft FRL for next 200, human verify and correct (gives ground-truth + error analysis)
4. Phase C: Release dataset + annotation schema + tooling

**Strategic value:**
- A dataset paper is faster to write than a systems paper
- Other researchers build on your data → your formalism gets adopted
- The annotation process itself generates insights about where NL→formal translation breaks down
- Directly feeds the compiler paper and the weight compilation research

**Infrastructure already built:**
- FRL v0 schema with provenance tracking ✓
- Z3 compiler with tracked assertions ✓
- Independent verifier ✓
- 5 worked examples ✓

**Timeline:** Could start Phase A immediately (50 hand-annotated problems). Dataset paper draft in parallel with compiler work.

**Related datasets to build on:** ZebraLogic, FOLIO, NL4Opt, ProverQA, Logic-LM benchmarks.

---

## Spark: RL for unsupervised FRL generation (2026-03-14)

**Triggered by:** Realizing that Z3 + the independent verifier give you a free, binary, structured reward signal — no human labels needed.

**The setup:**
```
LLM generates FRL from NL problem
        │
        ▼
    Z3 solves the FRL
        │
        ├── correct answer?  → reward +1
        ├── wrong answer?    → reward -1, feedback: which constraints differ
        └── UNSAT?           → reward -1, feedback: UNSAT core (which constraints conflict)
        │
        ▼
    LLM tries again (feedback is in FRL, not NL — precise, no lossy translation)
```

**Why this works:**
- The reward signal is **binary and verifiable** — not a fuzzy LLM-as-judge score
- The error signal is **structured** — UNSAT cores tell you *which* constraints are wrong
- The FRL format is **compact** — smaller action space than free-form code generation
- You can generate **unlimited training signal** — ZebraLogic produces arbitrary puzzles programmatically
- The verifier is **independent of the model** — no reward hacking possible

**Analogy:** This is the same structure as code generation RL (generate code → run tests → reward), but for constraint formalization. AlphaCode generates programs and tests them. We generate FRL and verify it.

**What you need:**
1. Problems with known answers (ZebraLogic 1K, Puzzle Baron, synthetic generation)
2. LLM that generates FRL from NL (start with prompted, no fine-tuning)
3. Existing pipeline: FRL → Z3 → verify against expected answer ✓ (already built)
4. Feedback loop: format solver errors as FRL-language feedback to the LLM

**Practical first step (before any RL):**
Prompted loop. Take 10 ZebraLogic problems, prompt an LLM to output FRL, run through the pipeline, see what breaks. This tells you:
- Whether the FRL schema is LLM-friendly (can the model produce valid FRL?)
- What error patterns emerge (missing constraints? wrong entity types? bad provenance?)
- Whether the feedback loop is informative (does the model improve on retry with UNSAT core feedback?)

If the prompted loop works, you have a paper: "FRL generation with verifier-in-the-loop." If it doesn't, the failure modes tell you what to fix in the schema or the prompting.

**RL comes later:** Once the prompted loop is validated, switch to actual RL fine-tuning (PPO/DPO on a small model like Llama 8B). The reward function is already built — it's your pipeline. The training data is unlimited — it's ZebraLogic's generator. The evaluation is rigorous — it's Z3.

**Timeline:** Prompted loop is doable now (1-2 days). RL fine-tuning is Paper 3+ territory.

**Connection to weight compilation spark:** The RL-trained model learns constraint formalization from experience. The weight compilation approach bakes it in by construction. These are complementary — RL handles the fuzzy parts, compilation handles the deterministic parts. The endgame is both together.

---

## Spark: Reasoning vs knowledge mutability — the case for separation (2026-03-20)

**Core insight:** LLMs bundle two capabilities with fundamentally different update frequencies:

| | Reasoning/Logic | World Knowledge |
|---|---|---|
| **Update frequency** | Rarely (modus ponens doesn't change) | Constantly (events, prices, facts) |
| **Training trigger** | New reasoning methods discovered | New information arrives |
| **Ideal architecture** | Train once, stable module | RAG, knowledge base, or frequent fine-tuning |

Cramming both into one set of weights means retraining everything when knowledge changes, even though the reasoning capability was fine. A separated reasoning compiler module has **low mutability** — trained once on formal reasoning patterns, stable across knowledge updates.

**This strengthens the portable module architecture:** The "frozen base LLM + separable reasoning compiler" design (see earlier spark) isn't just about portability across model versions. It's about separating components by their natural update cadence. The reasoning module rides the frontier without retraining because reasoning methods don't change. The base LLM handles knowledge and gets updated independently.

**Ternary weights for reasoning (speculative hunch):**

Reasoning is fundamentally about logic (constraint satisfied or not, implication holds or doesn't), not probability distributions. This suggests ternary weights (-1, 0, 1) may be a natural fit for the reasoning module:

- **Discrete mappings are ternary-friendly:** "no more than" → ≤ is a discrete rule, not a soft interpolation
- **Cheap and fast:** 1.58 bits per weight, multiply-free ops (add/subtract/skip)
- **Architecturally enforced separation:** ternary module can't be accidentally blended back into full-precision weights
- **Connects to BitNet research** (Ma et al., 2024): ternary models are surprisingly capable for general language; they may be *especially* suited for formal/logical tasks

**What's unproven:** Whether ternary is actually *better* for reasoning vs just *adequate*. The fuzzy parts of NL→FRL (pragmatic inference, ambiguity resolution) may still need full-precision weights. The hybrid compiled+learned module design handles this: compiled deterministic rules in ternary, learned fuzzy extraction in full-precision.

**Testable hypothesis:** Take a small reasoning model, quantize to ternary, measure constraint extraction accuracy vs full-precision. If accuracy holds, the mutability+efficiency argument is strong.

**Timeline:** Post-pipeline. Research direction for Paper 3+.

---

## Spark: FRL as a constraint algebra — Borel hierarchy + optimization layer (2026-03-20)

**Triggered by:** Systematic analysis of FRL completeness using real analysis / set theory.

**The framing:** FRL constraint types form an algebra. Completeness can be checked by mapping against standard mathematical operations and verifying closure.

### Σ-hierarchy of FRL expressiveness

```
Σ₀: base constraints (ASSIGNMENT, CO_OCCURRENCE, ORDER, DISTANCE, BOUNDS, CARDINALITY, UNIQUENESS)
     + CONDITIONAL (implication)
Σ₁: + complement (polarity=-1 on any constraint)
Σ₂: + union (DISJUNCTION)                              ← CURRENT STATE
Σ₃: + objective function + soft constraints + priorities ← OPTIMIZATION LAYER (future)
```

Each level strictly extends the previous. A Σ₃ problem with no objective and all hard constraints degrades cleanly to Σ₂ (pure SAT).

### Current state (Σ₂ complete)

9 primitive generators:

| Generator | Set theory analog | Real analysis analog |
|---|---|---|
| ASSIGNMENT | Point: {h} ⊂ H | Point evaluation |
| CO_OCCURRENCE | Diagonal: {(x,y) : x = y} | Kernel of f-g |
| ORDER | Half-space: {(x,y) : x < y} | Open set in product topology |
| DISTANCE | Level set: d⁻¹(N) | Metric ball boundary |
| BOUNDS | Measurable set: S ⊂ H | Indicator function support |
| CARDINALITY | Counting measure | Measure of preimage |
| UNIQUENESS | Injective function constraint | Non-degeneracy |
| CONDITIONAL | Implication: Aᶜ ∪ B | Open set in implication topology |
| DISJUNCTION | Union: A ∪ B | Open set union |

Operations: NOT (complement), AND (intersection, implicit), OR (DISJUNCTION).

3 derived types (backward compat): EXCLUSION, ADJACENT, RIGHT_OF.

Boolean algebra over constraints is complete.

### Optimization layer (Σ₃ — future, complementary not overlapping)

Lagrange multipliers motivate three additions:

| Concept | What it adds | FRL representation |
|---|---|---|
| **OBJECTIVE** | "What's the best solution?" | New type: minimize/maximize an expression |
| **Soft constraints** | "Prefer but don't require" | `weight: float` field on Constraint (None = hard) |
| **Priority** | "Which to satisfy first" | `priority: int` field on Constraint |
| **Multiplier output** | "Which constraints are binding" | Extension to SolveResult: dual variables per constraint |

**Why these are complementary, not overlapping:**
- SAT asks "does a solution exist?" — optimization asks "what's the best?"
- Hard constraints are a special case of soft constraints (infinite weight)
- A problem with no OBJECTIVE degrades to pure SAT
- Z3 supports both: `z3.Solver()` for SAT, `z3.Optimize()` for optimization

**Multipliers as structured feedback for the repair loop:**
The Lagrange multiplier (dual variable) for each constraint tells the LLM:
- multiplier > 0 → constraint is binding (active at the optimum)
- multiplier = 0 → constraint has slack (could be tightened without cost)
- magnitude → how much the objective improves per unit of relaxation

This is the structured solver trace the LLM needs for Stage 3 (EXECUTE): "constraint c3 is the most binding; relaxing it improves the objective by 2.5 per unit."

**Timeline:** After arithmetic domain is properly integrated. Optimization is the third domain (NL4Opt). Implementing Σ₃ requires `z3.Optimize()` backend, which is a clean compiler extension.

**Domains by Σ-level:**
- Σ₂: logic grids (ZebraLogic), arithmetic word problems (GSM8K)
- Σ₃: optimization (NL4Opt), scheduling with costs, resource allocation


---

## Spark: Bayesian confidence on constraints — repair loop prior (2026-03-20)

**Triggered by:** Checking FRL against statistical / Bayesian primitives.

**Finding:** FRL doesn't need probabilistic constraint *types* (the domains are deterministic). But the *meta-layer* — how confident we are in each constraint's correctness — benefits from Bayesian thinking.

**Current state:** `confidence: int ∈ {+1, 0, -1}` (explicit / inferred / contradicted). This is a quantized Bayesian prior.

**What continuous confidence enables:**

The repair loop becomes Bayesian inference:
```
Prior:      P(constraint_i correct) = 0.8     (LLM's initial confidence)
Evidence:   UNSAT core contains constraint_i
Posterior:  P(correct | in UNSAT core) → 0.3  (Bayes update)
Action:     Revise lowest-posterior constraint first
```

Mapping:

| Statistical concept | FRL mapping |
|---|---|
| Prior | `confidence` on each constraint (LLM's belief in its formulation) |
| Likelihood | UNSAT core membership (evidence about which constraints are wrong) |
| Posterior | Updated confidence after solving (guides repair) |
| Soft weight | `weight ≈ log(prior)` (optimization: how much to pay to satisfy) |
| Frequentist p-value | Constraint holds across N paraphrases (robustness) |

**What this does NOT add:** No probabilistic constraint types, no distributions, no sampling. Z3 is exact. This is about confidence in *formulation correctness*, not uncertainty in *problem data*.

**Design decision:** Keep `confidence: int` (ternary) for now. Upgrade to `confidence: float ∈ [0,1]` when the repair loop runs at scale. The ternary value captures the essential distinction; continuous confidence is an optimization for prioritized repair.

**Timeline:** Implement when repair loop exists (Paper 2+).
