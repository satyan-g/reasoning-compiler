# Viability Check Experiment 1

**Date:** 2026-02-22
**Status:** Setup complete, ready to run
**Branch:** `experiment/viability-check-1`

## Purpose

Test whether current reasoning models (Claude Sonnet 3.5, GPT-4o, Gemini) can solve high-fertility constraint problems, to determine if the fertility diagnostic paper (Paper 1) is still viable or if we should pivot to the verification story (Paper 2).

## Research Question

Do current reasoning models still fail on high-fertility constraint problems (30%+ failure rate), or has the frontier moved past the diagnostic value of Paper 1?

## Experimental Design

### Test Set
20 hard constraint-heavy problems across 3 categories:
- **Logic grids (8):** Multi-constraint puzzles with 8+ constraints and implicit uniqueness
- **Optimization (6):** NL4Opt-style problems with implicit constraints
- **FOLIO edge cases (6):** Reasoning with ambiguous quantifiers and underspecification

Some problems have deliberately incorrect ground truth to test whether models can detect inconsistencies.

### Models Tested (FREE TIER ONLY)
- Llama 3.3 70B (Groq)
- Llama 3.1 70B (Groq)
- Gemini 2.0 Flash Experimental (Google)
- Gemini 1.5 Flash (Google)

### Metrics
- **Accuracy:** % correct answers
- **Confidence calibration:** Does model express uncertainty when wrong?
- **Token cost:** Average output tokens for correct answers
- **Failure modes:** wrong_confident, wrong_uncertain, requests_clarification, partial, correct

### Decision Criteria

| Accuracy | Decision | Action |
|----------|----------|--------|
| < 70% | Proceed with Paper 1 | Models still fail frequently on high-fertility problems |
| 70-90% | Borderline | Consider which failures are interesting |
| > 90%, high tokens | Pivot to efficiency | Fertility predicts token cost, not just success |
| > 90%, low tokens | Skip to Paper 2 | Go directly to verification/certification story |

## Running the Experiment

### 1. Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API keys (both are FREE!)
export GROQ_API_KEY="gsk_..."  # Get from https://console.groq.com/
export GOOGLE_API_KEY="..."    # Get from https://aistudio.google.com/
```

### 2. Generate Problems

```bash
cd experiments/viability_check_1
python curate_problems.py
```

This creates `problems/problems.jsonl` with 20 test problems.

### 3. Run Experiment

```bash
python run_experiment.py
```

This will:
- Test all 20 problems against each configured model
- Save responses to `responses/*.jsonl`
- Rate-limit API calls appropriately
- Report progress and errors

**Expected runtime:** ~1-2 hours (free tier with rate limiting, but $0 cost!)

### 4. Analyze Results

```bash
# First run creates annotation template
python analyze_results.py

# This creates annotations_template.json
# Manually review model responses and fill in:
#   - is_correct (true/false)
#   - expresses_uncertainty (true/false)
#   - failure_mode (correct/wrong_confident/...)
#   - notes (optional)

# Save as annotations.json, then re-run:
python analyze_results.py
```

This will:
- Compute accuracy by model and category
- Calculate token costs and latency
- Apply decision criteria
- Generate `SUMMARY.md` and `DECISION.md`

## Outputs

```
experiments/viability_check_1/
├── problems/
│   ├── problems.jsonl          # 20 test problems
│   └── README.md
├── responses/
│   ├── anthropic_*_responses.jsonl
│   ├── openai_*_responses.jsonl
│   └── google_*_responses.jsonl
├── annotations_template.json   # Generated for manual review
├── annotations.json            # Manually filled evaluation
├── analysis.json               # Detailed metrics
├── SUMMARY.md                  # Results summary
└── DECISION.md                 # Go/no-go decision
```

## Next Steps

Based on `DECISION.md`:
- **Proceed with Paper 1:** Continue with fertility diagnostic as planned
- **Pivot to efficiency:** Reframe Paper 1 around token cost prediction
- **Skip to Paper 2:** Go directly to verification/certification story

## Configuration

See `experiments/configs/viability_check_1.yaml` for full experimental configuration.
