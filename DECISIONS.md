# DECISIONS.md

A running log of technical decisions. Add an entry whenever a non-obvious choice is made.

---

## 2026-02-22: Project structure established

**Context**: Starting the reasoning-compiler project.

**Decision**: Separate docs (sparks, plan, thesis ideas) from code. Use docs/sparks.md as the bridge between claude.ai brainstorming and Claude Code implementation.

**Rationale**: Ideas accumulate in claude.ai conversations. Code lives in the repo. docs/sparks.md is the shared artifact both can read and update.

---

## 2026-02-22: FRL v0 targets assignment problems only

**Context**: Could try to build a universal FRL from the start.

**Decision**: v0 handles only assignment/scheduling with Enum sorts, function variables, and 5 constraint types (EXCLUSION, ASSIGNMENT, UNIQUENESS, CONDITIONAL, CARDINALITY).

**Rationale**: One domain working end-to-end proves the thesis. Multiple domains is a scaling exercise, not a research question. Don't build the router before there are multiple backends to route to.

---

## 2026-02-22: FRL uses JSON/dataclasses, not a custom DSL

**Context**: Could design a custom syntax for FRL.

**Decision**: FRL instances are Python dataclasses, serialized as JSON.

**Rationale**: Faster to implement, schema-validatable via jsonschema, readable by LLMs for structured extraction. Revisit if FRL gets complex enough that JSON is unwieldy.

---

## 2026-02-22: Domain routing deferred to Phase 3+

**Context**: The LLM-as-router architecture is a key insight (see docs/sparks.md).

**Decision**: Don't build it yet. Build one domain first. Add a second domain. Then build the router.

**Rationale**: A router with one destination is just overhead. The router becomes useful and testable only when there are multiple backends.

---

_(Add new decisions below this line)_
