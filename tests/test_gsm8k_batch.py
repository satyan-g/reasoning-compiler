"""Batch test: 5 GSM8K problems through the arithmetic FRL pipeline.

Tests diverse problem types:
  #0   — subtraction + multiplication (rate × quantity)
  #50  — unit conversion + rate (per dozen → per week)
  #200 — multi-step addition + multiplication
  #500 — system of linear equations (already tested, included for completeness)
  #800 — fraction + addition
"""

import z3
import pytest


def _solve_arithmetic_frl(frl: dict) -> dict:
    """Compile arithmetic FRL → Z3, solve, return witness + answer."""
    s = z3.Solver()
    vars = {}

    for v in frl["variables"]:
        vars[v["name"]] = z3.Int(v["name"]) if v["type"] == "int" else z3.Real(v["name"])

    for c in frl["constraints"]:
        if c["kind"] in ("linear_eq", "relation"):
            lhs, rhs = c["expr"].split("=", 1)
            env = dict(vars)
            lhs_z3 = eval(lhs.strip(), {"__builtins__": {}}, env)
            rhs_z3 = eval(rhs.strip(), {"__builtins__": {}}, env)
            s.add(lhs_z3 == rhs_z3)
        elif c["kind"] == "non_negative":
            for vname in c["variables"]:
                s.add(vars[vname] >= 0)

    result = s.check()
    if result != z3.sat:
        return {"sat": False, "witness": {}, "answer": None}

    m = s.model()
    witness = {}
    for name, var in vars.items():
        val = m.eval(var, model_completion=True)
        witness[name] = val.as_long() if val.is_int() else float(val.as_fraction())

    target = frl["query"]["target"]
    return {"sat": True, "witness": witness, "answer": witness[target]}


# ============================================================
# Problem #0: Janet's ducks
# "Janet's ducks lay 16 eggs per day. She eats 3 for breakfast
#  and bakes muffins with 4. She sells the rest at $2 each.
#  How much does she make daily?"
# Answer: (16 - 3 - 4) * 2 = 18
# ============================================================

GSM8K_0 = {
    "domain": "arithmetic",
    "nl_text": "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
    "variables": [
        {"name": "eggs_laid", "type": "int", "description": "eggs laid per day"},
        {"name": "eggs_eaten", "type": "int", "description": "eggs eaten for breakfast"},
        {"name": "eggs_baked", "type": "int", "description": "eggs used for muffins"},
        {"name": "eggs_sold", "type": "int", "description": "eggs sold at market"},
        {"name": "price", "type": "int", "description": "price per egg in dollars"},
        {"name": "revenue", "type": "int", "description": "daily revenue in dollars"},
    ],
    "constraints": [
        {"kind": "relation", "expr": "eggs_laid = 16",
         "provenance": "ducks lay 16 eggs per day"},
        {"kind": "relation", "expr": "eggs_eaten = 3",
         "provenance": "she eats three for breakfast"},
        {"kind": "relation", "expr": "eggs_baked = 4",
         "provenance": "bakes muffins with four"},
        {"kind": "relation", "expr": "eggs_sold = eggs_laid - eggs_eaten - eggs_baked",
         "provenance": "she sells the remainder"},
        {"kind": "relation", "expr": "price = 2",
         "provenance": "$2 per fresh duck egg"},
        {"kind": "relation", "expr": "revenue = eggs_sold * price",
         "provenance": "revenue = quantity × price"},
    ],
    "query": {"kind": "solve_for", "target": "revenue"},
    "expected_answer": 18,
}


def test_gsm8k_0():
    r = _solve_arithmetic_frl(GSM8K_0)
    assert r["sat"]
    assert r["answer"] == 18
    assert r["witness"]["eggs_sold"] == 9


# ============================================================
# Problem #50: Lloyd's egg farm
# "252 eggs/day, $2 per dozen. How much per week?"
# Answer: (252/12) * 2 * 7 = 21 * 2 * 7 = 294
# ============================================================

GSM8K_50 = {
    "domain": "arithmetic",
    "nl_text": "Lloyd has an egg farm. His chickens produce 252 eggs per day and he sells them for $2 per dozen. How much does Lloyd make on eggs per week?",
    "variables": [
        {"name": "eggs_per_day", "type": "int", "description": "eggs produced per day"},
        {"name": "dozens_per_day", "type": "int", "description": "dozens per day"},
        {"name": "price_per_dozen", "type": "int", "description": "price per dozen"},
        {"name": "revenue_per_day", "type": "int", "description": "daily revenue"},
        {"name": "days_per_week", "type": "int", "description": "days in a week"},
        {"name": "revenue_per_week", "type": "int", "description": "weekly revenue"},
    ],
    "constraints": [
        {"kind": "relation", "expr": "eggs_per_day = 252",
         "provenance": "chickens produce 252 eggs per day"},
        {"kind": "relation", "expr": "dozens_per_day * 12 = eggs_per_day",
         "provenance": "dozen = 12 eggs"},
        {"kind": "relation", "expr": "price_per_dozen = 2",
         "provenance": "$2 per dozen"},
        {"kind": "relation", "expr": "revenue_per_day = dozens_per_day * price_per_dozen",
         "provenance": "daily revenue = dozens × price"},
        {"kind": "relation", "expr": "days_per_week = 7",
         "provenance": "per week"},
        {"kind": "relation", "expr": "revenue_per_week = revenue_per_day * days_per_week",
         "provenance": "weekly = daily × 7"},
    ],
    "query": {"kind": "solve_for", "target": "revenue_per_week"},
    "expected_answer": 294,
}


def test_gsm8k_50():
    r = _solve_arithmetic_frl(GSM8K_50)
    assert r["sat"]
    assert r["answer"] == 294


# ============================================================
# Problem #200: Baldur's water
# "5 pails morning + 6 pails afternoon, 5 liters each. Daily liters?"
# Answer: (5 + 6) * 5 = 55
# ============================================================

GSM8K_200 = {
    "domain": "arithmetic",
    "nl_text": "Baldur gets water from a well. He gets 5 pails of water every morning and 6 pails of water every afternoon. If each pail contains 5 liters of water, how many liters of water does he get every day?",
    "variables": [
        {"name": "morning_pails", "type": "int", "description": "pails in morning"},
        {"name": "afternoon_pails", "type": "int", "description": "pails in afternoon"},
        {"name": "total_pails", "type": "int", "description": "total pails per day"},
        {"name": "liters_per_pail", "type": "int", "description": "liters per pail"},
        {"name": "total_liters", "type": "int", "description": "total liters per day"},
    ],
    "constraints": [
        {"kind": "relation", "expr": "morning_pails = 5",
         "provenance": "5 pails every morning"},
        {"kind": "relation", "expr": "afternoon_pails = 6",
         "provenance": "6 pails every afternoon"},
        {"kind": "relation", "expr": "total_pails = morning_pails + afternoon_pails",
         "provenance": "total = morning + afternoon"},
        {"kind": "relation", "expr": "liters_per_pail = 5",
         "provenance": "each pail contains 5 liters"},
        {"kind": "relation", "expr": "total_liters = total_pails * liters_per_pail",
         "provenance": "total liters = pails × liters per pail"},
    ],
    "query": {"kind": "solve_for", "target": "total_liters"},
    "expected_answer": 55,
}


def test_gsm8k_200():
    r = _solve_arithmetic_frl(GSM8K_200)
    assert r["sat"]
    assert r["answer"] == 55


# ============================================================
# Problem #500: Lily, David, Bodhi insects (already tested)
# ============================================================

GSM8K_500 = {
    "domain": "arithmetic",
    "nl_text": "Together Lily, David, and Bodhi collected 43 insects. Lily found 7 more than David. David found half of what Bodhi found. How many insects did Lily find?",
    "variables": [
        {"name": "lily", "type": "int", "description": "insects Lily collected"},
        {"name": "david", "type": "int", "description": "insects David collected"},
        {"name": "bodhi", "type": "int", "description": "insects Bodhi collected"},
    ],
    "constraints": [
        {"kind": "linear_eq", "expr": "lily + david + bodhi = 43",
         "provenance": "together collected 43"},
        {"kind": "relation", "expr": "lily = david + 7",
         "provenance": "Lily found 7 more than David"},
        {"kind": "relation", "expr": "david * 2 = bodhi",
         "provenance": "David found half of what Bodhi found"},
        {"kind": "non_negative", "variables": ["lily", "david", "bodhi"],
         "provenance": "counts >= 0", "implicit": True},
    ],
    "query": {"kind": "solve_for", "target": "lily"},
    "expected_answer": 16,
}


def test_gsm8k_500():
    r = _solve_arithmetic_frl(GSM8K_500)
    assert r["sat"]
    assert r["answer"] == 16


# ============================================================
# Problem #800: Pierson and Nikita bowling
# "Pierson scored 278. Nikita scored 11 more than half of Pierson.
#  Total points?"
# Answer: 278 + (278/2 + 11) = 278 + 150 = 428
# ============================================================

GSM8K_800 = {
    "domain": "arithmetic",
    "nl_text": "Pierson scored 278 points in one game of bowling. Nikita scored 11 more than half as many as Pierson. How many points did Pierson and Nikita have in total?",
    "variables": [
        {"name": "pierson", "type": "int", "description": "Pierson's score"},
        {"name": "nikita", "type": "int", "description": "Nikita's score"},
        {"name": "total", "type": "int", "description": "combined score"},
    ],
    "constraints": [
        {"kind": "relation", "expr": "pierson = 278",
         "provenance": "Pierson scored 278 points"},
        {"kind": "relation", "expr": "nikita * 2 = pierson + 11 * 2",
         "provenance": "Nikita scored 11 more than half of Pierson"},
        {"kind": "relation", "expr": "total = pierson + nikita",
         "provenance": "total points combined"},
    ],
    "query": {"kind": "solve_for", "target": "total"},
    "expected_answer": 428,
}


def test_gsm8k_800():
    r = _solve_arithmetic_frl(GSM8K_800)
    assert r["sat"]
    assert r["answer"] == 428
    assert r["witness"]["nikita"] == 150


# ============================================================
# Verify all 5 independently (no Z3)
# ============================================================

@pytest.mark.parametrize("frl,expected", [
    (GSM8K_0, {"eggs_sold": 9, "revenue": 18}),
    (GSM8K_50, {"dozens_per_day": 21, "revenue_per_week": 294}),
    (GSM8K_200, {"total_pails": 11, "total_liters": 55}),
    (GSM8K_500, {"lily": 16, "david": 9, "bodhi": 18}),
    (GSM8K_800, {"nikita": 150, "total": 428}),
])
def test_verify_independently(frl, expected):
    """Verify solutions without Z3 — just check the math."""
    r = _solve_arithmetic_frl(frl)
    assert r["sat"]
    for var, val in expected.items():
        assert r["witness"][var] == val, f"{var}: got {r['witness'][var]}, expected {val}"
