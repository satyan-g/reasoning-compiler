"""Compile FRL instances to Z3 constraints and solve."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import z3

from src.frl.schema import (
    CardinalityOp,
    CompareOp,
    Constraint,
    ConstraintKind,
    FRLInstance,
)


@dataclass
class Z3Context:
    """Holds Z3 objects created during compilation."""

    sorts: dict[str, z3.DatatypeSortRef] = field(default_factory=dict)
    sort_constructors: dict[str, dict[str, z3.FuncDeclRef]] = field(default_factory=dict)
    functions: dict[str, z3.FuncDeclRef] = field(default_factory=dict)
    solver: z3.Solver = field(default_factory=z3.Solver)
    constraint_labels: dict[str, int] = field(default_factory=dict)


@dataclass
class SolveResult:
    """Result of solving an FRL instance."""

    sat: bool
    witness: Optional[dict[str, dict[str, str]]] = None  # {func_name: {entity: value}}
    unsat_core: Optional[list[int]] = None  # constraint indices


def compile_to_z3(frl: FRLInstance) -> Z3Context:
    """Compile an FRL instance to Z3 constraints. Returns context for solving."""
    ctx = Z3Context()

    # Create enum sorts
    for et in frl.entity_types:
        dt = z3.Datatype(et.name)
        for v in et.values:
            dt.declare(v)
        sort = dt.create()
        ctx.sorts[et.name] = sort
        ctx.sort_constructors[et.name] = {}
        for v in et.values:
            ctx.sort_constructors[et.name][v] = getattr(sort, v)

    # Create function variables
    for fv in frl.functions:
        domain_sort = ctx.sorts[fv.domain]
        codomain_sort = ctx.sorts[fv.codomain]
        ctx.functions[fv.name] = z3.Function(fv.name, domain_sort, codomain_sort)

    # Compile constraints
    for i, c in enumerate(frl.constraints):
        label = f"c{i}"
        z3_expr = _compile_constraint(c, ctx)
        ctx.solver.assert_and_track(z3_expr, label)
        ctx.constraint_labels[label] = i

    return ctx


def solve(frl: FRLInstance, ctx: Optional[Z3Context] = None) -> SolveResult:
    """Compile and solve an FRL instance."""
    if ctx is None:
        ctx = compile_to_z3(frl)

    result = ctx.solver.check()

    if result == z3.sat:
        model = ctx.solver.model()
        witness = _extract_witness(frl, ctx, model)
        return SolveResult(sat=True, witness=witness)

    elif result == z3.unsat:
        core = ctx.solver.unsat_core()
        indices = [ctx.constraint_labels[str(label)] for label in core]
        return SolveResult(sat=False, unsat_core=sorted(indices))

    else:
        raise RuntimeError(f"Z3 returned unexpected result: {result}")


def _compile_constraint(c: Constraint, ctx: Z3Context) -> z3.BoolRef:
    """Compile a single FRL constraint to a Z3 expression."""

    if c.kind == ConstraintKind.EXCLUSION:
        func = ctx.functions[c.var]
        entity = ctx.sort_constructors[_domain_of(c.var, ctx)][c.entity]
        value = ctx.sort_constructors[_codomain_of(c.var, ctx)][c.value]
        return func(entity) != value

    elif c.kind == ConstraintKind.ASSIGNMENT:
        func = ctx.functions[c.var]
        entity = ctx.sort_constructors[_domain_of(c.var, ctx)][c.entity]
        value = ctx.sort_constructors[_codomain_of(c.var, ctx)][c.value]
        return func(entity) == value

    elif c.kind == ConstraintKind.UNIQUENESS:
        func = ctx.functions[c.var]
        domain_name = _domain_of(c.var, ctx)
        if c.entities is not None:
            entities = [ctx.sort_constructors[domain_name][e] for e in c.entities]
        else:
            # All entities in the domain
            entities = list(ctx.sort_constructors[domain_name].values())
        apps = [func(e) for e in entities]
        return z3.Distinct(*apps)

    elif c.kind == ConstraintKind.CONDITIONAL:
        # Build condition
        cond_func = ctx.functions[c.condition_var]
        cond_entity = ctx.sort_constructors[_domain_of(c.condition_var, ctx)][c.condition_entity]
        cond_value = ctx.sort_constructors[_codomain_of(c.condition_var, ctx)][c.condition_value]
        if c.condition_op == CompareOp.EQ:
            condition = cond_func(cond_entity) == cond_value
        else:
            condition = cond_func(cond_entity) != cond_value

        # Build consequence
        cons_func = ctx.functions[c.consequence_var]
        cons_entity = ctx.sort_constructors[_domain_of(c.consequence_var, ctx)][c.consequence_entity]
        cons_value = ctx.sort_constructors[_codomain_of(c.consequence_var, ctx)][c.consequence_value]
        if c.consequence_op == CompareOp.EQ:
            consequence = cons_func(cons_entity) == cons_value
        else:
            consequence = cons_func(cons_entity) != cons_value

        return z3.Implies(condition, consequence)

    elif c.kind == ConstraintKind.CARDINALITY:
        func = ctx.functions[c.var]
        domain_name = _domain_of(c.var, ctx)
        codomain_name = _codomain_of(c.var, ctx)
        value = ctx.sort_constructors[codomain_name][c.value]
        entities = list(ctx.sort_constructors[domain_name].values())

        # Count: sum of (1 if func(e) == value else 0)
        counts = [z3.If(func(e) == value, 1, 0) for e in entities]
        total = z3.Sum(counts)

        if c.card_op == CardinalityOp.AT_LEAST:
            return total >= c.card_value
        elif c.card_op == CardinalityOp.AT_MOST:
            return total <= c.card_value
        elif c.card_op == CardinalityOp.EXACTLY:
            return total == c.card_value
        else:
            raise ValueError(f"Unknown cardinality op: {c.card_op}")

    else:
        raise ValueError(f"Unknown constraint kind: {c.kind}")


def _extract_witness(frl: FRLInstance, ctx: Z3Context, model: z3.ModelRef) -> dict[str, dict[str, str]]:
    """Extract a witness from a Z3 model as {func_name: {entity: value}}."""
    witness = {}
    for fv in frl.functions:
        func = ctx.functions[fv.name]
        domain_constructors = ctx.sort_constructors[fv.domain]
        witness[fv.name] = {}
        for entity_name, entity_ref in domain_constructors.items():
            result = model.eval(func(entity_ref), model_completion=True)
            witness[fv.name][entity_name] = str(result)
    return witness


def _domain_of(var_name: str, ctx: Z3Context) -> str:
    """Get the domain sort name for a function variable."""
    func = ctx.functions[var_name]
    return func.domain(0).name()


def _codomain_of(var_name: str, ctx: Z3Context) -> str:
    """Get the codomain sort name for a function variable."""
    func = ctx.functions[var_name]
    return func.range().name()
