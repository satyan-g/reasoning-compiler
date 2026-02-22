# Workflow: claude.ai → Git → Claude Code

How to bridge research conversations (ideas, literature, architecture) with implementation (code, experiments, results).

---

## Your Two Workspaces

### claude.ai (where you are now)
- **Good for**: brainstorming, literature review, architecture discussions, writing, refining ideas
- **Produces**: docs/sparks.md, plan.md, thesis.md, proposal.md, project_organization.md
- **Limitation**: files don't persist between conversations, no git, no code execution beyond simple scripts

### Claude Code (terminal agent)
- **Good for**: writing code, running experiments, git operations, file management, debugging
- **Produces**: actual Python modules, test results, experiment outputs
- **Limitation**: less suited for long back-and-forth brainstorming

---

## Recommended Setup

### Step 1: Create the git repo (do this once, manually or with Claude Code)

```bash
# In your terminal or with Claude Code
mkdir reasoning-compiler
cd reasoning-compiler
git init

# Create the directory structure from project_organization.md
mkdir -p src/{frl,compiler,runtime,pretokenizer,nl2frl,explain,fertility}
mkdir -p data/{raw,annotated,synthetic,processed}
mkdir -p datagen experiments/{configs,runners,analysis} results
mkdir -p scripts tests papers/{fertility,verified_reasoning}

# Initialize Python package
touch src/__init__.py
touch src/frl/__init__.py src/compiler/__init__.py
touch src/runtime/__init__.py src/pretokenizer/__init__.py
touch src/nl2frl/__init__.py src/explain/__init__.py
touch src/fertility/__init__.py

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "reasoning-compiler"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "z3-solver",
    "spacy",
    "tiktoken",
    "jsonschema",
]

[project.optional-dependencies]
dev = ["pytest", "ipython", "jupyter", "matplotlib"]

[tool.pytest.ini_options]
testpaths = ["tests"]
EOF

git add -A
git commit -m "init: project skeleton"
```

### Step 2: Seed the repo with documents from claude.ai

After each claude.ai session, download the files and commit them:

```bash
# After this session, you'll have these files to add:
# - docs/sparks.md              (idea log — the most important file)
# - plan.md                (execution plan)
# - project_organization.md (repo structure + experiments)

# Copy downloaded files into repo root
cp ~/Downloads/docs/sparks.md .
cp ~/Downloads/plan.md .
cp ~/Downloads/project_organization.md .

git add docs/sparks.md plan.md project_organization.md
git commit -m "docs: add sparks, plan, and project organization from research sessions"
```

### Step 3: Use Claude Code for implementation

Open Claude Code in the repo directory. It can read all your docs:

```bash
# Start Claude Code in the repo
cd reasoning-compiler
claude

# Then tell it:
# "Read docs/sparks.md and plan.md. I want to start with Phase 0:
#  build the Z3 runner, FRL schema, and verifier for assignment problems.
#  Start with src/frl/schema.py"
```

Claude Code will:
- Read your docs to understand the architecture
- Write code that matches the design in your docs
- Run tests
- Commit incrementally

---

## The Bridge Workflow (daily practice)

```
┌──────────────────────────────────────┐
│          claude.ai session           │
│                                      │
│  Brainstorm → refine → produce docs  │
│  (docs/sparks.md, thesis.md, etc.)        │
│                                      │
│  Download updated files              │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│          Git repo (local)            │
│                                      │
│  Copy downloaded docs into repo      │
│  git add + commit                    │
│                                      │
│  docs/sparks.md  ← ideas            │
│  docs/plan.md    ← execution plan   │
│  src/...         ← code             │
│  data/...        ← datasets         │
│  results/...     ← experiment output │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│          Claude Code session         │
│                                      │
│  "Read docs/sparks.md, implement X"       │
│  Writes code, runs tests, commits    │
│                                      │
│  When you discover something new     │
│  during coding → note it in a        │
│  scratch file or bring it back to    │
│  claude.ai for deeper exploration    │
└──────────────────────────────────────┘
```

---

## Practical Tips

### 1. docs/sparks.md is the bridge document

This is the single most important file. It captures ideas from claude.ai sessions AND can be read by Claude Code for context. Keep it in the repo root. Update it from both sides:
- claude.ai adds big ideas, architecture decisions, literature findings
- Claude Code (or you manually) adds implementation learnings ("Z3 doesn't support X, had to use Y instead")

### 2. Use a DECISIONS.md for implementation choices

Create a running log of technical decisions made during coding:

```markdown
# DECISIONS.md

## 2026-02-22: FRL v0 uses JSON, not a custom DSL
Reason: faster to implement, schema-validatable, good enough for Paper 1.
Revisit: if FRL gets complex enough that JSON is unwieldy.

## 2026-02-23: Z3 Python API, not SMT-LIB text
Reason: better error messages, easier provenance tracking.
Trade-off: less portable, but we can add SMT-LIB export later.
```

### 3. Use a FINDINGS.md for experiment results

Separate from sparks (ideas) and decisions (implementation):

```markdown
# FINDINGS.md

## 2026-02-24: Fertility baseline on GSM8K
- Annotated 50 problems
- Mean fertility: 8.3 NL tokens per constraint
- Correlation with GPT-4 failure: r=0.47 (moderate, p<0.01)
- Highest fertility problems: those with implicit constraints
- → Supports Paper 1 thesis
```

### 4. Claude Code session starters

When you open Claude Code, give it context by pointing to docs:

```
"Read docs/sparks.md and plan.md for project context.
 Read DECISIONS.md for implementation choices.
 I'm working on [specific task]. 
 The relevant code is in src/[module]/."
```

### 5. When to use which tool

| Task | Use |
|------|-----|
| "What should the architecture look like?" | claude.ai |
| "Write the FRL schema dataclass" | Claude Code |
| "Is this related to text-to-SQL?" | claude.ai |
| "Debug why Z3 returns UNKNOWN" | Claude Code |
| "Review my experiment results and suggest next steps" | claude.ai |
| "Run the fertility measurement on 200 problems" | Claude Code |
| "Write the related work section" | claude.ai (then download .md) |
| "Generate 10k synthetic training examples" | Claude Code |
| "Refine the paper draft" | claude.ai |
| "Set up pytest and CI" | Claude Code |

### 6. Project Knowledge in claude.ai

You already have the ChatGPT PDF as project knowledge. You can also add:
- docs/sparks.md (upload the latest version as project knowledge)
- plan.md
- Key paper PDFs you find during literature review

This way, every new claude.ai conversation has access to your accumulated thinking without you re-explaining everything.

---

## Monday Kickoff Checklist

```
□ Create git repo with skeleton (Step 1 above)
□ Commit docs/sparks.md, plan.md, project_organization.md
□ Open Claude Code in the repo
□ Phase 0, Day 1:
  □ src/frl/schema.py — FRL v0 dataclasses
  □ src/compiler/to_z3.py — FRL → Z3 compilation  
  □ src/compiler/verify.py — independent witness verification
  □ src/runtime/solver_runner.py — Z3 wrapper
  □ tests/test_compiler.py — roundtrip test
  □ Hand-write 5 assignment puzzle FRLs, verify they solve correctly
□ Phase 0, Day 2:
  □ scripts/annotate_fertility.py — helper for manual annotation
  □ data/annotated/gsm8k_50_fertility.jsonl — annotate 50 problems
  □ src/fertility/measure.py — compute fertility metrics
  □ Check correlation with LLM failure → go/no-go for Paper 1
```

---

## Git Workflow Reminder

```
main              ← stable, passes tests
├── dev           ← integration
├── feat/frl-schema
├── feat/z3-compiler
├── feat/solver-runner
├── exp/fertility-baseline
└── paper/fertility-draft

# Feature development
git checkout -b feat/frl-schema
# ... work with Claude Code ...
git add -A && git commit -m "feat(frl): add v0 schema with Enum, Int, Bool sorts"
git checkout dev && git merge feat/frl-schema

# Experiment
git checkout -b exp/fertility-baseline
# ... run experiments ...
git add -A && git commit -m "exp(fertility): measure fertility on 50 GSM8K problems"
```
