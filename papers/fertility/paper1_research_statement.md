# Formalization Fertility: Why LLM Reasoning Fails at the Tokenization Boundary

## Research Question

Why do large language models fail on constraint-heavy reasoning problems even when they "know" the relevant techniques? We hypothesize that the bottleneck is **encoding**, not reasoning capacity — and that this bottleneck is measurable.

## Key Idea

We introduce **formalization fertility**, a metric that captures how many natural-language tokens are required to encode each formal constraint in a problem. The concept is inspired by **tokenization fertility** in multilingual NLP, where BPE tokenizers fragment morphological units in languages like Hindi or Tamil, degrading downstream performance. We observe an analogous phenomenon in reasoning: standard LLM processing fragments the semantic-structural units (constraints, quantifiers, implicit assumptions) that matter for problem solving.

A simple example: the sentence *"Alice, Bob, and Cara must each be assigned to exactly one of three tasks, and no two people can share a task"* encodes three constraints (three unary assignment constraints + AllDifferent) in 28 tokens — a fertility of ~9.3 tokens per constraint. Problems with higher fertility are harder for LLMs to solve correctly.

## Contributions

1. **Formalization fertility as a diagnostic metric.** We define and measure the ratio of NL tokens to formal constraints across multiple reasoning benchmarks (GSM8K, logic grid puzzles, NL4Opt, FOLIO).

2. **Empirical finding: fertility predicts failure.** We show that high formalization fertility is a strong predictor of LLM reasoning failure, even after controlling for problem length and constraint count independently.

3. **Constraint pre-tokenization.** We propose a structured extraction pass — entity typing, constraint relation classification, quantifier normalization — that reduces fertility by converting NL into a compact intermediate representation before formalization.

4. **End-to-end evaluation.** We demonstrate that pre-tokenization + formal solving (via Z3) outperforms one-shot LLM reasoning in solve rate and robustness under paraphrase, and we isolate the contribution of each pipeline component through ablations.

## The Analogy

| Multilingual tokenization | Formalization |
|---------------------------|---------------|
| Morpheme | Constraint |
| Sandhi / agglutination | Implicit assumptions |
| BPE fragments morphological units | LLM tokenization fragments semantic-structural units |
| Fertility = subword tokens per word | Fertility = NL tokens per constraint |
| Fix: morphology-aware tokenization | Fix: constraint-aware pre-tokenization |

## Status

Currently in the empirical analysis phase — annotating problems with gold formalizations and measuring the fertility–failure correlation. Early results on logic grid puzzles show a clear relationship between fertility and LLM error rate.

## Target Venues

ACL/EMNLP 2026 (main), ICML TokShop (workshop), NeurIPS (neuro-symbolic track)

## Context

This is the first paper in a broader research agenda on **verified reasoning via compilation** — treating NL reasoning as a compilation problem (NL → formal language → solver → certificate) rather than a generation problem. This paper focuses on diagnosing and measuring the encoding bottleneck; subsequent work addresses the full compile–check–repair loop.

## Looking For

- Feedback on the fertility metric definition and dataset selection
- Collaborators with experience in semantic parsing, multilingual NLP, or neuro-symbolic methods
- Pointers to related work we may have missed

## Contact

[your info here]
