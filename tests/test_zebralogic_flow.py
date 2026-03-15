"""Full prompted loop flow on a real ZebraLogic puzzle.

Puzzle: lgp-test-3x3-24
3 houses, 3 people, 3 colors, 3 children.

This file documents the FULL flow:
  1. NL puzzle from ZebraLogic
  2. LLM (Claude) generates FRL as JSON
  3. Parse → Validate → Compile → Solve → Verify
  4. If wrong: examine error, retry with corrected FRL
  5. Extract traces at each stage
"""

import json

from src.frl import FRLInstance, validate
from src.compiler.to_z3 import compile_to_z3, solve
from src.compiler.verify import verify_witness


NL_PUZZLE = """
There are 3 houses, numbered 1 to 3 from left to right. Each house is
occupied by a different person. Each house has a unique attribute for each
of the following characteristics:
 - Each person has a unique name: Peter, Eric, Arnold
 - Each person has a favorite color: red, white, yellow
 - Each mother is accompanied by their child: Fred, Meredith, Bella

Clues:
1. Arnold is the person whose favorite color is red.
2. The person whose child is named Fred is somewhere to the left of Eric.
3. The person whose favorite color is red is in the second house.
4. The person whose child is named Bella is in the first house.
5. The person who loves white is the person whose child is named Meredith.
"""


# ============================================================
# ATTEMPT 1: LLM generates FRL
# ============================================================

ATTEMPT_1 = """
{
  "nl_text": "3 houses, 3 people (Peter, Eric, Arnold), 3 colors (red, white, yellow), 3 children (Fred, Meredith, Bella). Arnold=red, Fred's parent left of Eric, red=house 2, Bella's parent=house 1, white=Meredith.",
  "entity_types": [
    {"name": "House", "values": ["H1", "H2", "H3"]},
    {"name": "Name", "values": ["Peter", "Eric", "Arnold"]},
    {"name": "Color", "values": ["Red", "White", "Yellow"]},
    {"name": "Child", "values": ["Fred", "Meredith", "Bella"]}
  ],
  "functions": [
    {"name": "name", "domain": "Name", "codomain": "House"},
    {"name": "color", "domain": "Color", "codomain": "House"},
    {"name": "child", "domain": "Child", "codomain": "House"}
  ],
  "constraints": [
    {
      "kind": "uniqueness",
      "var": "name",
      "provenance": {"text": "Each house occupied by different person", "implicit": true}
    },
    {
      "kind": "uniqueness",
      "var": "color",
      "provenance": {"text": "Each house has unique color", "implicit": true}
    },
    {
      "kind": "uniqueness",
      "var": "child",
      "provenance": {"text": "Each house has unique child", "implicit": true}
    },
    {
      "kind": "co_occurrence",
      "var1": "name",
      "entity1": "Arnold",
      "var2": "color",
      "entity2": "Red",
      "provenance": {"text": "Arnold is the person whose favorite color is red"}
    },
    {
      "kind": "assignment",
      "var": "color",
      "entity": "Red",
      "value": "H2",
      "provenance": {"text": "The person whose favorite color is red is in the second house"}
    },
    {
      "kind": "assignment",
      "var": "child",
      "entity": "Bella",
      "value": "H1",
      "provenance": {"text": "The person whose child is named Bella is in the first house"}
    },
    {
      "kind": "co_occurrence",
      "var1": "color",
      "entity1": "White",
      "var2": "child",
      "entity2": "Meredith",
      "provenance": {"text": "The person who loves white is the person whose child is named Meredith"}
    }
  ],
  "query": {
    "kind": "find_assignment",
    "description": "Assign people, colors, and children to houses"
  },
  "metadata": {"source": "ZebraLogic lgp-test-3x3-24"}
}
"""

# NOTE: Clue 2 ("Fred's parent is left of Eric") requires a LEFT_OF
# constraint type we don't have yet! LEFT_OF is weaker than RIGHT_OF
# (it means index < other index, not necessarily adjacent).
# Let's see what happens without it first.


def test_attempt_1_parse():
    """Stage 1: Parse LLM output."""
    frl = FRLInstance.from_json(ATTEMPT_1)
    assert len(frl.constraints) == 7
    print(f"PARSE OK: {len(frl.constraints)} constraints, {len(frl.entity_types)} entity types")


def test_attempt_1_validate():
    """Stage 2: Validate references."""
    frl = FRLInstance.from_json(ATTEMPT_1)
    errors = validate(frl)
    assert errors == [], f"VALIDATION FAILED: {errors}"
    print("VALIDATE OK: all references valid")


def test_attempt_1_solve():
    """Stage 3: Compile and solve. Expect SAT but possibly wrong — missing clue 2."""
    frl = FRLInstance.from_json(ATTEMPT_1)
    result = solve(frl)
    assert result.sat is True

    w = result.witness
    print("SOLVE OK (SAT). Witness:")
    # Build house-centric view
    for h in ["H1", "H2", "H3"]:
        name = next(k for k, v in w["name"].items() if v == h)
        color = next(k for k, v in w["color"].items() if v == h)
        child = next(k for k, v in w["child"].items() if v == h)
        print(f"  {h}: {name}, {color}, {child}")

    # Check known constraints
    assert w["name"]["Arnold"] == "H2", "Arnold should be in H2 (clues 1+3)"
    assert w["color"]["Red"] == "H2", "Red should be in H2 (clue 3)"
    assert w["child"]["Bella"] == "H1", "Bella in H1 (clue 4)"

    # Clue 2 is MISSING — Fred's parent might not be left of Eric
    # This is the gap. Let's check:
    fred_house = int(w["child"]["Fred"][1])
    eric_house = int(w["name"]["Eric"][1])
    clue_2_satisfied = fred_house < eric_house
    print(f"\n  Clue 2 check: Fred in H{fred_house}, Eric in H{eric_house} "
          f"-> {'SATISFIED' if clue_2_satisfied else 'VIOLATED (need LEFT_OF)'}")

    return clue_2_satisfied


def test_attempt_1_verify():
    """Stage 4: Independent verification."""
    frl = FRLInstance.from_json(ATTEMPT_1)
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    # Should pass — verifier only checks constraints we expressed
    assert vr.valid is True, vr.violations
    print("VERIFY OK: all expressed constraints satisfied")
    print("WARNING: clue 2 not expressed in FRL — solution may violate it")


# ============================================================
# ATTEMPT 2: Fix by adding LEFT_OF constraint
# We don't have LEFT_OF in the schema yet.
# Workaround: model "left of" as a set of exclusion constraints.
# If Fred is left of Eric, and there are 3 houses:
#   - Eric cannot be in H1 (Fred must be further left, impossible)
#   - If Eric is in H2, Fred must be in H1
#   - If Eric is in H3, Fred can be in H1 or H2
# Simplest encoding: for each pair where Fred's house >= Eric's house,
# add a constraint that blocks it. But that requires disjunction.
#
# Alternative: use CONDITIONAL constraints.
# If child(Fred) == H2, then name(Eric) == H3
# If child(Fred) == H3, then name(Eric) cannot exist left of or at H3...
#
# Actually simplest: just assert name(Eric) != H1.
# Because if Eric is in H1, Fred can't be to his left.
# And add: if Eric is in H2, Fred must be in H1.
# ============================================================

ATTEMPT_2 = """
{
  "nl_text": "Same puzzle, now with clue 2 encoded as conditional constraints.",
  "entity_types": [
    {"name": "House", "values": ["H1", "H2", "H3"]},
    {"name": "Name", "values": ["Peter", "Eric", "Arnold"]},
    {"name": "Color", "values": ["Red", "White", "Yellow"]},
    {"name": "Child", "values": ["Fred", "Meredith", "Bella"]}
  ],
  "functions": [
    {"name": "name", "domain": "Name", "codomain": "House"},
    {"name": "color", "domain": "Color", "codomain": "House"},
    {"name": "child", "domain": "Child", "codomain": "House"}
  ],
  "constraints": [
    {"kind": "uniqueness", "var": "name",
     "provenance": {"text": "unique names", "implicit": true}},
    {"kind": "uniqueness", "var": "color",
     "provenance": {"text": "unique colors", "implicit": true}},
    {"kind": "uniqueness", "var": "child",
     "provenance": {"text": "unique children", "implicit": true}},

    {"kind": "co_occurrence", "var1": "name", "entity1": "Arnold",
     "var2": "color", "entity2": "Red",
     "provenance": {"text": "Clue 1: Arnold's favorite color is red"}},

    {"kind": "assignment", "var": "color", "entity": "Red", "value": "H2",
     "provenance": {"text": "Clue 3: Red is in house 2"}},

    {"kind": "assignment", "var": "child", "entity": "Bella", "value": "H1",
     "provenance": {"text": "Clue 4: Bella's parent is in house 1"}},

    {"kind": "co_occurrence", "var1": "color", "entity1": "White",
     "var2": "child", "entity2": "Meredith",
     "provenance": {"text": "Clue 5: White lover has child Meredith"}},

    {"kind": "exclusion", "var": "name", "entity": "Eric", "value": "H1",
     "provenance": {"text": "Clue 2: Fred's parent is left of Eric, so Eric not in H1"}},

    {"kind": "conditional",
     "condition_var": "name", "condition_entity": "Eric", "condition_value": "H2",
     "consequence_var": "child", "consequence_entity": "Fred", "consequence_value": "H1",
     "provenance": {"text": "Clue 2: If Eric in H2, Fred must be in H1"}}
  ],
  "query": {
    "kind": "find_assignment",
    "description": "Assign people, colors, and children to houses"
  },
  "metadata": {"source": "ZebraLogic lgp-test-3x3-24", "attempt": 2}
}
"""


def test_attempt_2_full_pipeline():
    """Attempt 2: with clue 2 encoded. Full pipeline."""
    frl = FRLInstance.from_json(ATTEMPT_2)

    # Validate
    errors = validate(frl)
    assert errors == [], f"VALIDATION FAILED: {errors}"

    # Solve
    result = solve(frl)
    assert result.sat is True

    w = result.witness

    # Build house-centric view
    print("ATTEMPT 2 — Full solution:")
    for h in ["H1", "H2", "H3"]:
        name = next(k for k, v in w["name"].items() if v == h)
        color = next(k for k, v in w["color"].items() if v == h)
        child = next(k for k, v in w["child"].items() if v == h)
        print(f"  {h}: {name}, {color}, {child}")

    # Verify all constraints including clue 2
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, f"VERIFY FAILED: {vr.violations}"

    # Manual check of all 5 clues
    assert w["name"]["Arnold"] == w["color"]["Red"], "Clue 1: Arnold = Red"
    assert w["color"]["Red"] == "H2", "Clue 3: Red = H2"
    assert w["child"]["Bella"] == "H1", "Clue 4: Bella = H1"
    assert w["color"]["White"] == w["child"]["Meredith"], "Clue 5: White = Meredith"

    fred_h = int(w["child"]["Fred"][1])
    eric_h = int(w["name"]["Eric"][1])
    assert fred_h < eric_h, f"Clue 2: Fred({fred_h}) should be left of Eric({eric_h})"

    print("\nAll 5 clues verified. Solution is correct.")


def test_schema_gap_discovered():
    """Document the schema gap found during this exercise."""
    gap = {
        "LEFT_OF": {
            "description": "index(var1(entity1)) < index(var2(entity2))",
            "example": "child(Fred) is in a house to the left of name(Eric)",
            "current_workaround": "EXCLUSION + CONDITIONAL (verbose, error-prone)",
            "recommendation": "Add LEFT_OF constraint type to FRL schema",
        }
    }
    # The workaround for clue 2 required 2 constraints instead of 1.
    # A LEFT_OF type would make this a single constraint.
    # Also need: RIGHT_OF_STRICT (not adjacent, just greater index)
    # Current RIGHT_OF means "immediately right" (diff == 1).
    # Need: BEFORE/AFTER for "somewhere left/right of".
    print("SCHEMA GAP: LEFT_OF (strict ordering, not adjacent)")
    print("  Current RIGHT_OF means 'immediately right' (diff == 1)")
    print("  Need BEFORE/AFTER for 'somewhere left/right of'")
