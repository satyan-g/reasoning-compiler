#!/usr/bin/env python3
"""Score baseline LLM results against expected answers.

Usage: python3 scripts/score_baseline.py experiments/baseline_llm/results_*.jsonl
"""

import json
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/score_baseline.py <results_file>")
        sys.exit(1)

    results_file = sys.argv[1]
    results = []
    with open(results_file) as f:
        for line in f:
            results.append(json.loads(line))

    print(f"=== Scoring {len(results)} results from {results_file} ===\n")

    for i, r in enumerate(results):
        print(f"--- [{i+1}] {r['id']} ---")
        print(f"Problem:  {r.get('problem', 'N/A')[:300]}")
        print()
        print(f"Expected: {r['expected']}")
        print()
        print(f"Response: {r['response'][:500]}")
        print()

        while True:
            score = input("Score (c=correct, w=wrong, p=partial, s=skip): ").strip().lower()
            if score in ("c", "w", "p", "s"):
                r["score"] = {"c": "correct", "w": "wrong", "p": "partial", "s": "skipped"}[score]
                break

        print()

    # Summary
    scored = [r for r in results if r.get("score") != "skipped"]
    correct = sum(1 for r in scored if r["score"] == "correct")
    partial = sum(1 for r in scored if r["score"] == "partial")
    wrong = sum(1 for r in scored if r["score"] == "wrong")

    print(f"=== Summary ===")
    print(f"Correct: {correct}/{len(scored)} ({100*correct/len(scored):.0f}%)")
    print(f"Partial: {partial}/{len(scored)}")
    print(f"Wrong:   {wrong}/{len(scored)}")
    print()

    # Save scored results
    scored_file = results_file.replace(".jsonl", "_scored.jsonl")
    with open(scored_file, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Scored results saved to: {scored_file}")


if __name__ == "__main__":
    main()
