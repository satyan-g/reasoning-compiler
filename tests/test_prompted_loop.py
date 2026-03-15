"""Prompted loop test: simulate LLM generating FRL from NL.

The FRL JSON below is what an LLM would produce given the NL problem
and the FRL schema. We parse it, compile it, solve it, and verify it.

This tests the full pipeline as it would work in production:
  NL → [LLM generates JSON] → parse → validate → compile → solve → verify
"""

import json

from src.frl import FRLInstance, validate
from src.compiler.to_z3 import solve
from src.compiler.verify import verify_witness


# --- Problem: a fresh 4x4 logic grid puzzle ---

NL_PROBLEM = """
Four musicians — Alice, Bob, Carol, and Dave — each play exactly one
instrument: guitar, piano, drums, or violin. Each instrument is played
by exactly one person.

1. Alice does not play drums or violin.
2. Bob plays an instrument that is next to Carol's in the alphabetical
   ordering (drums, guitar, piano, violin).
3. Dave plays violin.
4. The guitarist and the pianist live next to each other (their instruments
   are adjacent alphabetically).

Who plays what?
"""

EXPECTED_ANSWER = {
    "Alice": "Guitar",
    "Bob": "Piano",
    "Carol": "Drums",
    "Dave": "Violin",
}

# This is what the LLM would generate — FRL as JSON.
# Simulating Claude/GPT producing this from the NL problem + schema docs.

LLM_GENERATED_FRL = """
{
  "nl_text": "Four musicians — Alice, Bob, Carol, and Dave — each play exactly one instrument: guitar, piano, drums, or violin. Each instrument is played by exactly one person. Alice does not play drums or violin. Bob plays an instrument that is next to Carol's in the alphabetical ordering. Dave plays violin. The guitarist and the pianist live next to each other.",
  "entity_types": [
    {"name": "Person", "values": ["Alice", "Bob", "Carol", "Dave"]},
    {"name": "Instrument", "values": ["Drums", "Guitar", "Piano", "Violin"]}
  ],
  "functions": [
    {"name": "plays", "domain": "Person", "codomain": "Instrument"}
  ],
  "constraints": [
    {
      "kind": "uniqueness",
      "var": "plays",
      "provenance": {"text": "each play exactly one instrument, each instrument played by one person"}
    },
    {
      "kind": "exclusion",
      "var": "plays",
      "entity": "Alice",
      "value": "Drums",
      "provenance": {"text": "Alice does not play drums"}
    },
    {
      "kind": "exclusion",
      "var": "plays",
      "entity": "Alice",
      "value": "Violin",
      "provenance": {"text": "Alice does not play violin"}
    },
    {
      "kind": "adjacent",
      "var1": "plays",
      "entity1": "Bob",
      "var2": "plays",
      "entity2": "Carol",
      "provenance": {"text": "Bob plays an instrument next to Carol's alphabetically"}
    },
    {
      "kind": "assignment",
      "var": "plays",
      "entity": "Dave",
      "value": "Violin",
      "provenance": {"text": "Dave plays violin"}
    }
  ],
  "query": {
    "kind": "find_assignment",
    "description": "Who plays what?"
  }
}
"""

# Note: Clue 4 ("guitarist and pianist are adjacent") is redundant given
# the alphabetical ordering (Guitar and Piano ARE adjacent: D,G,P,V).
# A smart LLM might note this and skip it. We skip it too.


def test_parse_llm_output():
    """Parse the LLM-generated JSON into an FRL instance."""
    frl = FRLInstance.from_json(LLM_GENERATED_FRL)
    assert len(frl.entity_types) == 2
    assert len(frl.functions) == 1
    assert len(frl.constraints) == 5


def test_validate_llm_output():
    """Validate that all references in the LLM output are correct."""
    frl = FRLInstance.from_json(LLM_GENERATED_FRL)
    errors = validate(frl)
    assert errors == [], f"Validation errors: {errors}"


def test_solve_llm_output():
    """Solve the LLM-generated FRL and check constraints are satisfied."""
    frl = FRLInstance.from_json(LLM_GENERATED_FRL)
    result = solve(frl)
    assert result.sat is True, "Expected SAT"

    w = result.witness["plays"]
    # Dave must be Violin (ASSIGNMENT constraint)
    assert w["Dave"] == "Violin"
    # Alice must not be Drums or Violin (EXCLUSION constraints)
    assert w["Alice"] in ("Guitar", "Piano")
    # Bob and Carol must be adjacent alphabetically (ADJACENT constraint)
    order = {"Drums": 0, "Guitar": 1, "Piano": 2, "Violin": 3}
    assert abs(order[w["Bob"]] - order[w["Carol"]]) == 1
    # All different (UNIQUENESS)
    assert len(set(w.values())) == 4


def test_verify_llm_output():
    """Independently verify the solution."""
    frl = FRLInstance.from_json(LLM_GENERATED_FRL)
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


# --- Negative test: LLM makes a mistake ---

LLM_WRONG_FRL = """
{
  "nl_text": "Same problem but LLM misses the adjacency constraint.",
  "entity_types": [
    {"name": "Person", "values": ["Alice", "Bob", "Carol", "Dave"]},
    {"name": "Instrument", "values": ["Drums", "Guitar", "Piano", "Violin"]}
  ],
  "functions": [
    {"name": "plays", "domain": "Person", "codomain": "Instrument"}
  ],
  "constraints": [
    {
      "kind": "uniqueness",
      "var": "plays",
      "provenance": {"text": "each play exactly one instrument"}
    },
    {
      "kind": "exclusion",
      "var": "plays",
      "entity": "Alice",
      "value": "Drums",
      "provenance": {"text": "Alice does not play drums"}
    },
    {
      "kind": "exclusion",
      "var": "plays",
      "entity": "Alice",
      "value": "Violin",
      "provenance": {"text": "Alice does not play violin"}
    },
    {
      "kind": "assignment",
      "var": "plays",
      "entity": "Dave",
      "value": "Violin",
      "provenance": {"text": "Dave plays violin"}
    }
  ],
  "query": {
    "kind": "find_assignment",
    "description": "Who plays what?"
  }
}
"""


def test_wrong_frl_still_solves_but_may_differ():
    """Missing constraint → solver finds A solution but maybe not THE solution."""
    frl = FRLInstance.from_json(LLM_WRONG_FRL)
    result = solve(frl)
    assert result.sat is True  # Still SAT — fewer constraints, more solutions

    w = result.witness["plays"]
    # Dave must still be Violin (that constraint is present)
    assert w["Dave"] == "Violin"
    # Alice must not be Drums or Violin
    assert w["Alice"] in ("Guitar", "Piano")
    # But Bob and Carol's assignment might not match expected —
    # the missing adjacency constraint means other solutions are valid
