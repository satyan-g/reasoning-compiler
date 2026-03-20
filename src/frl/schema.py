"""FRL v0 schema for assignment/scheduling domain.

Minimal dataclasses + JSON serialization. One domain only.

Ternary values:
  polarity:   +1 (asserted), 0 (ambiguous), -1 (negated)
  confidence: +1 (explicit in NL), 0 (inferred/implicit), -1 (contradicted)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional


# --- Ternary values ---

ASSERTED = 1
AMBIGUOUS = 0
NEGATED = -1

EXPLICIT = 1
INFERRED = 0
CONTRADICTED = -1


# --- Provenance ---


@dataclass
class Provenance:
    """Links a constraint back to the NL text that produced it."""

    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    confidence: int = EXPLICIT  # +1 explicit, 0 inferred, -1 contradicted


# --- Entity types (Enum sorts) ---


@dataclass
class EntityType:
    """A named set of entities (maps to Z3 EnumSort).

    Example: EntityType(name="Person", values=["Alice", "Bob", "Cara"])
    """

    name: str
    values: list[str]


# --- Function variables ---


@dataclass
class FunctionVar:
    """A function variable mapping one entity type to another.

    Example: FunctionVar(name="assign", domain="Person", codomain="Task")
    means assign: Person -> Task

    For arithmetic domain, use NumericVar instead.
    """

    name: str
    domain: str
    codomain: str


@dataclass
class NumericVar:
    """A numeric variable with optional bounds.

    Used in arithmetic domain. Bounded variables are decidable and fast;
    unbounded variables may cause solver timeouts.

    Examples:
        NumericVar("price", "int", lower=0, upper=1000)  # bounded
        NumericVar("count", "int", lower=0)               # lower-bounded only
        NumericVar("ratio", "real")                        # unbounded
    """

    name: str
    type: str = "int"  # "int" or "real"
    lower: Optional[int | float] = None
    upper: Optional[int | float] = None
    description: str = ""

    @property
    def is_bounded(self) -> bool:
        return self.lower is not None and self.upper is not None

    @property
    def is_lower_bounded(self) -> bool:
        return self.lower is not None

    @property
    def is_upper_bounded(self) -> bool:
        return self.upper is not None


# --- Constraint types ---


class ConstraintKind(Enum):
    EXCLUSION = "exclusion"
    ASSIGNMENT = "assignment"
    UNIQUENESS = "uniqueness"
    CONDITIONAL = "conditional"
    CARDINALITY = "cardinality"
    CO_OCCURRENCE = "co_occurrence"
    ADJACENT = "adjacent"
    RIGHT_OF = "right_of"
    BOUNDS = "bounds"


class CompareOp(Enum):
    EQ = "=="
    NEQ = "!="


class CardinalityOp(Enum):
    AT_LEAST = ">="
    AT_MOST = "<="
    EXACTLY = "=="


@dataclass
class Constraint:
    """A single constraint in the FRL.

    The `kind` field determines which other fields are relevant:

    EXCLUSION:   var(entity) != value
    ASSIGNMENT:  var(entity) == value
    UNIQUENESS:  AllDifferent(var(e) for e in entities)
    CONDITIONAL: if condition_var(condition_entity) condition_op condition_value
                 then consequence_var(consequence_entity) consequence_op consequence_value
    CARDINALITY: |{e : var(e) == value}| card_op card_value
    CO_OCCURRENCE: var1(entity1) == var2(entity2) (same codomain value)
    ADJACENT: |index(var1(entity1)) - index(var2(entity2))| == 1
    RIGHT_OF: index(var1(entity1)) == index(var2(entity2)) + 1
    BOUNDS: var(entity) in allowed_values (value bounds)
            With polarity=-1: var(entity) NOT in allowed_values (exclusion set)
    """

    kind: ConstraintKind
    provenance: Provenance
    polarity: int = ASSERTED  # +1 asserted, 0 ambiguous, -1 negated

    # EXCLUSION, ASSIGNMENT, UNIQUENESS, CARDINALITY
    var: Optional[str] = None
    entity: Optional[str] = None
    value: Optional[str] = None

    # UNIQUENESS — None means all entities in domain
    entities: Optional[list[str]] = None

    # CONDITIONAL
    condition_var: Optional[str] = None
    condition_entity: Optional[str] = None
    condition_value: Optional[str] = None
    condition_op: CompareOp = CompareOp.EQ
    consequence_var: Optional[str] = None
    consequence_entity: Optional[str] = None
    consequence_value: Optional[str] = None
    consequence_op: CompareOp = CompareOp.EQ

    # CARDINALITY
    card_op: Optional[CardinalityOp] = None
    card_value: Optional[int] = None

    # CO_OCCURRENCE, ADJACENT, RIGHT_OF
    var1: Optional[str] = None
    entity1: Optional[str] = None
    var2: Optional[str] = None
    entity2: Optional[str] = None

    # BOUNDS — allowed values (polarity=-1 flips to excluded values)
    allowed_values: Optional[list[str]] = None


# --- Query ---


class QueryKind(Enum):
    FIND_ASSIGNMENT = "find_assignment"
    ALL_ASSIGNMENTS = "all_assignments"
    IS_SATISFIABLE = "is_satisfiable"


@dataclass
class Query:
    """What we're being asked to find."""

    kind: QueryKind
    description: str = ""


# --- Top-level FRL instance ---


@dataclass
class FRLInstance:
    """A complete FRL problem specification."""

    entity_types: list[EntityType]
    functions: list[FunctionVar]
    constraints: list[Constraint]
    query: Query
    numeric_vars: list[NumericVar] = field(default_factory=list)
    nl_text: str = ""
    metadata: dict = field(default_factory=dict)

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, default=_enum_serializer, indent=2)

    @classmethod
    def from_json(cls, s: str) -> FRLInstance:
        d = json.loads(s)
        return _dict_to_frl(d)


# --- Validation ---


def validate(frl: FRLInstance) -> list[str]:
    """Check that all references in constraints are valid. Returns list of errors."""
    errors = []
    type_names = {et.name for et in frl.entity_types}
    type_values = {et.name: set(et.values) for et in frl.entity_types}
    func_map = {f.name: f for f in frl.functions}

    def _check_var_entity_value(var: str | None, entity: str | None, value: str | None, label: str):
        if var is not None and var not in func_map:
            errors.append(f"{label}: unknown function '{var}'")
        if var is not None and var in func_map:
            fv = func_map[var]
            if fv.domain not in type_names:
                errors.append(f"{label}: function '{var}' has unknown domain '{fv.domain}'")
            elif entity is not None and entity not in type_values.get(fv.domain, set()):
                errors.append(f"{label}: entity '{entity}' not in {fv.domain}")
            if fv.codomain not in type_names:
                errors.append(f"{label}: function '{var}' has unknown codomain '{fv.codomain}'")
            elif value is not None and value not in type_values.get(fv.codomain, set()):
                errors.append(f"{label}: value '{value}' not in {fv.codomain}")

    for i, c in enumerate(frl.constraints):
        label = f"constraint[{i}] ({c.kind.value})"

        if c.kind in (ConstraintKind.EXCLUSION, ConstraintKind.ASSIGNMENT):
            _check_var_entity_value(c.var, c.entity, c.value, label)

        elif c.kind == ConstraintKind.UNIQUENESS:
            if c.var is not None and c.var in func_map:
                fv = func_map[c.var]
                if c.entities is not None:
                    domain_vals = type_values.get(fv.domain, set())
                    for e in c.entities:
                        if e not in domain_vals:
                            errors.append(f"{label}: entity '{e}' not in {fv.domain}")

        elif c.kind == ConstraintKind.CONDITIONAL:
            _check_var_entity_value(c.condition_var, c.condition_entity, c.condition_value, f"{label} condition")
            _check_var_entity_value(c.consequence_var, c.consequence_entity, c.consequence_value, f"{label} consequence")

        elif c.kind == ConstraintKind.CARDINALITY:
            _check_var_entity_value(c.var, None, c.value, label)
            if c.card_op is None:
                errors.append(f"{label}: missing card_op")
            if c.card_value is None:
                errors.append(f"{label}: missing card_value")

        elif c.kind in (ConstraintKind.CO_OCCURRENCE, ConstraintKind.ADJACENT, ConstraintKind.RIGHT_OF):
            # var1(entity1) and var2(entity2) — entity is in domain, no value to check
            _check_var_entity_value(c.var1, c.entity1, None, f"{label} var1")
            _check_var_entity_value(c.var2, c.entity2, None, f"{label} var2")
            # Both functions must share the same codomain
            if c.var1 in func_map and c.var2 in func_map:
                if func_map[c.var1].codomain != func_map[c.var2].codomain:
                    errors.append(
                        f"{label}: var1 codomain '{func_map[c.var1].codomain}' "
                        f"!= var2 codomain '{func_map[c.var2].codomain}'"
                    )

        elif c.kind == ConstraintKind.BOUNDS:
            _check_var_entity_value(c.var, c.entity, None, label)
            if not c.allowed_values:
                errors.append(f"{label}: missing allowed_values")
            elif c.var in func_map:
                codomain_vals = type_values.get(func_map[c.var].codomain, set())
                for v in c.allowed_values:
                    if v not in codomain_vals:
                        errors.append(f"{label}: allowed value '{v}' not in codomain")

    return errors


# --- Serialization helpers ---


def _enum_serializer(obj):
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _dict_to_frl(d: dict) -> FRLInstance:
    entity_types = [EntityType(**et) for et in d["entity_types"]]
    functions = [FunctionVar(**fv) for fv in d["functions"]]
    constraints = []
    for c in d["constraints"]:
        c["kind"] = ConstraintKind(c["kind"])
        # Backward compat: convert implicit → confidence
        prov = c["provenance"]
        if "implicit" in prov:
            implicit = prov.pop("implicit")
            if "confidence" not in prov:
                prov["confidence"] = INFERRED if implicit else EXPLICIT
        c["provenance"] = Provenance(**prov)
        if c.get("condition_op") is not None:
            c["condition_op"] = CompareOp(c["condition_op"])
        if c.get("consequence_op") is not None:
            c["consequence_op"] = CompareOp(c["consequence_op"])
        if c.get("card_op") is not None:
            c["card_op"] = CardinalityOp(c["card_op"])
        constraints.append(Constraint(**c))
    query = Query(
        kind=QueryKind(d["query"]["kind"]),
        description=d["query"].get("description", ""),
    )
    numeric_vars = [NumericVar(**nv) for nv in d.get("numeric_vars", [])]
    return FRLInstance(
        entity_types=entity_types,
        functions=functions,
        constraints=constraints,
        query=query,
        numeric_vars=numeric_vars,
        nl_text=d.get("nl_text", ""),
        metadata=d.get("metadata", {}),
    )
