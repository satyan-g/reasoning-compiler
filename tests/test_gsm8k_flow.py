"""GSM8K domain: arithmetic word problems compiled to FRL → Z3.

This proves the pipeline extends beyond logic grid puzzles.
The FRL schema needs new types for numeric variables and equations.

Problem: GSM8K test #500
  "Together Lily, David, and Bodhi collected 43 insects.
   Lily found 7 more than David. David found half of what Bodhi found.
   How many insects did Lily find?"
  Answer: 16

This is a system of linear equations:
  lily + david + bodhi = 43
  lily = david + 7
  david = bodhi / 2
  solve for: lily
"""

import z3


# ============================================================
# Step 1: Direct Z3 (reference implementation, no FRL)
# ============================================================

def test_gsm8k_500_z3_direct():
    """Solve GSM8K #500 directly in Z3 as reference."""
    s = z3.Solver()

    lily = z3.Int("lily")
    david = z3.Int("david")
    bodhi = z3.Int("bodhi")

    # Constraints from NL
    s.add(lily + david + bodhi == 43)  # "together collected 43"
    s.add(lily == david + 7)            # "Lily found 7 more than David"
    s.add(david * 2 == bodhi)           # "David found half of what Bodhi found"

    # Non-negativity (implicit)
    s.add(lily >= 0, david >= 0, bodhi >= 0)

    assert s.check() == z3.sat
    m = s.model()
    assert m.eval(lily).as_long() == 16
    assert m.eval(david).as_long() == 9
    assert m.eval(bodhi).as_long() == 18


# ============================================================
# Step 2: FRL for arithmetic — what the schema needs
# ============================================================

# The current FRL schema handles enums + functions over enums.
# GSM8K needs:
#   - Integer/Real variables (not enum sorts)
#   - Linear equations (a + b + c = 43)
#   - Linear inequalities (x >= 0)
#   - Multiplicative relations (david * 2 = bodhi)
#   - Solve-for queries (find value of specific variable)
#
# New constraint types needed:
#   - LINEAR_EQ: a1*x1 + a2*x2 + ... = constant
#   - LINEAR_INEQ: a1*x1 + a2*x2 + ... >= constant (or <=)
#   - RELATION: x = y + constant, x = y * constant, etc.
#
# New entity/variable types:
#   - NumericVar: integer or real variable (not an enum)
#   - No EntityType needed — variables ARE the entities
#
# Query type:
#   - SOLVE_FOR: find value of a specific variable


# For now, we test with a lightweight JSON format that represents
# the arithmetic FRL, and compile it manually to Z3.

import json


ARITHMETIC_FRL = {
    "domain": "arithmetic",
    "nl_text": (
        "Together Lily, David, and Bodhi collected 43 insects. "
        "Lily found 7 more than David. David found half of what Bodhi found. "
        "How many insects did Lily find?"
    ),
    "variables": [
        {"name": "lily", "type": "int", "description": "insects Lily collected"},
        {"name": "david", "type": "int", "description": "insects David collected"},
        {"name": "bodhi", "type": "int", "description": "insects Bodhi collected"},
    ],
    "constraints": [
        {
            "kind": "linear_eq",
            "expr": "lily + david + bodhi = 43",
            "provenance": "Together Lily, David, and Bodhi collected 43 insects",
        },
        {
            "kind": "relation",
            "expr": "lily = david + 7",
            "provenance": "Lily found 7 more than David",
        },
        {
            "kind": "relation",
            "expr": "david * 2 = bodhi",
            "provenance": "David found half of what Bodhi found",
        },
        {
            "kind": "non_negative",
            "variables": ["lily", "david", "bodhi"],
            "provenance": "counts cannot be negative",
            "implicit": True,
        },
    ],
    "query": {
        "kind": "solve_for",
        "target": "lily",
        "description": "How many insects did Lily find?",
    },
    "expected_answer": 16,
    "metadata": {"source": "GSM8K test #500"},
}


def _compile_arithmetic_frl(frl: dict) -> tuple[z3.Solver, dict[str, z3.ArithRef]]:
    """Quick compiler for arithmetic FRL → Z3. Proof of concept."""
    s = z3.Solver()
    vars = {}

    # Create variables
    for v in frl["variables"]:
        if v["type"] == "int":
            vars[v["name"]] = z3.Int(v["name"])
        else:
            vars[v["name"]] = z3.Real(v["name"])

    # Compile constraints
    for c in frl["constraints"]:
        if c["kind"] in ("linear_eq", "relation"):
            # Parse simple expressions: "a + b + c = 43", "lily = david + 7"
            expr = c["expr"]
            lhs, rhs = expr.split("=", 1)
            lhs_z3 = _parse_expr(lhs.strip(), vars)
            rhs_z3 = _parse_expr(rhs.strip(), vars)
            s.add(lhs_z3 == rhs_z3)
        elif c["kind"] == "non_negative":
            for vname in c["variables"]:
                s.add(vars[vname] >= 0)

    return s, vars


def _parse_expr(expr: str, vars: dict[str, z3.ArithRef]) -> z3.ArithRef:
    """Parse a simple arithmetic expression. Handles +, -, * with variables and ints."""
    # Replace variable names with z3 refs for eval
    # This is a quick hack — real parser would use AST
    env = dict(vars)
    try:
        return eval(expr, {"__builtins__": {}}, env)
    except Exception:
        raise ValueError(f"Cannot parse expression: {expr}")


def test_gsm8k_500_arithmetic_frl():
    """Solve GSM8K #500 through the arithmetic FRL pipeline."""
    frl = ARITHMETIC_FRL
    s, vars = _compile_arithmetic_frl(frl)

    assert s.check() == z3.sat
    m = s.model()

    target = frl["query"]["target"]
    answer = m.eval(vars[target]).as_long()
    expected = frl["expected_answer"]

    assert answer == expected, f"Got {answer}, expected {expected}"

    # Extract full witness
    witness = {name: m.eval(var).as_long() for name, var in vars.items()}
    assert witness == {"lily": 16, "david": 9, "bodhi": 18}


def test_gsm8k_500_verify_arithmetic():
    """Verify the arithmetic solution independently (no Z3)."""
    witness = {"lily": 16, "david": 9, "bodhi": 18}

    # Check each constraint manually
    assert witness["lily"] + witness["david"] + witness["bodhi"] == 43
    assert witness["lily"] == witness["david"] + 7
    assert witness["david"] * 2 == witness["bodhi"]
    assert all(v >= 0 for v in witness.values())


# ============================================================
# Step 3: Domain classification
# ============================================================

def test_domain_classification():
    """Simple heuristic domain classifier. Proves the routing concept."""
    logic_grid_problem = (
        "There are 3 houses. Each house has a different color. "
        "The red house is next to the blue house."
    )
    arithmetic_problem = (
        "Together Lily, David, and Bodhi collected 43 insects. "
        "Lily found 7 more than David."
    )

    def classify_domain(nl_text: str) -> str:
        """Heuristic domain classifier. Replace with learned model later."""
        arithmetic_signals = [
            "how many", "how much", "total", "altogether", "per day",
            "per week", "cost", "price", "earned", "spent", "collected",
            "more than", "less than", "half of", "twice", "times",
        ]
        grid_signals = [
            "houses", "next to", "left of", "right of", "same house",
            "favorite color", "each person", "each house", "clue",
        ]
        text_lower = nl_text.lower()
        arith_score = sum(1 for s in arithmetic_signals if s in text_lower)
        grid_score = sum(1 for s in grid_signals if s in text_lower)

        if arith_score > grid_score:
            return "arithmetic"
        elif grid_score > arith_score:
            return "logic_grid"
        else:
            return "unknown"

    assert classify_domain(logic_grid_problem) == "logic_grid"
    assert classify_domain(arithmetic_problem) == "arithmetic"


# ============================================================
# Step 4: What extending the FRL schema requires
# ============================================================

def test_schema_extension_requirements():
    """Document what's needed to properly integrate arithmetic into FRL."""
    requirements = {
        "new_variable_type": {
            "NumericVar": "Integer or real variable (not enum)",
            "fields": ["name", "type (int/real)", "description"],
        },
        "new_constraint_types": {
            "LINEAR_EQ": "a1*x1 + a2*x2 + ... = constant",
            "LINEAR_INEQ": "a1*x1 + a2*x2 + ... >= or <= constant",
            "RELATION": "x = f(y) where f is +, -, *, /",
            "NON_NEGATIVE": "x >= 0 (implicit for counts)",
        },
        "new_query_type": {
            "SOLVE_FOR": "Find value of specific variable(s)",
        },
        "what_stays_the_same": [
            "Provenance tracking",
            "JSON serialization",
            "Validation framework",
            "Independent verifier pattern",
            "Solver runner (compile → solve → extract witness)",
        ],
    }
    # The key point: the PIPELINE stays the same.
    # NL → FRL → Z3 → witness → verify.
    # Only the FRL schema and compiler need domain-specific extensions.
    assert len(requirements["what_stays_the_same"]) == 5
