# Test Problems for Viability Check 1

This directory contains the 20 hard constraint-heavy problems used to test
whether current reasoning models can solve high-fertility problems.

## Problem Categories

### Logic Grids (8 problems)
Multi-constraint logic puzzles with 8+ constraints and implicit uniqueness assumptions.

### Optimization (6 problems)
NL4Opt-style optimization problems with implicit constraints.

### FOLIO Edge Cases (6 problems)
Reasoning problems with ambiguous quantifiers and underspecification.

## Format

Each problem is stored as a JSON object with:
- `id`: Unique identifier
- `category`: Problem category
- `text`: Natural language problem statement
- `ground_truth`: Correct answer (for validation)
- `constraints`: List of constraints (for fertility analysis)
- `difficulty`: Expected difficulty (easy/medium/hard)
- `source`: Where the problem came from
