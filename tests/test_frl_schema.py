"""Tests for FRL v0 schema: construction, serialization, validation."""

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
    validate,
)


def _make_3x3():
    """Build the standard 3-person/3-task example."""
    return FRLInstance(
        nl_text=(
            "Alice, Bob, and Cara must each be assigned to one of three tasks: "
            "painting, packing, or welding. Alice cannot weld. "
            "If Bob welds, then Cara paints. Everyone has a different task."
        ),
        entity_types=[
            EntityType("Person", ["Alice", "Bob", "Cara"]),
            EntityType("Task", ["Paint", "Pack", "Weld"]),
        ],
        functions=[FunctionVar("assign", "Person", "Task")],
        constraints=[
            Constraint(
                kind=ConstraintKind.EXCLUSION,
                var="assign",
                entity="Alice",
                value="Weld",
                provenance=Provenance("Alice cannot weld"),
            ),
            Constraint(
                kind=ConstraintKind.CONDITIONAL,
                condition_var="assign",
                condition_entity="Bob",
                condition_value="Weld",
                consequence_var="assign",
                consequence_entity="Cara",
                consequence_value="Paint",
                provenance=Provenance("If Bob welds, then Cara paints"),
            ),
            Constraint(
                kind=ConstraintKind.UNIQUENESS,
                var="assign",
                provenance=Provenance("Everyone has a different task"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )


def test_construction():
    frl = _make_3x3()
    assert len(frl.entity_types) == 2
    assert len(frl.functions) == 1
    assert len(frl.constraints) == 3
    assert frl.constraints[0].kind == ConstraintKind.EXCLUSION
    assert frl.constraints[1].kind == ConstraintKind.CONDITIONAL
    assert frl.constraints[2].kind == ConstraintKind.UNIQUENESS


def test_json_roundtrip():
    frl = _make_3x3()
    json_str = frl.to_json()
    restored = FRLInstance.from_json(json_str)
    assert restored.nl_text == frl.nl_text
    assert len(restored.constraints) == len(frl.constraints)
    for orig, rest in zip(frl.constraints, restored.constraints):
        assert orig.kind == rest.kind
        assert orig.provenance.text == rest.provenance.text


def test_validate_valid():
    frl = _make_3x3()
    errors = validate(frl)
    assert errors == []


def test_validate_bad_function_ref():
    frl = _make_3x3()
    frl.constraints[0].var = "nonexistent"
    errors = validate(frl)
    assert any("nonexistent" in e for e in errors)


def test_validate_bad_entity_ref():
    frl = _make_3x3()
    frl.constraints[0].entity = "Dave"
    errors = validate(frl)
    assert any("Dave" in e for e in errors)


def test_validate_bad_value_ref():
    frl = _make_3x3()
    frl.constraints[0].value = "Swim"
    errors = validate(frl)
    assert any("Swim" in e for e in errors)


def test_provenance_implicit():
    p = Provenance("implied uniqueness", implicit=True)
    assert p.implicit is True
    assert p.text == "implied uniqueness"


def test_cardinality_constraint():
    frl = FRLInstance(
        entity_types=[
            EntityType("Person", ["Alice", "Bob", "Cara", "Dave"]),
            EntityType("Task", ["Paint", "Pack"]),
        ],
        functions=[FunctionVar("assign", "Person", "Task")],
        constraints=[
            Constraint(
                kind=ConstraintKind.CARDINALITY,
                var="assign",
                value="Paint",
                card_op=CardinalityOp.AT_MOST,
                card_value=2,
                provenance=Provenance("At most 2 people paint"),
            ),
        ],
        query=Query(kind=QueryKind.FIND_ASSIGNMENT),
    )
    errors = validate(frl)
    assert errors == []


def test_negated_conditional():
    """Conditional with NEQ consequence: if Bob welds, Cara does NOT pack."""
    c = Constraint(
        kind=ConstraintKind.CONDITIONAL,
        condition_var="assign",
        condition_entity="Bob",
        condition_value="Weld",
        consequence_var="assign",
        consequence_entity="Cara",
        consequence_value="Pack",
        consequence_op=CompareOp.NEQ,
        provenance=Provenance("If Bob welds, Cara does not pack"),
    )
    assert c.consequence_op == CompareOp.NEQ
