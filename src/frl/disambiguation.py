"""FRL disambiguation rules and aliases.

This module serves three purposes:
1. Documentation for LLM prompts (tells the LLM how to handle edge cases)
2. Machine-readable rules for validation and testing
3. Alias table mapping NL phrasings to canonical FRL constraint types

Each disambiguation rule has:
  - nl_patterns: NL phrases that trigger this ambiguity
  - candidates: possible FRL constraint types it could map to
  - resolution: how to decide
  - default: what to pick when genuinely ambiguous
  - flag: how to mark uncertainty in provenance

Each alias maps a set of NL phrases to a single canonical FRL form,
optionally with parameter transforms (e.g., swapping entity order).
"""

from dataclasses import dataclass, field


@dataclass
class Alias:
    """Maps NL phrases to a canonical FRL constraint type."""
    nl_phrases: list[str]
    canonical: str  # canonical ConstraintKind value
    swap_entities: bool = False  # if True, swap entity1/entity2 (e.g., "left of" → RIGHT_OF reversed)
    negate: bool = False  # if True, set negated=True on the constraint
    notes: str = ""


@dataclass
class DisambiguationRule:
    id: str
    nl_patterns: list[str]
    candidates: list[str]
    resolution: str
    default: str
    flag: str


RULES: list[DisambiguationRule] = [
    DisambiguationRule(
        id="left_of",
        nl_patterns=["left of", "to the left of"],
        candidates=["RIGHT_OF (directly left, no gap)", "BEFORE (somewhere left, gap allowed)"],
        resolution=(
            "Check if the NL implies adjacency. "
            "'Directly to the left' → RIGHT_OF. "
            "'Somewhere to the left' → BEFORE. "
            "If just 'left of' with no qualifier, check surrounding clues for context."
        ),
        default="BEFORE (weaker claim — allows gap)",
        flag="implicit=True, text='assumed somewhere left, not directly left'",
    ),
    DisambiguationRule(
        id="right_of",
        nl_patterns=["right of", "to the right of"],
        candidates=["RIGHT_OF (directly right, no gap)", "AFTER (somewhere right, gap allowed)"],
        resolution=(
            "Same logic as left_of but mirrored. "
            "'Directly to the right' → use RIGHT_OF from the left entity's perspective. "
            "'Somewhere to the right' → AFTER."
        ),
        default="AFTER (weaker claim)",
        flag="implicit=True, text='assumed somewhere right, not directly right'",
    ),
    DisambiguationRule(
        id="next_to",
        nl_patterns=["next to", "beside", "neighbor", "adjacent"],
        candidates=["ADJACENT (position differs by exactly 1)"],
        resolution="These all mean ADJACENT. No ambiguity in logic grid context.",
        default="ADJACENT",
        flag="",
    ),
    DisambiguationRule(
        id="or_constraint",
        nl_patterns=["or", "either ... or"],
        candidates=["inclusive OR (at least one)", "exclusive OR (exactly one)"],
        resolution=(
            "'Either A or B' in logic puzzles is usually inclusive OR. "
            "'Either A or B but not both' is exclusive OR. "
            "If 'but not both' is absent, default to inclusive OR."
        ),
        default="inclusive OR",
        flag="implicit=True, text='assumed inclusive OR'",
    ),
    DisambiguationRule(
        id="not_same",
        nl_patterns=["different from", "not the same as", "is not"],
        candidates=["EXCLUSION (specific value excluded)", "NOT CO_OCCURRENCE (different house)"],
        resolution=(
            "If comparing entity to a specific value: EXCLUSION. "
            "'Alice is not a painter' → EXCLUSION(assign, Alice, Paint). "
            "If comparing two entities: negated CO_OCCURRENCE. "
            "'Alice and Bob are not in the same house' → CO_OCCURRENCE(negated=True)."
        ),
        default="EXCLUSION if value is named, negated CO_OCCURRENCE if comparing entities",
        flag="",
    ),
    DisambiguationRule(
        id="between",
        nl_patterns=["between", "in between"],
        candidates=["BETWEEN (strict: a < b < c)"],
        resolution=(
            "'B is between A and C' means index(A) < index(B) < index(C) "
            "OR index(C) < index(B) < index(A). The NL doesn't specify which "
            "end is left. Model as: BETWEEN(b, a, c) meaning b is strictly "
            "between a and c in either direction."
        ),
        default="BETWEEN (bidirectional)",
        flag="",
    ),
    DisambiguationRule(
        id="each_exactly_one",
        nl_patterns=["each ... exactly one", "every ... one and only one", "assigned to exactly one"],
        candidates=["UNIQUENESS (AllDifferent)", "ASSIGNMENT (specific mapping)"],
        resolution=(
            "This is almost always UNIQUENESS (AllDifferent). "
            "It means the function is a bijection — no two entities share a value. "
            "Mark as implicit=True since it's often stated once and applies globally."
        ),
        default="UNIQUENESS",
        flag="implicit=True",
    ),
    DisambiguationRule(
        id="half_of",
        nl_patterns=["half of", "half as many", "twice as many", "double"],
        candidates=["RELATION (arithmetic)", "Not applicable for logic grids"],
        resolution=(
            "In arithmetic domain: model as a relation (x = y / 2 or x = 2 * y). "
            "In logic grid domain: this pattern shouldn't appear — flag as unusual."
        ),
        default="RELATION in arithmetic domain",
        flag="",
    ),
]


# --- Alias table ---
# Maps NL phrasings to canonical FRL constraint types.
# When multiple NL phrases mean the same thing, they all map here.
# The LLM should produce the canonical form; the alias table
# documents what that canonical form is.

ALIASES: list[Alias] = [
    # --- Positional: BEFORE (index <) ---
    Alias(
        nl_phrases=["left of", "to the left of", "before", "somewhere to the left",
                     "in a lower position than"],
        canonical="BEFORE",
        notes="Weaker than RIGHT_OF — allows any gap between positions",
    ),
    Alias(
        nl_phrases=["not right of", "not to the right of", "not after"],
        canonical="BEFORE",
        negate=False,  # "not right of" ≡ BEFORE (or equal), but BEFORE is strict <
        notes="'Not right of' ≈ BEFORE. Strictly: idx(a) <= idx(b), but BEFORE is idx(a) < idx(b). "
              "If equality is possible, use negated AFTER instead.",
    ),

    # --- Positional: AFTER (index >) ---
    Alias(
        nl_phrases=["right of", "to the right of", "after", "somewhere to the right",
                     "in a higher position than"],
        canonical="AFTER",
        notes="Mirror of BEFORE",
    ),
    Alias(
        nl_phrases=["not left of", "not to the left of", "not before"],
        canonical="AFTER",
        negate=False,
        notes="Same caveat as 'not right of' above",
    ),

    # --- Positional: RIGHT_OF (index == other + 1, directly right) ---
    Alias(
        nl_phrases=["directly to the right of", "immediately right of",
                     "in the next position after"],
        canonical="RIGHT_OF",
    ),
    Alias(
        nl_phrases=["directly to the left of", "immediately left of",
                     "in the position just before"],
        canonical="RIGHT_OF",
        swap_entities=True,
        notes="'A directly left of B' → RIGHT_OF(B, A) — swap entity order",
    ),

    # --- Positional: ADJACENT (|index diff| == 1) ---
    Alias(
        nl_phrases=["next to", "beside", "neighbor of", "adjacent to",
                     "right next to", "side by side with"],
        canonical="ADJACENT",
    ),
    Alias(
        nl_phrases=["not next to", "not beside", "not adjacent to",
                     "not neighbor of"],
        canonical="ADJACENT",
        negate=True,
    ),

    # --- Co-occurrence: same house ---
    Alias(
        nl_phrases=["in the same house as", "lives with", "same position as",
                     "shares a house with", "is the person who"],
        canonical="CO_OCCURRENCE",
    ),
    Alias(
        nl_phrases=["not in the same house as", "different house from",
                     "does not live with", "is not the person who"],
        canonical="CO_OCCURRENCE",
        negate=True,
    ),

    # --- Assignment ---
    Alias(
        nl_phrases=["is in house", "lives in house", "is at position",
                     "is found at", "found at position"],
        canonical="ASSIGNMENT",
    ),
    Alias(
        nl_phrases=["is not in house", "does not live in house",
                     "is not at position", "is not found at"],
        canonical="EXCLUSION",
    ),

    # --- Between ---
    Alias(
        nl_phrases=["between", "in between", "somewhere between"],
        canonical="BETWEEN",
        notes="idx(a) < idx(b) < idx(c) in either direction",
    ),
]


def resolve_alias(nl_phrase: str) -> Alias | None:
    """Find the alias that best matches an NL phrase (case-insensitive).

    Prefers longer (more specific) matches over shorter ones.
    """
    nl_lower = nl_phrase.lower().strip()
    best_match: Alias | None = None
    best_length = 0
    for alias in ALIASES:
        for pattern in alias.nl_phrases:
            if pattern in nl_lower and len(pattern) > best_length:
                best_match = alias
                best_length = len(pattern)
    return best_match


def get_aliases_for_prompt() -> str:
    """Format alias table for inclusion in an LLM prompt."""
    lines = ["## FRL Alias Table", "",
             "Multiple NL phrases map to the same canonical FRL constraint.", ""]

    # Group by canonical type
    by_canonical: dict[str, list[Alias]] = {}
    for a in ALIASES:
        key = f"{'NOT ' if a.negate else ''}{a.canonical}"
        by_canonical.setdefault(key, []).append(a)

    for canonical, aliases in by_canonical.items():
        all_phrases = []
        for a in aliases:
            all_phrases.extend(a.nl_phrases)
        lines.append(f"**{canonical}**: {', '.join(repr(p) for p in all_phrases)}")
        for a in aliases:
            if a.swap_entities:
                lines.append(f"  ⚠ Swap entity order when using: {', '.join(repr(p) for p in a.nl_phrases)}")
            if a.notes:
                lines.append(f"  Note: {a.notes}")
        lines.append("")

    return "\n".join(lines)


def get_rules_for_prompt() -> str:
    """Format all disambiguation rules for inclusion in an LLM prompt."""
    lines = ["## FRL Disambiguation Rules", ""]
    for rule in RULES:
        lines.append(f"### {rule.id}")
        lines.append(f"NL triggers: {', '.join(repr(p) for p in rule.nl_patterns)}")
        lines.append(f"Could mean: {' | '.join(rule.candidates)}")
        lines.append(f"How to decide: {rule.resolution}")
        lines.append(f"Default: {rule.default}")
        if rule.flag:
            lines.append(f"Flag: {rule.flag}")
        lines.append("")
    return "\n".join(lines)


def get_rule(rule_id: str) -> DisambiguationRule | None:
    """Look up a disambiguation rule by ID."""
    for r in RULES:
        if r.id == rule_id:
            return r
    return None
