#!/usr/bin/env bash
# Test frontier LLM on raw NL problems (no FRL, no solver).
# Compares raw LLM answers to verified Z3 answers.
#
# Usage: ./scripts/baseline_llm_test.sh [rate_limit_seconds]
# Default rate limit: 5 seconds between calls

set -euo pipefail

CLAUDE="/Users/satya/.local/bin/claude"
RATE_LIMIT="${1:-5}"
RESULTS_DIR="experiments/baseline_llm"
mkdir -p "$RESULTS_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="$RESULTS_DIR/results_${TIMESTAMP}.jsonl"

echo "=== Baseline LLM Test ==="
echo "Rate limit: ${RATE_LIMIT}s between calls"
echo "Results: $RESULTS_FILE"
echo ""

# Problems with known answers (from our verified Z3 solutions)
declare -a PROBLEMS
declare -a EXPECTED
declare -a IDS

# --- Logic Grid Problems ---

IDS+=("logic_3x3_simple")
EXPECTED+=("Alice does not do Cleanup. Valid assignments include Alice→Setup or Alice→Cooking.")
PROBLEMS+=("Three friends — Alice, Bob, and Carol — each volunteer for exactly one task. The tasks are Setup, Cooking, and Cleanup. Each task is done by exactly one person. Alice refuses to do Cleanup. What is a valid assignment of people to tasks? Give ONLY the assignment, one per line: Name → Task")

IDS+=("zebralogic_3x3")
EXPECTED+=("H1: Peter, Yellow, Bella. H2: Arnold, Red, Fred. H3: Eric, White, Meredith")
PROBLEMS+=("There are 3 houses, numbered 1 to 3 from left to right. Each house is occupied by a different person with a unique name, favorite color, and child.
Names: Peter, Eric, Arnold. Colors: red, white, yellow. Children: Fred, Meredith, Bella.
Clues:
1. Arnold is the person whose favorite color is red.
2. The person whose child is named Fred is somewhere to the left of Eric.
3. The person whose favorite color is red is in the second house.
4. The person whose child is named Bella is in the first house.
5. The person who loves white is the person whose child is named Meredith.
Give the complete solution as: House N: Name, Color, Child")

IDS+=("zebra_puzzle")
EXPECTED+=("Japanese owns zebra. Norwegian drinks water.")
PROBLEMS+=("There are five houses in a row, numbered 1 to 5. Each has a different nationality, color, drink, smoke brand, and pet.
1. The Englishman lives in the red house.
2. The Spaniard owns the dog.
3. Coffee is drunk in the green house.
4. The Ukrainian drinks tea.
5. The green house is immediately to the right of the ivory house.
6. The Old Gold smoker owns snails.
7. Kools are smoked in the yellow house.
8. Milk is drunk in the middle house.
9. The Norwegian lives in the first house.
10. The Chesterfields smoker lives next to the fox owner.
11. Kools are smoked next to the house where the horse is kept.
12. The Lucky Strike smoker drinks orange juice.
13. The Japanese smokes Parliaments.
14. The Norwegian lives next to the blue house.
Who owns the zebra? Who drinks water? Give the full house-by-house solution.")

# --- Arithmetic Problems (GSM8K) ---

IDS+=("gsm8k_0")
EXPECTED+=("18")
PROBLEMS+=("Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for \$2 per fresh duck egg. How much in dollars does she make every day at the farmers' market? Give ONLY the numeric answer.")

IDS+=("gsm8k_50")
EXPECTED+=("294")
PROBLEMS+=("Lloyd has an egg farm. His chickens produce 252 eggs per day and he sells them for \$2 per dozen. How much does Lloyd make on eggs per week? Give ONLY the numeric answer.")

IDS+=("gsm8k_200")
EXPECTED+=("55")
PROBLEMS+=("Baldur gets water from a well. He gets 5 pails of water every morning and 6 pails of water every afternoon. If each pail contains 5 liters of water, how many liters of water does he get every day? Give ONLY the numeric answer.")

IDS+=("gsm8k_500")
EXPECTED+=("16")
PROBLEMS+=("Together Lily, David, and Bodhi collected 43 insects. Lily found 7 more than David. David found half of what Bodhi found. How many insects did Lily find? Give ONLY the numeric answer.")

IDS+=("gsm8k_800")
EXPECTED+=("428")
PROBLEMS+=("Pierson scored 278 points in one game of bowling. Nikita scored 11 more than half as many as Pierson. How many points did Pierson and Nikita have in total? Give ONLY the numeric answer.")

# --- UNSAT Problem ---

IDS+=("unsat_pigeonhole")
EXPECTED+=("IMPOSSIBLE")
PROBLEMS+=("Four workers — Kim, Leo, Mia, and Nate — must each be assigned to exactly one project: Alpha, Beta, Gamma, or Delta. Each project needs exactly one worker. All four workers will only work on Alpha or Beta. Is there a valid assignment? Answer POSSIBLE or IMPOSSIBLE and explain why.")

echo "Running ${#PROBLEMS[@]} problems..."
echo ""

CORRECT=0
WRONG=0
ERRORS=0

for i in "${!PROBLEMS[@]}"; do
    ID="${IDS[$i]}"
    PROBLEM="${PROBLEMS[$i]}"
    EXPECT="${EXPECTED[$i]}"

    echo "--- [$((i+1))/${#PROBLEMS[@]}] $ID ---"
    echo "Expected: $EXPECT"

    # Call claude with the problem
    RESPONSE=$("$CLAUDE" -p "$PROBLEM" --model sonnet 2>/dev/null) || {
        echo "ERROR: claude call failed"
        ERRORS=$((ERRORS + 1))
        echo "{\"id\":\"$ID\",\"status\":\"error\",\"expected\":\"$EXPECT\",\"response\":\"\"}" >> "$RESULTS_FILE"
        sleep "$RATE_LIMIT"
        continue
    }

    # Truncate response for display
    DISPLAY_RESP=$(echo "$RESPONSE" | head -20)
    echo "Response: $DISPLAY_RESP"
    echo ""

    # Save full result with problem text
    python3 -c "
import json, sys
result = {
    'id': sys.argv[1],
    'problem': sys.argv[2],
    'expected': sys.argv[3],
    'response': sys.argv[4],
}
print(json.dumps(result))
" "$ID" "$PROBLEM" "$EXPECT" "$RESPONSE" >> "$RESULTS_FILE"

    sleep "$RATE_LIMIT"
done

echo ""
echo "=== Done ==="
echo "Results saved to: $RESULTS_FILE"
echo "Review results and manually score correctness."
echo ""
echo "To score, run:"
echo "  python3 scripts/score_baseline.py $RESULTS_FILE"
