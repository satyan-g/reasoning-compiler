"""Zebra Puzzle (Einstein's Riddle) — the classic 5-house logic grid puzzle.

This is a stress test for the FRL schema and Z3 compiler. It requires
positional reasoning (house ordering, adjacency) which pushes beyond
simple assignment constraints.

Source: https://en.wikipedia.org/wiki/Zebra_Puzzle

The 15 clues:
1.  There are five houses.
2.  The Englishman lives in the red house.
3.  The Spaniard owns the dog.
4.  Coffee is drunk in the green house.
5.  The Ukrainian drinks tea.
6.  The green house is immediately to the right of the ivory house.
7.  The Old Gold smoker owns snails.
8.  Kools are smoked in the yellow house.
9.  Milk is drunk in the middle house.
10. The Norwegian lives in the first house.
11. The Chesterfields smoker lives next to the fox owner.
12. Kools are smoked next to the house where the horse is kept.
13. The Lucky Strike smoker drinks orange juice.
14. The Japanese smokes Parliaments.
15. The Norwegian lives next to the blue house.

Solution:
  House 1: Norwegian, fox,    yellow, water,        Kools
  House 2: Ukrainian, horse,  blue,   tea,          Chesterfields
  House 3: Englishman,snails, red,    milk,         Old Gold
  House 4: Spaniard,  dog,    ivory,  orange juice, Lucky Strike
  House 5: Japanese,  zebra,  green,  coffee,       Parliaments

Answer: The German (Japanese) owns the zebra. The Norwegian drinks water.

NOTE: The version above uses the Life International 1962 version with
Nationality/Pet/Color/Drink/Smoke categories. Some versions differ slightly.
"""

import z3


def test_zebra_puzzle_z3_direct():
    """Solve the Zebra Puzzle directly in Z3 to verify our pipeline can handle it.

    This uses Z3 directly (not through FRL) as a reference implementation.
    The FRL version will come once we extend the schema for positional constraints.
    """
    s = z3.Solver()

    # 5 houses, positions 1-5
    # Each category assigns a position (house number) to each value
    nationalities = ["English", "Spaniard", "Ukrainian", "Norwegian", "Japanese"]
    colors = ["Red", "Green", "Ivory", "Yellow", "Blue"]
    drinks = ["Coffee", "Tea", "Milk", "OJ", "Water"]
    smokes = ["OldGold", "Kools", "Chesterfields", "LuckyStrike", "Parliaments"]
    pets = ["Dog", "Snails", "Fox", "Horse", "Zebra"]

    # Create integer variables: each value gets a house number 1-5
    def make_vars(names, prefix):
        vs = {n: z3.Int(f"{prefix}_{n}") for n in names}
        for v in vs.values():
            s.add(v >= 1, v <= 5)
        s.add(z3.Distinct(*vs.values()))
        return vs

    nat = make_vars(nationalities, "nat")
    col = make_vars(colors, "col")
    dri = make_vars(drinks, "dri")
    smo = make_vars(smokes, "smo")
    pet = make_vars(pets, "pet")

    # Clue 2: The Englishman lives in the red house
    s.add(nat["English"] == col["Red"])
    # Clue 3: The Spaniard owns the dog
    s.add(nat["Spaniard"] == pet["Dog"])
    # Clue 4: Coffee is drunk in the green house
    s.add(dri["Coffee"] == col["Green"])
    # Clue 5: The Ukrainian drinks tea
    s.add(nat["Ukrainian"] == dri["Tea"])
    # Clue 6: The green house is immediately to the right of the ivory house
    s.add(col["Green"] == col["Ivory"] + 1)
    # Clue 7: The Old Gold smoker owns snails
    s.add(smo["OldGold"] == pet["Snails"])
    # Clue 8: Kools are smoked in the yellow house
    s.add(smo["Kools"] == col["Yellow"])
    # Clue 9: Milk is drunk in the middle house
    s.add(dri["Milk"] == 3)
    # Clue 10: The Norwegian lives in the first house
    s.add(nat["Norwegian"] == 1)
    # Clue 11: The Chesterfields smoker lives next to the fox owner
    s.add(z3.Or(smo["Chesterfields"] == pet["Fox"] + 1,
                smo["Chesterfields"] == pet["Fox"] - 1))
    # Clue 12: Kools are smoked next to the house where the horse is kept
    s.add(z3.Or(smo["Kools"] == pet["Horse"] + 1,
                smo["Kools"] == pet["Horse"] - 1))
    # Clue 13: The Lucky Strike smoker drinks orange juice
    s.add(smo["LuckyStrike"] == dri["OJ"])
    # Clue 14: The Japanese smokes Parliaments
    s.add(nat["Japanese"] == smo["Parliaments"])
    # Clue 15: The Norwegian lives next to the blue house
    s.add(z3.Or(nat["Norwegian"] == col["Blue"] + 1,
                nat["Norwegian"] == col["Blue"] - 1))

    assert s.check() == z3.sat
    m = s.model()

    # Extract solution: build house->attributes mapping
    solution = {}
    for i in range(1, 6):
        solution[i] = {}
    for name, var in nat.items():
        solution[m.eval(var).as_long()]["nationality"] = name
    for name, var in col.items():
        solution[m.eval(var).as_long()]["color"] = name
    for name, var in dri.items():
        solution[m.eval(var).as_long()]["drink"] = name
    for name, var in smo.items():
        solution[m.eval(var).as_long()]["smoke"] = name
    for name, var in pet.items():
        solution[m.eval(var).as_long()]["pet"] = name

    # Verify the known answer
    zebra_owner = None
    water_drinker = None
    for house, attrs in solution.items():
        if attrs["pet"] == "Zebra":
            zebra_owner = attrs["nationality"]
        if attrs["drink"] == "Water":
            water_drinker = attrs["nationality"]

    assert zebra_owner == "Japanese"
    assert water_drinker == "Norwegian"

    # Verify specific house assignments
    assert solution[1]["nationality"] == "Norwegian"
    assert solution[3]["drink"] == "Milk"
    assert solution[5]["color"] == "Green"
    assert solution[4]["color"] == "Ivory"
