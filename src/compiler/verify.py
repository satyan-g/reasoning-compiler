"""Independent verifier — check a witness against FRL constraints without Z3."""

from __future__ import annotations

from dataclasses import dataclass

from src.frl.schema import (
    CardinalityOp,
    CompareOp,
    Constraint,
    ConstraintKind,
    FRLInstance,
)


@dataclass
class VerifyResult:
    """Result of verifying a witness against FRL constraints."""

    valid: bool
    violations: list[str]  # human-readable descriptions of violated constraints


def verify_witness(frl: FRLInstance, witness: dict[str, dict[str, str]]) -> VerifyResult:
    """Check a witness against all FRL constraints. No Z3 dependency.

    Args:
        frl: The FRL problem instance.
        witness: {func_name: {entity: value}} mapping, e.g.
                 {"assign": {"Alice": "Paint", "Bob": "Weld", "Cara": "Wire"}}

    Returns:
        VerifyResult with valid=True if all constraints are satisfied.
    """
    violations = []

    for i, c in enumerate(frl.constraints):
        label = f"constraint[{i}] ({c.kind.value})"
        result = _check_constraint(c, witness, label)
        if result is not None:
            violations.append(result)

    return VerifyResult(valid=len(violations) == 0, violations=violations)


def _check_constraint(c: Constraint, witness: dict[str, dict[str, str]], label: str) -> str | None:
    """Check one constraint. Returns error string or None if satisfied."""

    if c.kind == ConstraintKind.EXCLUSION:
        actual = witness[c.var][c.entity]
        if actual == c.value:
            return f"{label}: {c.var}({c.entity}) == {c.value}, expected != {c.value}"
        return None

    elif c.kind == ConstraintKind.ASSIGNMENT:
        actual = witness[c.var][c.entity]
        if actual != c.value:
            return f"{label}: {c.var}({c.entity}) == {actual}, expected {c.value}"
        return None

    elif c.kind == ConstraintKind.UNIQUENESS:
        func_witness = witness[c.var]
        if c.entities is not None:
            values = [func_witness[e] for e in c.entities]
        else:
            values = list(func_witness.values())
        if len(values) != len(set(values)):
            dupes = [v for v in set(values) if values.count(v) > 1]
            return f"{label}: duplicate values {dupes} in {c.var}"
        return None

    elif c.kind == ConstraintKind.CONDITIONAL:
        cond_actual = witness[c.condition_var][c.condition_entity]
        if c.condition_op == CompareOp.EQ:
            condition_met = cond_actual == c.condition_value
        else:
            condition_met = cond_actual != c.condition_value

        if not condition_met:
            return None  # condition not triggered, constraint satisfied vacuously

        cons_actual = witness[c.consequence_var][c.consequence_entity]
        if c.consequence_op == CompareOp.EQ:
            consequence_met = cons_actual == c.consequence_value
        else:
            consequence_met = cons_actual != c.consequence_value

        if not consequence_met:
            return (
                f"{label}: condition {c.condition_var}({c.condition_entity}) "
                f"{c.condition_op.value} {c.condition_value} is true, "
                f"but {c.consequence_var}({c.consequence_entity}) == {cons_actual}, "
                f"expected {c.consequence_op.value} {c.consequence_value}"
            )
        return None

    elif c.kind == ConstraintKind.CARDINALITY:
        func_witness = witness[c.var]
        count = sum(1 for v in func_witness.values() if v == c.value)

        if c.card_op == CardinalityOp.AT_LEAST and count < c.card_value:
            return f"{label}: {count} entities assigned to {c.value}, expected >= {c.card_value}"
        elif c.card_op == CardinalityOp.AT_MOST and count > c.card_value:
            return f"{label}: {count} entities assigned to {c.value}, expected <= {c.card_value}"
        elif c.card_op == CardinalityOp.EXACTLY and count != c.card_value:
            return f"{label}: {count} entities assigned to {c.value}, expected == {c.card_value}"
        return None

    else:
        return f"{label}: unknown constraint kind {c.kind}"
