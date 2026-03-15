"""Attempt to formalize the Zebra Puzzle in FRL.

This is the first "LLM generates FRL" test. The FRL below is what Claude
(acting as the NL→FRL compiler) produces from the Zebra Puzzle's NL clues.

Expected outcome: some clues won't fit the v0 schema. That's the point —
we discover what needs extending.

Modeling choice:
  Each category maps its values to a House position.
    nat: Nationality → House
    col: Color → House
    dri: Drink → House
    smo: Smoke → House
    pet: Pet → House

  "Englishman in red house" = nat(English) and col(Red) are the same house.
  "Norwegian in first house" = nat(Norwegian) == H1 → ASSIGNMENT.
  "Green right of ivory" = col(Green) is one position right of col(Ivory) → POSITIONAL.
  "Next to" = |pos_a - pos_b| == 1 → ADJACENT.

Schema gaps discovered:
  1. CO_OCCURRENCE — two functions map to the same house (no current constraint type)
  2. ADJACENT — positional adjacency (|f(a) - g(b)| == 1)
  3. RIGHT_OF — positional ordering (f(a) == g(b) + 1)
  4. Arithmetic on enum values — House positions need ordering
"""

from src.frl import (
    Constraint,
    ConstraintKind,
    EntityType,
    FRLInstance,
    FunctionVar,
    Provenance,
    Query,
    QueryKind,
    validate,
)


def _zebra_frl():
    """Best-effort FRL for the Zebra Puzzle using current v0 schema."""
    return FRLInstance(
        nl_text=(
            "There are five houses in a row. "
            "The Englishman lives in the red house. "
            "The Spaniard owns the dog. "
            "Coffee is drunk in the green house. "
            "The Ukrainian drinks tea. "
            "The green house is immediately to the right of the ivory house. "
            "The Old Gold smoker owns snails. "
            "Kools are smoked in the yellow house. "
            "Milk is drunk in the middle house. "
            "The Norwegian lives in the first house. "
            "The Chesterfields smoker lives next to the fox owner. "
            "Kools are smoked next to the house where the horse is kept. "
            "The Lucky Strike smoker drinks orange juice. "
            "The Japanese smokes Parliaments. "
            "The Norwegian lives next to the blue house."
        ),
        entity_types=[
            EntityType("House", ["H1", "H2", "H3", "H4", "H5"]),
            EntityType("Nationality", ["English", "Spaniard", "Ukrainian", "Norwegian", "Japanese"]),
            EntityType("Color", ["Red", "Green", "Ivory", "Yellow", "Blue"]),
            EntityType("Drink", ["Coffee", "Tea", "Milk", "OJ", "Water"]),
            EntityType("Smoke", ["OldGold", "Kools", "Chesterfields", "LuckyStrike", "Parliaments"]),
            EntityType("Pet", ["Dog", "Snails", "Fox", "Horse", "Zebra"]),
        ],
        functions=[
            FunctionVar("nat", "Nationality", "House"),
            FunctionVar("col", "Color", "House"),
            FunctionVar("dri", "Drink", "House"),
            FunctionVar("smo", "Smoke", "House"),
            FunctionVar("pet", "Pet", "House"),
        ],
        constraints=[
            # Each category: all different houses (5 values → 5 houses, bijection)
            Constraint(kind=ConstraintKind.UNIQUENESS, var="nat",
                       provenance=Provenance("Five houses, each nationality in one")),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="col",
                       provenance=Provenance("Each house a different color")),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="dri",
                       provenance=Provenance("Each house a different drink")),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="smo",
                       provenance=Provenance("Each house a different smoke")),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="pet",
                       provenance=Provenance("Each house a different pet")),

            # Clue 10: Norwegian in first house → ASSIGNMENT (expressible!)
            Constraint(kind=ConstraintKind.ASSIGNMENT, var="nat",
                       entity="Norwegian", value="H1",
                       provenance=Provenance("The Norwegian lives in the first house")),

            # Clue 9: Milk in the middle house → ASSIGNMENT (expressible!)
            Constraint(kind=ConstraintKind.ASSIGNMENT, var="dri",
                       entity="Milk", value="H3",
                       provenance=Provenance("Milk is drunk in the middle house")),

            # --- SCHEMA GAPS BELOW ---
            # The remaining clues need constraint types we don't have yet.
            # Marking them with the gap type.

            # Clue 2: Englishman lives in red house → CO_OCCURRENCE(nat, English, col, Red)
            # Clue 3: Spaniard owns dog → CO_OCCURRENCE(nat, Spaniard, pet, Dog)
            # Clue 4: Coffee in green house → CO_OCCURRENCE(dri, Coffee, col, Green)
            # Clue 5: Ukrainian drinks tea → CO_OCCURRENCE(nat, Ukrainian, dri, Tea)
            # Clue 7: Old Gold smoker owns snails → CO_OCCURRENCE(smo, OldGold, pet, Snails)
            # Clue 8: Kools in yellow house → CO_OCCURRENCE(smo, Kools, col, Yellow)
            # Clue 13: Lucky Strike smoker drinks OJ → CO_OCCURRENCE(smo, LuckyStrike, dri, OJ)
            # Clue 14: Japanese smokes Parliaments → CO_OCCURRENCE(nat, Japanese, smo, Parliaments)

            # Clue 6: Green immediately right of ivory → RIGHT_OF(col, Green, col, Ivory)
            # Clue 11: Chesterfields next to fox → ADJACENT(smo, Chesterfields, pet, Fox)
            # Clue 12: Kools next to horse → ADJACENT(smo, Kools, pet, Horse)
            # Clue 15: Norwegian next to blue → ADJACENT(nat, Norwegian, col, Blue)
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT,
                    description="Who owns the zebra? Who drinks water?"),
    )


def test_zebra_frl_validates_partial():
    """The partial FRL (only expressible constraints) should validate."""
    frl = _zebra_frl()
    errors = validate(frl)
    assert errors == [], errors


def test_zebra_frl_schema_gaps():
    """Document exactly what's missing from FRL v0 for the Zebra Puzzle."""
    gaps = {
        "CO_OCCURRENCE": {
            "description": "Two functions map to the same value (same house)",
            "example": "nat(English) == col(Red)",
            "clues": [2, 3, 4, 5, 7, 8, 13, 14],
            "count": 8,
        },
        "ADJACENT": {
            "description": "Two function outputs differ by exactly 1 (next-to)",
            "example": "|smo(Chesterfields) - pet(Fox)| == 1",
            "clues": [11, 12, 15],
            "count": 3,
        },
        "RIGHT_OF": {
            "description": "One function output is exactly 1 greater (immediately right)",
            "example": "col(Green) == col(Ivory) + 1",
            "clues": [6],
            "count": 1,
        },
    }

    total_clues = 15
    # Clue 1 ("there are five houses") is structural, not a constraint.
    # Clues 9, 10 are ASSIGNMENT (expressible). That's 2 of 14 non-structural clues.
    # UNIQUENESS constraints are implicit (not clues).
    expressible_clues = 2  # clues 9 and 10
    inexpressible = sum(g["count"] for g in gaps.values())

    assert expressible_clues + inexpressible == total_clues - 1  # minus clue 1 (structural)
    assert inexpressible == 12  # 12 of 14 constraint clues can't be expressed in v0

    # Key finding: v0 handles 2/14 = 14% of Zebra Puzzle constraint clues.
    # CO_OCCURRENCE is the biggest gap (8 clues).
    # These are all "X and Y are in the same house" constraints.
    return gaps
