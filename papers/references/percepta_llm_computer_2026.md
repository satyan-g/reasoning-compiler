# Percepta: Can LLMs Be Computers?

**Source:** https://www.percepta.ai/blog/can-llms-be-computers
**Authors:** Christos Tzamos et al. (Percepta)
**Date:** March 11, 2026

---

## What They Claim

LLMs can reason about computation but cannot reliably execute it — they delegate to external tools. Percepta addresses this by building an in-model executor: C programs compiled to WebAssembly tokens are executed step-by-step within the transformer's own inference loop, with no external round-trip. A 2D attention head restriction enables O(log t) decoding via convex-hull queries, making million-step execution traces practical. They demonstrate 100% accuracy on hard constraint-satisfaction benchmarks (Sudoku) and combinatorial optimization (Hungarian algorithm).

## Methodological Relevance to Our Work

**Same diagnosis, different layer.** Both projects identify that LLMs fail at structured reasoning. Percepta targets the *execution* bottleneck; we target the *encoding* bottleneck (NL → formal constraints). These are complementary, not competing.

**Their inputs are already formalized.** All demos start with structured inputs (cost matrices, Sudoku grids). The NL-to-formal gap — the problem our fertility metric measures — is entirely untouched by their work.

**Strengthens our Paper 1 motivation.** If execution is increasingly solvable (as Percepta demonstrates), then encoding becomes the clearly remaining hard problem. We can cite this to sharpen focus on the encoding layer.

**Contrasting correctness guarantees (relevant to Paper 2).** They claim correctness via compiler correctness ("if the compiled solver is correct, execution is correct"). We claim correctness via mathematical certificates that are independently verifiable. Their guarantee still requires correct problem formulation upstream — which is exactly what fertility measures. Open question: which approach is more robust under adversarial or ambiguous NL inputs?

**Potential long-term connection (speculative).** An in-model executor could eventually replace the external solver in our pipeline (NL → pre-tokenizer → FRL → compiled WASM → in-model execution), eliminating the external dependency while preserving the encoding/verification story. Only relevant if 2D-head models prove trainable at scale.
