"""Tests for FRL → Z3 compiler and independent verifier.

Five hand-written problems covering all constraint types.
"""

from src.frl import (
    CardinalityOp,
    CompareOp,
    Constraint,
    ConstraintKind,
    EntityType,
    FRLInstance,
    FunctionVar,
    Provenance,
    Query,
    QueryKind,
)
from src.compiler.to_z3 import solve
from src.compiler.verify import verify_witness


# --- Problem 1: Simple 3x3 with EXCLUSION ---


def _problem_1():
    """Alice, Bob, Carol → Setup, Cooking, Cleanup. Alice refuses Cleanup."""
    return FRLInstance(
        nl_text=(
            "Three friends — Alice, Bob, and Carol — each volunteer for exactly one task. "
            "The tasks are Setup, Cooking, and Cleanup. Each task is done by exactly one person. "
            "Alice refuses to do Cleanup."
        ),
        entity_types=[
            EntityType("Person", ["Alice", "Bob", "Carol"]),
            EntityType("Task", ["Setup", "Cooking", "Cleanup"]),
        ],
        functions=[FunctionVar("assign", "Person", "Task")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("each volunteer for exactly one task"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Alice",
                value="Cleanup",
                provenance=Provenance("Alice refuses to do Cleanup"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )


def test_problem_1_sat():
    frl = _problem_1()
    result = solve(frl)
    assert result.sat is True
    assert result.witness is not None
    assert result.witness["assign"]["Alice"] != "Cleanup"


def test_problem_1_verify():
    frl = _problem_1()
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


# --- Problem 2: 3x3 with CONDITIONAL ---


def _problem_2():
    """Dan, Eve, Frank → Morning, Afternoon, Night.
    If Dan works Morning, Eve works Night. Frank cannot work Morning."""
    return FRLInstance(
        nl_text=(
            "Dan, Eve, and Frank must each work exactly one shift: Morning, Afternoon, or Night. "
            "No two employees work the same shift. If Dan works Morning, then Eve works Night. "
            "Frank cannot work Morning."
        ),
        entity_types=[
            EntityType("Person", ["Dan", "Eve", "Frank"]),
            EntityType("Shift", ["Morning", "Afternoon", "Night"]),
        ],
        functions=[FunctionVar("assign", "Person", "Shift")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("No two employees work the same shift"),
            ),
            Constraint(
                kind=ConstraintKind.CONDITIONAL,
                condition_var="assign",
                condition_entity="Dan",
                condition_value="Morning",
                consequence_var="assign",
                consequence_entity="Eve",
                consequence_value="Night",
                provenance=Provenance("If Dan works Morning, then Eve works Night"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Frank",
                value="Morning",
                provenance=Provenance("Frank cannot work Morning"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )


def test_problem_2_sat():
    frl = _problem_2()
    result = solve(frl)
    assert result.sat is True
    w = result.witness["assign"]
    assert w["Frank"] != "Morning"
    # Check conditional: if Dan has Morning, Eve must have Night
    if w["Dan"] == "Morning":
        assert w["Eve"] == "Night"


def test_problem_2_verify():
    frl = _problem_2()
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


# --- Problem 3: 4x4 with CARDINALITY ---


def _problem_3():
    """Grace, Hank, Iris, Jay → Math, Physics, Chemistry, Biology.
    Grace not in Chemistry or Biology. Hank not in Math.
    Iris in Physics or Chemistry (at least 1 of those two assigned to Iris — modeled as exclusions)."""
    return FRLInstance(
        nl_text=(
            "Four students — Grace, Hank, Iris, and Jay — each join one of four groups: "
            "Math, Physics, Chemistry, Biology. Each group has exactly one student. "
            "Grace will not join Chemistry or Biology. Hank will not join Math. "
            "Iris must join either Physics or Chemistry."
        ),
        entity_types=[
            EntityType("Person", ["Grace", "Hank", "Iris", "Jay"]),
            EntityType("Group", ["Math", "Physics", "Chemistry", "Biology"]),
        ],
        functions=[FunctionVar("assign", "Person", "Group")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("each join one group, each group has one student"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Grace",
                value="Chemistry",
                provenance=Provenance("Grace will not join Chemistry"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Grace",
                value="Biology",
                provenance=Provenance("Grace will not join Biology"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Hank",
                value="Math",
                provenance=Provenance("Hank will not join Math"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Iris",
                value="Math",
                provenance=Provenance("Iris must join Physics or Chemistry", confidence=0),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Iris",
                value="Biology",
                provenance=Provenance("Iris must join Physics or Chemistry", confidence=0),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )


def test_problem_3_sat():
    frl = _problem_3()
    result = solve(frl)
    assert result.sat is True
    w = result.witness["assign"]
    assert w["Grace"] in ("Math", "Physics")
    assert w["Hank"] != "Math"
    assert w["Iris"] in ("Physics", "Chemistry")


def test_problem_3_verify():
    frl = _problem_3()
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


# --- Problem 4: 4x4 UNSAT (pigeonhole) ---


def _problem_4():
    """Kim, Leo, Mia, Nate → Alpha, Beta, Gamma, Delta.
    All four restricted to {Alpha, Beta}. Pigeonhole: impossible."""
    return FRLInstance(
        nl_text=(
            "Four workers — Kim, Leo, Mia, and Nate — must each be assigned to one project: "
            "Alpha, Beta, Gamma, or Delta. Each project needs one worker. "
            "All four workers will only work on Alpha or Beta."
        ),
        entity_types=[
            EntityType("Person", ["Kim", "Leo", "Mia", "Nate"]),
            EntityType("Project", ["Alpha", "Beta", "Gamma", "Delta"]),
        ],
        functions=[FunctionVar("assign", "Person", "Project")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("each assigned to one project, each project needs one worker"),
            ),
            *[
                Constraint(
                    kind=ConstraintKind.EXCLUSION,
                    var="assign",
                    entity=person,
                    value=project,
                    provenance=Provenance(f"{person} will only work on Alpha or Beta"),
                )
                for person in ["Kim", "Leo", "Mia", "Nate"]
                for project in ["Gamma", "Delta"]
            ],
        ],
        query=Query(kind=QueryKind.IS_SATISFIABLE),
    )


def test_problem_4_unsat():
    frl = _problem_4()
    result = solve(frl)
    assert result.sat is False
    assert result.unsat_core is not None
    assert len(result.unsat_core) > 0


# --- Problem 5: 5x5 with all constraint types ---


def _problem_5():
    """Olivia, Pat, Quinn, Rosa, Sam → ER, ICU, Pediatrics, Oncology, Surgery.
    Olivia not ER or Surgery. Pat must be ER or ICU.
    If Quinn does Surgery, Rosa does Pediatrics. Sam not ICU or Oncology."""
    return FRLInstance(
        nl_text=(
            "Five nurses — Olivia, Pat, Quinn, Rosa, and Sam — are each assigned to one ward: "
            "ER, ICU, Pediatrics, Oncology, Surgery. Each ward has exactly one nurse. "
            "Olivia cannot work in ER or Surgery. Pat must be in ER or ICU. "
            "If Quinn is in Surgery, Rosa must be in Pediatrics. "
            "Sam cannot work in ICU or Oncology."
        ),
        entity_types=[
            EntityType("Person", ["Olivia", "Pat", "Quinn", "Rosa", "Sam"]),
            EntityType("Ward", ["ER", "ICU", "Pediatrics", "Oncology", "Surgery"]),
        ],
        functions=[FunctionVar("assign", "Person", "Ward")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("each assigned to one ward, each ward has one nurse"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Olivia",
                value="ER",
                provenance=Provenance("Olivia cannot work in ER"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Olivia",
                value="Surgery",
                provenance=Provenance("Olivia cannot work in Surgery"),
            ),
            # Pat must be ER or ICU = Pat not in Pediatrics, Oncology, Surgery
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Pat",
                value="Pediatrics",
                provenance=Provenance("Pat must be in ER or ICU", confidence=0),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Pat",
                value="Oncology",
                provenance=Provenance("Pat must be in ER or ICU", confidence=0),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Pat",
                value="Surgery",
                provenance=Provenance("Pat must be in ER or ICU", confidence=0),
            ),
            Constraint(
                kind=ConstraintKind.CONDITIONAL,
                condition_var="assign",
                condition_entity="Quinn",
                condition_value="Surgery",
                consequence_var="assign",
                consequence_entity="Rosa",
                consequence_value="Pediatrics",
                provenance=Provenance("If Quinn is in Surgery, Rosa must be in Pediatrics"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Sam",
                value="ICU",
                provenance=Provenance("Sam cannot work in ICU"),
            ),
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Sam",
                value="Oncology",
                provenance=Provenance("Sam cannot work in Oncology"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )


def test_problem_5_sat():
    frl = _problem_5()
    result = solve(frl)
    assert result.sat is True
    w = result.witness["assign"]
    assert w["Olivia"] not in ("ER", "Surgery")
    assert w["Pat"] in ("ER", "ICU")
    assert w["Sam"] not in ("ICU", "Oncology")
    if w["Quinn"] == "Surgery":
        assert w["Rosa"] == "Pediatrics"


def test_problem_5_verify():
    frl = _problem_5()
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


# --- ORDER test (Borel primitive: strict <) ---


def test_order_solve():
    """ORDER: Fred's parent is somewhere left of Eric."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Name", ["Alice", "Bob", "Eric"]),
        ],
        functions=[FunctionVar("name", "Name", "House")],
        constraints=[
            Constraint(kind=ConstraintKind.UNIQUENESS, var="name",
                       provenance=Provenance("each in different house")),
            Constraint(kind=ConstraintKind.ORDER,
                       var1="name", entity1="Alice",
                       var2="name", entity2="Eric",
                       provenance=Provenance("Alice is somewhere left of Eric")),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    w = result.witness["name"]
    houses = ["H1", "H2", "H3"]
    assert houses.index(w["Alice"]) < houses.index(w["Eric"])


def test_order_verify():
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Name", ["Alice", "Bob", "Eric"]),
        ],
        functions=[FunctionVar("name", "Name", "House")],
        constraints=[
            Constraint(kind=ConstraintKind.UNIQUENESS, var="name",
                       provenance=Provenance("each in different house")),
            Constraint(kind=ConstraintKind.ORDER,
                       var1="name", entity1="Alice",
                       var2="name", entity2="Eric",
                       provenance=Provenance("Alice is somewhere left of Eric")),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


# --- DISTANCE test (Borel primitive: |diff| == N or directed) ---


def test_distance_solve():
    """DISTANCE: Alice is exactly 2 houses from Bob."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3", "H4"]),
            EntityType("Name", ["Alice", "Bob", "Carol", "Dave"]),
        ],
        functions=[FunctionVar("name", "Name", "House")],
        constraints=[
            Constraint(kind=ConstraintKind.UNIQUENESS, var="name",
                       provenance=Provenance("each in different house")),
            Constraint(kind=ConstraintKind.DISTANCE,
                       var1="name", entity1="Alice",
                       var2="name", entity2="Bob",
                       distance_n=2,
                       provenance=Provenance("Alice is exactly 2 houses from Bob")),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    w = result.witness["name"]
    houses = ["H1", "H2", "H3", "H4"]
    assert abs(houses.index(w["Alice"]) - houses.index(w["Bob"])) == 2


def test_distance_directed_solve():
    """DISTANCE directed: Alice is exactly 2 positions RIGHT of Bob."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3", "H4"]),
            EntityType("Name", ["Alice", "Bob", "Carol", "Dave"]),
        ],
        functions=[FunctionVar("name", "Name", "House")],
        constraints=[
            Constraint(kind=ConstraintKind.UNIQUENESS, var="name",
                       provenance=Provenance("each in different house")),
            Constraint(kind=ConstraintKind.DISTANCE,
                       var1="name", entity1="Alice",
                       var2="name", entity2="Bob",
                       distance_n=2, directed=True,
                       provenance=Provenance("Alice is 2 positions right of Bob")),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    w = result.witness["name"]
    houses = ["H1", "H2", "H3", "H4"]
    assert houses.index(w["Alice"]) - houses.index(w["Bob"]) == 2


# --- BOUNDS test ---


def _problem_bounds():
    """Iris can only join Physics or Chemistry (BOUNDS replaces 2 EXCLUSIONs)."""
    return FRLInstance(
        nl_text="Iris must join either Physics or Chemistry.",
        entity_types=[
            EntityType("Person", ["Grace", "Hank", "Iris", "Jay"]),
            EntityType("Group", ["Math", "Physics", "Chemistry", "Biology"]),
        ],
        functions=[FunctionVar("assign", "Person", "Group")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("each person joins one group"),
            ),
            Constraint(
                kind=ConstraintKind.BOUNDS,
                var="assign",
                entity="Iris",
                allowed_values=["Physics", "Chemistry"],
                provenance=Provenance("Iris must join Physics or Chemistry"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )


def test_bounds_solve():
    frl = _problem_bounds()
    result = solve(frl)
    assert result.sat is True
    assert result.witness["assign"]["Iris"] in ("Physics", "Chemistry")


def test_bounds_verify():
    frl = _problem_bounds()
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


def test_bounds_negated_solve():
    """NOT IN: Grace cannot join Chemistry or Biology."""
    from src.frl.schema import NEGATED
    frl = FRLInstance(
        entity_types=[
            EntityType("Person", ["Grace", "Hank", "Iris", "Jay"]),
            EntityType("Group", ["Math", "Physics", "Chemistry", "Biology"]),
        ],
        functions=[FunctionVar("assign", "Person", "Group")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("each person joins one group"),
            ),
            Constraint(
                kind=ConstraintKind.BOUNDS,
                var="assign",
                entity="Grace",
                allowed_values=["Chemistry", "Biology"],
                polarity=NEGATED,
                provenance=Provenance("Grace will not join Chemistry or Biology"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    assert result.witness["assign"]["Grace"] in ("Math", "Physics")


# --- DISJUNCTION test (Σ₂ closure: UNION / OR) ---


def test_disjunction_solve():
    """OR: Alice is in house 1 or house 3."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Name", ["Alice", "Bob", "Carol"]),
        ],
        functions=[FunctionVar("name", "Name", "House")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS, var="name",
                provenance=Provenance("each in different house"),
            ),
            Constraint(
                kind=ConstraintKind.DISJUNCTION,
                disjuncts=[
                    Constraint(
                        kind=ConstraintKind.ASSIGNMENT,
                        var="name", entity="Alice", value="H1",
                        provenance=Provenance("Alice in house 1"),
                    ),
                    Constraint(
                        kind=ConstraintKind.ASSIGNMENT,
                        var="name", entity="Alice", value="H3",
                        provenance=Provenance("Alice in house 3"),
                    ),
                ],
                provenance=Provenance("Alice is in house 1 or house 3"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    assert result.witness["name"]["Alice"] in ("H1", "H3")


def test_disjunction_verify():
    """Verify disjunction independently."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Name", ["Alice", "Bob", "Carol"]),
        ],
        functions=[FunctionVar("name", "Name", "House")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS, var="name",
                provenance=Provenance("each in different house"),
            ),
            Constraint(
                kind=ConstraintKind.DISJUNCTION,
                disjuncts=[
                    Constraint(
                        kind=ConstraintKind.ASSIGNMENT,
                        var="name", entity="Alice", value="H1",
                        provenance=Provenance("Alice in house 1"),
                    ),
                    Constraint(
                        kind=ConstraintKind.ASSIGNMENT,
                        var="name", entity="Alice", value="H3",
                        provenance=Provenance("Alice in house 3"),
                    ),
                ],
                provenance=Provenance("Alice is in house 1 or house 3"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


def test_disjunction_complex():
    """OR with heterogeneous sub-constraints: assignment OR co_occurrence."""
    from src.frl.schema import NEGATED
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Name", ["Alice", "Bob", "Carol"]),
            EntityType("Color", ["Red", "Blue", "Green"]),
        ],
        functions=[
            FunctionVar("name", "Name", "House"),
            FunctionVar("color", "Color", "House"),
        ],
        constraints=[
            Constraint(kind=ConstraintKind.UNIQUENESS, var="name",
                       provenance=Provenance("unique names")),
            Constraint(kind=ConstraintKind.UNIQUENESS, var="color",
                       provenance=Provenance("unique colors")),
            # "Either Alice is in house 1, or Alice and Red are in the same house"
            Constraint(
                kind=ConstraintKind.DISJUNCTION,
                disjuncts=[
                    Constraint(
                        kind=ConstraintKind.ASSIGNMENT,
                        var="name", entity="Alice", value="H1",
                        provenance=Provenance("Alice in house 1"),
                    ),
                    Constraint(
                        kind=ConstraintKind.CO_OCCURRENCE,
                        var1="name", entity1="Alice",
                        var2="color", entity2="Red",
                        provenance=Provenance("Alice in red house"),
                    ),
                ],
                provenance=Provenance("Alice in H1 or Alice in red house"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    w = result.witness
    alice_house = w["name"]["Alice"]
    red_house = w["color"]["Red"]
    # At least one disjunct must hold
    assert alice_house == "H1" or alice_house == red_house


# --- FORALL / EXISTS tests (quantified constraints) ---


def test_forall_solve():
    """FORALL: every person must be in house 1 or house 2 (BOUNDS via quantifier)."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Person", ["Alice", "Bob", "Carol"]),
        ],
        functions=[FunctionVar("assign", "Person", "House")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS, var="assign",
                provenance=Provenance("all different"),
            ),
            # FORALL p ∈ Person: assign(p) ∈ {H1, H2}
            # This should be UNSAT — 3 people, only 2 allowed houses, uniqueness
            Constraint(
                kind=ConstraintKind.FORALL,
                bind_var="p",
                bind_domain="Person",
                body=Constraint(
                    kind=ConstraintKind.BOUNDS,
                    var="assign",
                    entity="p",  # will be substituted with each person
                    allowed_values=["H1", "H2"],
                    provenance=Provenance("must be in H1 or H2"),
                ),
                provenance=Provenance("every person in H1 or H2"),
            ),
        ],
        query=Query(kind=QueryKind.IS_SATISFIABLE),
    )
    result = solve(frl)
    assert result.sat is False  # pigeonhole: 3 people, 2 houses, uniqueness


def test_forall_sat():
    """FORALL: every person is NOT in house 3 (2 people, 3 houses → SAT)."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Person", ["Alice", "Bob"]),
        ],
        functions=[FunctionVar("assign", "Person", "House")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS, var="assign",
                provenance=Provenance("all different"),
            ),
            Constraint(
                kind=ConstraintKind.FORALL,
                bind_var="p",
                bind_domain="Person",
                body=Constraint(
                    kind=ConstraintKind.EXCLUSION,
                    var="assign",
                    entity="p",
                    value="H3",
                    provenance=Provenance("not in H3"),
                ),
                provenance=Provenance("nobody in H3"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    assert result.witness["assign"]["Alice"] != "H3"
    assert result.witness["assign"]["Bob"] != "H3"


def test_forall_verify():
    """Verify FORALL constraint independently."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Person", ["Alice", "Bob"]),
        ],
        functions=[FunctionVar("assign", "Person", "House")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS, var="assign",
                provenance=Provenance("all different"),
            ),
            Constraint(
                kind=ConstraintKind.FORALL,
                bind_var="p",
                bind_domain="Person",
                body=Constraint(
                    kind=ConstraintKind.EXCLUSION,
                    var="assign",
                    entity="p",
                    value="H3",
                    provenance=Provenance("not in H3"),
                ),
                provenance=Provenance("nobody in H3"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    vr = verify_witness(frl, result.witness)
    assert vr.valid is True, vr.violations


def test_exists_solve():
    """EXISTS: at least one person is in house 1."""
    frl = FRLInstance(
        entity_types=[
            EntityType("House", ["H1", "H2", "H3"]),
            EntityType("Person", ["Alice", "Bob", "Carol"]),
        ],
        functions=[FunctionVar("assign", "Person", "House")],
        constraints=[
            Constraint(
                kind=ConstraintKind.UNIQUENESS, var="assign",
                provenance=Provenance("all different"),
            ),
            Constraint(
                kind=ConstraintKind.EXISTS,
                bind_var="p",
                bind_domain="Person",
                body=Constraint(
                    kind=ConstraintKind.ASSIGNMENT,
                    var="assign",
                    entity="p",
                    value="H1",
                    provenance=Provenance("in H1"),
                ),
                provenance=Provenance("someone is in H1"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    result = solve(frl)
    assert result.sat is True
    # At least one person in H1
    assert "H1" in result.witness["assign"].values()


# --- Verifier negative test ---


def test_verify_catches_violation():
    """Verifier should catch a bad witness."""
    frl = _problem_1()
    bad_witness = {"assign": {"Alice": "Cleanup", "Bob": "Setup", "Carol": "Cooking"}}
    vr = verify_witness(frl, bad_witness)
    assert vr.valid is False
    assert len(vr.violations) > 0
    assert any("Cleanup" in v for v in vr.violations)
