# reasoning-compiler

**Verified reasoning via compilation: NL → formal language → solver → certificate → faithful explanation.**

A research system that makes LLM reasoning reliable by treating it as compilation. Instead of trusting chain-of-thought, we compile natural language into formal representations, solve with classical tools, verify via certificates, and explain from the verified artifact.

## Core ideas

- **Formalization fertility**: measures NL tokens per formal constraint. High fertility predicts LLM failure. Inspired by multilingual tokenization research.
- **Domain routing**: LLM/SLM classifies problem domain → domain-specific formal language + solver. No universal IR needed — the domain choice IS the latent variable.
- **Compile-check-repair loop**: generate formalization → typecheck → solve → verify → repair from structured errors. Formulation-graph search with backtracking.
- **Faithful explanations**: derived from solver certificates + constraint provenance. Every explanation step is machine-checkable.

## Status

🚧 Early research. See [docs/plan.md](docs/plan.md) for execution plan, [docs/sparks.md](docs/sparks.md) for idea log.

## Setup

```bash
pip install -e ".[dev]"
```

## Citation

```
reasoning-compiler: Verified Reasoning via Compilation. 2026.
https://github.com/satyan-g/reasoning-compiler
```

## License

MIT
