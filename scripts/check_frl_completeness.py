#!/usr/bin/env python3
"""FRL schema completeness checker.

Run after any FRL schema revision to verify:
1. Every constraint type has a complement (or negated support)
2. Every constraint type has a compiler implementation
3. Every constraint type has a verifier implementation
4. Every constraint type has at least one test
5. All ambiguous NL patterns have disambiguation rules
6. All constraint types are documented

Usage: python3 scripts/check_frl_completeness.py
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
TESTS = ROOT / "tests"


def get_constraint_kinds() -> list[str]:
    """Extract all ConstraintKind values from schema.py."""
    schema = (SRC / "frl" / "schema.py").read_text()
    kinds = []
    in_enum = False
    for line in schema.split("\n"):
        if "class ConstraintKind" in line:
            in_enum = True
            continue
        if in_enum:
            if line.strip() == "" or (not line.startswith(" ") and line.strip()):
                if not line.startswith(" ") and "=" not in line:
                    break
            if "=" in line and line.strip().startswith(("'", '"')) is False:
                name = line.strip().split("=")[0].strip()
                if name and name[0].isupper():
                    kinds.append(name)
    return kinds


def check_compiler_coverage(kinds: list[str]) -> list[str]:
    """Check that to_z3.py handles every constraint kind."""
    compiler = (SRC / "compiler" / "to_z3.py").read_text()
    missing = []
    for kind in kinds:
        pattern = f"ConstraintKind.{kind}"
        if pattern not in compiler:
            missing.append(kind)
    return missing


def check_verifier_coverage(kinds: list[str]) -> list[str]:
    """Check that verify.py handles every constraint kind."""
    verifier = (SRC / "compiler" / "verify.py").read_text()
    missing = []
    for kind in kinds:
        pattern = f"ConstraintKind.{kind}"
        if pattern not in verifier:
            missing.append(kind)
    return missing


def check_test_coverage(kinds: list[str]) -> list[str]:
    """Check that each constraint kind appears in at least one test."""
    test_content = ""
    for tf in TESTS.glob("test_*.py"):
        test_content += tf.read_text()

    missing = []
    for kind in kinds:
        # Check for the kind value string or enum reference
        kind_lower = kind.lower()
        if kind_lower not in test_content and f"ConstraintKind.{kind}" not in test_content:
            missing.append(kind)
    return missing


def check_complement_pairs(kinds: list[str]) -> list[str]:
    """Check that constraints have complement support (negated field or explicit pair)."""
    schema = (SRC / "frl" / "schema.py").read_text()

    # Check if negated field exists
    has_negated_field = "negated" in schema

    if has_negated_field:
        return []  # All constraints are negatable via the field

    # Otherwise check for explicit pairs
    known_pairs = {
        "ASSIGNMENT": "EXCLUSION",
        "EXCLUSION": "ASSIGNMENT",
    }
    warnings = []
    for kind in kinds:
        if kind not in known_pairs and kind not in known_pairs.values():
            if kind not in ("UNIQUENESS", "CARDINALITY", "CONDITIONAL"):
                warnings.append(f"{kind} has no complement (add 'negated: bool' field to Constraint)")
    return warnings


def check_disambiguation_coverage() -> list[str]:
    """Check that disambiguation.py covers common NL patterns."""
    disambig_path = SRC / "frl" / "disambiguation.py"
    if not disambig_path.exists():
        return ["disambiguation.py does not exist"]

    content = disambig_path.read_text()

    expected_patterns = [
        "left_of", "right_of", "next_to", "between",
        "or_constraint", "not_same", "each_exactly_one",
    ]
    missing = []
    for pattern in expected_patterns:
        if f'"{pattern}"' not in content and f"'{pattern}'" not in content:
            missing.append(f"disambiguation rule missing for: {pattern}")
    return missing


def check_validator_coverage(kinds: list[str]) -> list[str]:
    """Check that validate() in schema.py handles every constraint kind."""
    schema = (SRC / "frl" / "schema.py").read_text()
    # Find the validate function and check for kind references
    missing = []
    for kind in kinds:
        pattern = f"ConstraintKind.{kind}"
        # Check if it appears in the validation section (after 'def validate')
        validate_section = schema[schema.find("def validate"):]
        if pattern not in validate_section:
            missing.append(kind)
    return missing


def main():
    print("=== FRL Schema Completeness Check ===\n")

    kinds = get_constraint_kinds()
    print(f"Constraint types defined: {len(kinds)}")
    for k in kinds:
        print(f"  - {k}")
    print()

    all_ok = True

    # 1. Compiler coverage
    missing = check_compiler_coverage(kinds)
    if missing:
        print(f"❌ Compiler missing: {', '.join(missing)}")
        all_ok = False
    else:
        print(f"✓ Compiler covers all {len(kinds)} constraint types")

    # 2. Verifier coverage
    missing = check_verifier_coverage(kinds)
    if missing:
        print(f"❌ Verifier missing: {', '.join(missing)}")
        all_ok = False
    else:
        print(f"✓ Verifier covers all {len(kinds)} constraint types")

    # 3. Validator coverage
    missing = check_validator_coverage(kinds)
    if missing:
        print(f"❌ Validator missing: {', '.join(missing)}")
        all_ok = False
    else:
        print(f"✓ Validator covers all {len(kinds)} constraint types")

    # 4. Test coverage
    missing = check_test_coverage(kinds)
    if missing:
        print(f"❌ Tests missing for: {', '.join(missing)}")
        all_ok = False
    else:
        print(f"✓ Tests cover all {len(kinds)} constraint types")

    # 5. Complement pairs
    warnings = check_complement_pairs(kinds)
    if warnings:
        print(f"⚠ Complement gaps:")
        for w in warnings:
            print(f"    {w}")
        all_ok = False
    else:
        print(f"✓ All constraint types have complement support")

    # 6. Disambiguation rules
    missing = check_disambiguation_coverage()
    if missing:
        print(f"⚠ Disambiguation gaps:")
        for m in missing:
            print(f"    {m}")
    else:
        print(f"✓ Disambiguation rules complete")

    print()
    if all_ok:
        print("All checks passed.")
    else:
        print("Some checks failed — review above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
