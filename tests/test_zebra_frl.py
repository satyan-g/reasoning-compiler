"""Zebra Puzzle formalized in FRL — full pipeline test.

All 15 clues expressed using FRL v0 + the three new constraint types
(CO_OCCURRENCE, ADJACENT, RIGHT_OF).

Source: https://en.wikipedia.org/wiki/Zebra_Puzzle
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
from src.compiler.to_z3 import solve
from src.compiler.verify import verify_witness


def _zebra_frl():
    """Complete FRL for the Zebra Puzzle — all 15 clues."""
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
            # Implicit: each category is a bijection (all different houses)
            Constraint(kind=ConstraintKind.UNIQUENESS, var="nat",
                       provenance=Provenance("Five houses, each nationality in one", implicit=True)),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="col",
                       provenance=Provenance("Each house a different color", implicit=True)),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="dri",
                       provenance=Provenance("Each house a different drink", implicit=True)),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="smo",
                       provenance=Provenance("Each house a different smoke", implicit=True)),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="pet",
                       provenance=Provenance("Each house a different pet", implicit=True)),

            # Clue 2: The Englishman lives in the red house
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="nat", entity1="English", var2="col", entity2="Red",
                       provenance=Provenance("The Englishman lives in the red house")),

            # Clue 3: The Spaniard owns the dog
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="nat", entity1="Spaniard", var2="pet", entity2="Dog",
                       provenance=Provenance("The Spaniard owns the dog")),

            # Clue 4: Coffee is drunk in the green house
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="dri", entity1="Coffee", var2="col", entity2="Green",
                       provenance=Provenance("Coffee is drunk in the green house")),

            # Clue 5: The Ukrainian drinks tea
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="nat", entity1="Ukrainian", var2="dri", entity2="Tea",
                       provenance=Provenance("The Ukrainian drinks tea")),

            # Clue 6: The green house is immediately to the right of the ivory house
            Constraint(kind=ConstraintKind.RIGHT_OF,
                       var1="col", entity1="Green", var2="col", entity2="Ivory",
                       provenance=Provenance("The green house is immediately to the right of the ivory house")),

            # Clue 7: The Old Gold smoker owns snails
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="smo", entity1="OldGold", var2="pet", entity2="Snails",
                       provenance=Provenance("The Old Gold smoker owns snails")),

            # Clue 8: Kools are smoked in the yellow house
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="smo", entity1="Kools", var2="col", entity2="Yellow",
                       provenance=Provenance("Kools are smoked in the yellow house")),

            # Clue 9: Milk is drunk in the middle house
            Constraint(kind=ConstraintKind.ASSIGNMENT, var="dri",
                       entity="Milk", value="H3",
                       provenance=Provenance("Milk is drunk in the middle house")),

            # Clue 10: The Norwegian lives in the first house
            Constraint(kind=ConstraintKind.ASSIGNMENT, var="nat",
                       entity="Norwegian", value="H1",
                       provenance=Provenance("The Norwegian lives in the first house")),

            # Clue 11: The Chesterfields smoker lives next to the fox owner
            Constraint(kind=ConstraintKind.ADJACENT,
                       var1="smo", entity1="Chesterfields", var2="pet", entity2="Fox",
                       provenance=Provenance("The Chesterfields smoker lives next to the fox owner")),

            # Clue 12: Kools are smoked next to the house where the horse is kept
            Constraint(kind=ConstraintKind.ADJACENT,
                       var1="smo", entity1="Kools", var2="pet", entity2="Horse",
                       provenance=Provenance("Kools are smoked next to the house where the horse is kept")),

            # Clue 13: The Lucky Strike smoker drinks orange juice
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="smo", entity1="LuckyStrike", var2="dri", entity2="OJ",
                       provenance=Provenance("The Lucky Strike smoker drinks orange juice")),

            # Clue 14: The Japanese smokes Parliaments
            Constraint(kind=ConstraintKind.CO_OCCURRENCE,
                       var1="nat", entity1="Japanese", var2="smo", entity2="Parliaments",
                       provenance=Provenance("The Japanese smokes Parliaments")),

            # Clue 15: The Norwegian lives next to the blue house
            Constraint(kind=ConstraintKind.ADJACENT,
                       var1="nat", entity1="Norwegian", var2="col", entity2="Blue",
                       provenance=Provenance("The Norwegian lives next to the blue house")),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT,
                    description="Who owns the zebra? Who drinks water?"),
    )


def test_zebra_frl_validates():
    """All constraints should validate against the schema."""
    frl = _zebra_frl()
    errors = validate(frl)
    assert errors == [], errors


def test_zebra_frl_solves():
    """Solve the Zebra Puzzle through the full FRL pipeline."""
    frl = _zebra_frl()
    result = solve(frl)
    assert result.sat is True
    assert result.witness is not None

    w = result.witness

    # Find who owns the zebra and who drinks water
    zebra_house = w["pet"]["Zebra"]
    water_house = w["dri"]["Water"]

    # Find nationality in those houses
    nat_by_house = {v: k for k, v in w["nat"].items()}
    zebra_owner = nat_by_house[zebra_house]
    water_drinker = nat_by_house[water_house]

    assert zebra_owner == "Japanese"
    assert water_drinker == "Norwegian"


def test_zebra_frl_verify():
    """Independently verify the witness against all FRL constraints."""
    frl = _zebra_frl()
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


def test_zebra_frl_full_solution():
    """Verify the complete house-by-house solution."""
    frl = _zebra_frl()
    result = solve(frl)
    w = result.witness

    # Expected: each value maps to its house
    # House 1: Norwegian, Yellow, Water, Kools, Fox
    assert w["nat"]["Norwegian"] == "H1"
    assert w["col"]["Yellow"] == "H1"
    assert w["dri"]["Water"] == "H1"
    assert w["smo"]["Kools"] == "H1"
    assert w["pet"]["Fox"] == "H1"

    # House 2: Ukrainian, Blue, Tea, Chesterfields, Horse
    assert w["nat"]["Ukrainian"] == "H2"
    assert w["col"]["Blue"] == "H2"
    assert w["dri"]["Tea"] == "H2"
    assert w["smo"]["Chesterfields"] == "H2"
    assert w["pet"]["Horse"] == "H2"

    # House 3: English, Red, Milk, OldGold, Snails
    assert w["nat"]["English"] == "H3"
    assert w["col"]["Red"] == "H3"
    assert w["dri"]["Milk"] == "H3"
    assert w["smo"]["OldGold"] == "H3"
    assert w["pet"]["Snails"] == "H3"

    # House 4: Spaniard, Ivory, OJ, LuckyStrike, Dog
    assert w["nat"]["Spaniard"] == "H4"
    assert w["col"]["Ivory"] == "H4"
    assert w["dri"]["OJ"] == "H4"
    assert w["smo"]["LuckyStrike"] == "H4"
    assert w["pet"]["Dog"] == "H4"

    # House 5: Japanese, Green, Coffee, Parliaments, Zebra
    assert w["nat"]["Japanese"] == "H5"
    assert w["col"]["Green"] == "H5"
    assert w["dri"]["Coffee"] == "H5"
    assert w["smo"]["Parliaments"] == "H5"
    assert w["pet"]["Zebra"] == "H5"
