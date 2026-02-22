# CLAUDE.md — Guidance for AI-Assisted Development

## Who am I (the human)

I'm a practitioner, not a full-time researcher. Research is a side pursuit. I have strong intuitions and seed ideas but limited time. I need focused, incremental progress — not architecture astronautics.

## What this project is

A research system for **verified reasoning via compilation**: NL → formal language → solver → certificate → faithful explanation.

**Core thesis**: LLM reasoning fails at the semantic-to-formal compilation boundary (high "formalization fertility"), not at reasoning itself. Fix it by domain-specific compilation + formal verification.

**Two-paper strategy**:
- Paper 1: "Formalization Fertility" — fertility metric predicts LLM failure; constraint pre-tokenization helps
- Paper 2: "Verified Reasoning via Compilation" — full system with search, ASK step, EIR explanations

See `docs/sparks.md` for the full idea log and `docs/plan.md` for execution plan.

## Repository structure

```
reasoning-compiler/
├── src/                          # Source modules (all placeholder READMEs, no .py yet)
│   ├── frl/                      # Formal Reasoning Language: schema, types, canonicalization
│   ├── compiler/                 # FRL → Z3/SMT-LIB compilation with provenance tracking
│   ├── runtime/                  # Solver execution, formulation-graph search, ASK step
│   ├── pretokenizer/             # Multi-view constraint extraction (AMR, NER, classifiers)
│   ├── nl2frl/                   # NL → FRL translation (rule-based, LLM, seq2seq)
│   ├── explain/                  # EIR explanation generation + step checker
│   └── fertility/                # Token counting, fertility metrics, failure correlation
├── tests/                        # pytest tests (empty — write tests alongside each module)
├── data/
│   ├── raw/                      # Downloaded datasets (gitignored)
│   ├── annotated/                # Manual annotations (committed)
│   ├── synthetic/                # Generated data (gitignored, reproducible via seed)
│   └── processed/                # Intermediate artifacts (gitignored)
├── datagen/                      # Synthetic data generation scripts
├── scripts/                      # Utility scripts
├── experiments/
│   ├── configs/                  # YAML experiment configurations
│   ├── runners/                  # Experiment execution scripts
│   └── analysis/                 # Post-hoc analysis notebooks
├── papers/
│   ├── fertility/                # Paper 1 drafts and figures
│   └── verified_reasoning/       # Paper 2 drafts and figures
├── docs/                         # Design documentation
│   ├── sparks.md                 # Comprehensive idea log (668 lines — read this first)
│   ├── plan.md                   # Phased execution plan
│   ├── project_organization.md   # Repo structure, experiment plans, git workflow
│   └── workflow_guide.md         # claude.ai ↔ Git ↔ Claude Code bridge
├── CLAUDE.md                     # This file — AI assistant guidance
├── DECISIONS.md                  # Technical decisions log
├── FINDINGS.md                   # Experiment results (empty — to be populated)
├── README.md                     # Project overview
├── Makefile                      # Dev commands
└── pyproject.toml                # Python package config
```

## Implementation status

**Current state**: Project scaffold complete. All documentation written. **No Python code exists yet.** All `src/` modules are directory + README placeholders only.

### Phase 0: Foundation ← CURRENT PHASE
- [ ] FRL v0 schema (dataclasses for assignment domain)
- [ ] Z3 compiler (FRL → Z3 constraints with tracking)
- [ ] Independent verifier (check witness against FRL, no Z3)
- [ ] Solver runner (compile + solve + extract witness/core)
- [ ] 5 hand-written FRL examples that solve correctly
- [ ] Fertility measurement on 50 manually annotated GSM8K problems
- [ ] Go/no-go: does fertility correlate with LLM failure?

### Phase 1: Data + Baseline
- [ ] Synthetic puzzle generator (10k problems with ground truth FRL)
- [ ] LLM baseline: GPT-4/Claude on same problems (CoT, PAL, direct)
- [ ] Measure fertility on synthetic data
- [ ] Simple NL→FRL via LLM structured extraction (stub the "compiler")

### Phase 2: Pre-tokenizer + Paper 1
- [ ] AMR parsing baseline (what does it recover?)
- [ ] Constraint classifier (DeBERTa on synthetic data)
- [ ] Full pipeline evaluation vs baselines
- [ ] Robustness tests (paraphrase, distractor, reorder)
- [ ] Write and submit Paper 1 / arXiv preprint

### Phase 3: Runtime + Paper 2
- [ ] Formulation-graph search with backtracking
- [ ] ASK step (detect underspecification)
- [ ] EIR explanation generation + checker
- [ ] Write Paper 2

## Tech stack and development commands

### Dependencies
- Python 3.10+
- z3-solver >= 4.12 (SMT backend)
- tiktoken >= 0.5 (token counting for fertility)
- jsonschema >= 4.0 (FRL validation)
- pytest >= 7.0 (testing, dev dependency)
- Later: spacy, amrlib, transformers (NLP components)
- Later: matplotlib, seaborn, pandas, scipy (analysis/figures)

### Setup and commands
```bash
make setup          # pip install -e ".[dev]"
make test           # pytest tests/ -v
make clean          # remove __pycache__ and .pyc files
```

### pytest configuration
- Test paths: `tests/`
- Default options: `-v --tb=short`
- Configured in `pyproject.toml` under `[tool.pytest.ini_options]`

## Key technical decisions made

1. **FRL v0 targets assignment problems only** — not universal. 5 constraint types: EXCLUSION, ASSIGNMENT, UNIQUENESS, CONDITIONAL, CARDINALITY.
2. **FRL uses JSON/dataclasses, not a custom DSL** — schema-validatable, LLM-readable. Revisit if complexity grows.
3. **Domain routing deferred** — don't build until 2+ domains exist. A router with one destination is overhead.
4. **docs/sparks.md is the bridge** — shared artifact between claude.ai brainstorming and Claude Code implementation.

See `DECISIONS.md` for the full log with rationale.

## Project principles — ENFORCE THESE

### 1. BUILD BEFORE THEORIZING
- Do not design elaborate architectures before the basics work end-to-end.
- The first priority is always: can I run a problem through the pipeline and get a verified answer?
- Stub what isn't needed yet. Implement what is needed now.

### 2. ONE DOMAIN FIRST
- Start with assignment/scheduling puzzles compiled to Z3.
- Do NOT build multi-domain support until single-domain works perfectly.
- Do NOT build the domain router until there are at least 2 working domains to route between.

### 3. TESTS BEFORE FEATURES
- Every module gets tests before the next module starts.
- A passing test suite is the definition of "done" for a module.
- If you can't test it, you've built too much.

### 4. SMALL COMMITS, CLEAR MESSAGES
- Each commit does one thing.
- Commit convention: `feat(module):`, `fix(module):`, `test(module):`, `data:`, `exp:`, `docs:`, `paper:`
- Never commit broken tests to main or dev.

### 5. DATA IS GENERATED, NOT COMMITTED
- Raw datasets go in `data/raw/` (gitignored).
- Synthetic data is generated by scripts in `datagen/` (gitignored, reproducible via seed).
- Only manual annotations (`data/annotated/`) are committed.

### 6. EXPERIMENTS ARE REPRODUCIBLE
- Every experiment has a YAML config in `experiments/configs/`.
- Config + seed + data version = same result.
- Results go in `results/` (gitignored). Key findings go in `FINDINGS.md`.

## Guardrails — STOP ME IF I DO THESE

### Scope creep
- If I ask to "also add support for X" before the current thing works → push back.
- Remind me: "Does the current pipeline work end-to-end? If not, finish that first."

### Over-engineering
- If I ask for an elaborate class hierarchy, plugin system, or config framework → push back.
- Remind me: "A function that works is better than an architecture that doesn't."

### Premature optimization
- If I worry about performance before correctness → push back.
- Remind me: "Make it work, make it right, make it fast. In that order."

### Rabbit holes
- If I spend more than 30 minutes on a tangent → flag it.
- Suggest: "Note this in docs/sparks.md and come back to it later."

### Perfectionism on writing
- If I delay publishing because "it's not ready" → push back firmly.
- Remind me: "An imperfect arXiv preprint posted today protects you better than a perfect paper in 6 months."

## Code conventions

- **Functions over classes.** Flat over nested. Working over elegant.
- **Dataclasses** for FRL schema (not Pydantic, not custom DSL).
- **No .py files exist yet** — when creating them, add `__init__.py` to each `src/` subpackage.
- **Test file naming**: `tests/test_<module>.py` (e.g., `tests/test_frl.py`, `tests/test_compiler.py`).
- **Imports**: use `from src.frl.schema import ...` style (package installed in editable mode via `pip install -e`).

## Gitignored paths (do NOT commit)

- `data/raw/`, `data/synthetic/`, `data/processed/` — generated/downloaded data
- `results/` — experiment results
- `chats/` — conversation logs
- `models/`, `checkpoints/` — trained models
- `.venv/`, `venv/` — virtual environments
- `.env` — secrets

## Key files to read for context

| File | What it contains |
|------|-----------------|
| `docs/sparks.md` | Full idea log — architecture, literature, decisions, vision (read this first) |
| `docs/plan.md` | Execution plan with timeline and paper outlines |
| `docs/project_organization.md` | Repo structure, 7 experiment plans, git workflow |
| `docs/workflow_guide.md` | How claude.ai and Claude Code work together |
| `DECISIONS.md` | Technical decisions made during implementation |
| `FINDINGS.md` | Experiment results and key observations |

## How to help me best

1. **Read docs/sparks.md first** when starting a new session. It has all the context.
2. **Be direct** about what to build next. Don't give me options — give me the next concrete step.
3. **Push back** when I'm going off track (see Guardrails above).
4. **Keep code simple.** Functions > classes. Flat over nested. Working over elegant.
5. **Test everything.** Write the test before or alongside the code.
6. **Commit often.** Small, working increments.
7. **Update DECISIONS.md** when making non-obvious technical choices.
8. **Update FINDINGS.md** when experiments produce results.
