# Experiment Log - Viability Check 1

**Date:** 2026-02-22
**Branch:** `experiment/viability-check-1`
**Status:** Data collection complete

## Summary

Successfully collected responses from 3 free-tier models on 20 hard constraint problems to determine if current reasoning models still fail on high-fertility problems.

## Models Tested

| Model | Provider | Status | Responses | File Size |
|-------|----------|--------|-----------|-----------|
| Llama 3.3 70B Versatile | Groq | ✓ Complete | 20/20 | 110 KB |
| Llama 3.1 8B Instant | Groq | ✓ Complete | 20/20 | 126 KB |
| Gemini 2.5 Flash | Google | ✓ Complete | 20/20 | 93 KB |
| Gemini 2.0 Flash | Google | ✗ Quota exceeded | 0/20 | - |

**Total:** 60 valid responses across 3 models

## Problems Tested

- **Logic Grids (8):** Multi-constraint puzzles with 8+ constraints
- **Optimization (6):** NL4Opt-style problems with implicit constraints
- **FOLIO Edge Cases (6):** Reasoning with ambiguous quantifiers

## Issues Encountered

### 1. Model Availability
- **Llama 3.1 70B decommissioned** - Groq deprecated this model
- **Solution:** Used Llama 3.1 8B Instant instead

### 2. Gemini Model Names
- **Initial names incorrect** - `gemini-2.0-flash-exp` and `gemini-1.5-flash` returned 404
- **Solution:** Used `gemini-2.5-flash` and `gemini-2.0-flash` (correct names)

### 3. Google SDK Deprecation
- **Warning:** `google.generativeai` package deprecated, should migrate to `google.genai`
- **Impact:** None currently, but should update for future experiments

### 4. Rate Limiting
- **Gemini 2.0 Flash hit quota** after Gemini 2.5 Flash consumed daily free tier limit
- **Impact:** Only have 3 models instead of 4, but sufficient for analysis

## Performance Observations

### Token Usage
- **Llama 3.3 70B:** ~1,500 avg output tokens (hits 4K max frequently)
- **Llama 3.1 8B:** ~1,600 avg output tokens (also hits 4K max)
- **Gemini 2.5 Flash:** ~1,400 avg output tokens

### Latency
- **Groq (Llama):** Very fast, 1-5s per problem
- **Gemini 2.5:** Slower, 7-100s per problem (avg ~25s)

## Next Steps

1. **Manual annotation** - Review all 60 responses and mark correct/incorrect
2. **Analysis** - Run `analyze_results.py` to compute metrics
3. **Decision** - Based on accuracy thresholds:
   - <70% → Proceed with Paper 1 (fertility diagnostic)
   - >90% → Pivot to Paper 2 (verification) or efficiency story

## Cost

**$0.00** - All free tier models

## Files Generated

```
responses/
├── groq_llama_3.3_70b_versatile_responses.jsonl  (110 KB, 20 problems)
├── groq_llama_3.1_8b_instant_responses.jsonl     (126 KB, 20 problems)
└── google_gemini_2.5_flash_responses.jsonl       (93 KB, 20 problems)
```

## Command History

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate problems
python curate_problems.py

# Run experiment (took ~10 min total)
python run_experiment.py

# Check available models (debugging)
python check_available_models.py
```

## Lessons Learned

1. **Always check model availability** - Free tier models change frequently
2. **Monitor quota limits** - Google has per-model daily limits on free tier
3. **Start with one model** - Test first before running all models
4. **Free tier is viable** - Got good data completely free

## Ready for Analysis

The experiment succeeded in collecting enough data (60 responses across 3 diverse models) to answer the viability question. Proceeding to manual annotation phase.
