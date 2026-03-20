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


# --- Verifier negative test ---


def test_verify_catches_violation():
    """Verifier should catch a bad witness."""
    frl = _problem_1()
    bad_witness = {"assign": {"Alice": "Cleanup", "Bob": "Setup", "Carol": "Cooking"}}
    vr = verify_witness(frl, bad_witness)
    assert vr.valid is False
    assert len(vr.violations) > 0
    assert any("Cleanup" in v for v in vr.violations)
