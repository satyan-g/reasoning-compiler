#!/usr/bin/env python3
"""
Analyze results from the viability check experiment.

This script:
1. Loads all model responses
2. Evaluates correctness (manual annotation needed)
3. Computes metrics: accuracy, token costs, failure modes
4. Generates decision recommendation based on criteria
5. Outputs summary and analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ProblemResult:
    """Result for a single problem."""
    problem_id: str
    category: str
    model: str
    is_correct: bool
    expresses_uncertainty: bool
    failure_mode: str  # correct, wrong_confident, wrong_uncertain, requests_clarification, partial
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    notes: str = ""


class ResultsAnalyzer:
    """Analyze experiment results."""

    def __init__(self, problems_path: Path, responses_dir: Path, annotations_path: Path = None):
        self.problems_path = problems_path
        self.responses_dir = responses_dir
        self.annotations_path = annotations_path

        # Load problems
        with open(problems_path) as f:
            self.problems = {json.loads(line)['id']: json.loads(line) for line in f}

        # Load responses
        self.responses = self._load_responses()

        # Load annotations if available
        self.annotations = {}
        if annotations_path and annotations_path.exists():
            with open(annotations_path) as f:
                self.annotations = json.load(f)

    def _load_responses(self) -> Dict[str, List[Dict]]:
        """Load all response files."""
        responses_by_model = defaultdict(list)

        for response_file in self.responses_dir.glob("*_responses.jsonl"):
            with open(response_file) as f:
                for line in f:
                    response = json.loads(line)
                    responses_by_model[response['model']].append(response)

        return dict(responses_by_model)

    def create_annotation_template(self) -> Path:
        """Create a template for manual annotation of results."""
        template = {
            "instructions": """
For each problem-model pair, provide:
- is_correct: true/false
- expresses_uncertainty: true/false (did model signal uncertainty?)
- failure_mode: one of [correct, wrong_confident, wrong_uncertain, requests_clarification, partial]
- notes: any observations

Some problems have deliberately incorrect ground truth to test verification.
Check the problem notes.
            """.strip(),
            "problems": {}
        }

        for model, responses in self.responses.items():
            for response in responses:
                problem_id = response['problem_id']
                key = f"{problem_id}_{model}"

                template["problems"][key] = {
                    "problem_id": problem_id,
                    "model": model,
                    "category": self.problems[problem_id]['category'],
                    "problem_text": self.problems[problem_id]['text'],
                    "response_text": response['response_text'][:500] + "..." if len(response['response_text']) > 500 else response['response_text'],
                    "ground_truth": self.problems[problem_id].get('ground_truth'),
                    "problem_notes": self.problems[problem_id].get('notes', ''),
                    # Fields to fill in:
                    "is_correct": None,
                    "expresses_uncertainty": None,
                    "failure_mode": None,
                    "notes": ""
                }

        output_path = self.responses_dir.parent / "annotations_template.json"
        with open(output_path, "w") as f:
            json.dump(template, f, indent=2)

        print(f"✓ Created annotation template: {output_path}")
        print(f"  Please review and fill in the evaluation fields, then save as 'annotations.json'")
        return output_path

    def compute_metrics(self) -> Dict[str, Any]:
        """Compute metrics from annotated results."""
        if not self.annotations:
            print("⚠ No annotations found. Run create_annotation_template() first.")
            return {}

        results_by_model = defaultdict(list)
        results_by_category = defaultdict(list)

        # Process annotations
        for key, annotation in self.annotations.get("problems", {}).items():
            if annotation.get('is_correct') is None:
                continue  # Skip unannotated

            result = ProblemResult(
                problem_id=annotation['problem_id'],
                category=annotation['category'],
                model=annotation['model'],
                is_correct=annotation['is_correct'],
                expresses_uncertainty=annotation.get('expresses_uncertainty', False),
                failure_mode=annotation.get('failure_mode', 'unknown'),
                input_tokens=0,  # Will be filled from responses
                output_tokens=0,
                latency_seconds=0,
                notes=annotation.get('notes', '')
            )

            # Add token data from responses
            for response in self.responses.get(annotation['model'], []):
                if response['problem_id'] == annotation['problem_id']:
                    result.input_tokens = response['input_tokens']
                    result.output_tokens = response['output_tokens']
                    result.latency_seconds = response['latency_seconds']
                    break

            results_by_model[annotation['model']].append(result)
            results_by_category[annotation['category']].append(result)

        # Compute aggregate metrics
        metrics = {
            "by_model": {},
            "by_category": {},
            "overall": {}
        }

        # Per-model metrics
        for model, results in results_by_model.items():
            correct = sum(1 for r in results if r.is_correct)
            total = len(results)
            accuracy = correct / total if total > 0 else 0

            avg_tokens = sum(r.output_tokens for r in results) / total if total > 0 else 0
            avg_latency = sum(r.latency_seconds for r in results) / total if total > 0 else 0

            failure_modes = defaultdict(int)
            for r in results:
                failure_modes[r.failure_mode] += 1

            metrics["by_model"][model] = {
                "accuracy": accuracy,
                "correct": correct,
                "total": total,
                "avg_output_tokens": avg_tokens,
                "avg_latency_seconds": avg_latency,
                "failure_modes": dict(failure_modes)
            }

        # Per-category metrics
        for category, results in results_by_category.items():
            correct = sum(1 for r in results if r.is_correct)
            total = len(results)
            accuracy = correct / total if total > 0 else 0

            metrics["by_category"][category] = {
                "accuracy": accuracy,
                "correct": correct,
                "total": total
            }

        # Overall
        all_results = [r for results in results_by_model.values() for r in results]
        if all_results:
            overall_correct = sum(1 for r in all_results if r.is_correct)
            overall_total = len(all_results)
            metrics["overall"] = {
                "accuracy": overall_correct / overall_total,
                "correct": overall_correct,
                "total": overall_total
            }

        return metrics

    def make_decision(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decision criteria from config."""
        if not metrics:
            return {"decision": "no_data", "reason": "No annotated data available"}

        overall_accuracy = metrics.get("overall", {}).get("accuracy", 0)

        # Decision logic from config
        if overall_accuracy < 0.70:
            return {
                "decision": "proceed_paper_1",
                "reason": f"Overall accuracy {overall_accuracy:.1%} < 70%. Models still fail frequently on high-fertility problems. Proceed with fertility diagnostic paper as planned.",
                "accuracy": overall_accuracy
            }
        elif overall_accuracy > 0.90:
            # Check token costs
            avg_tokens = sum(
                m.get("avg_output_tokens", 0)
                for m in metrics.get("by_model", {}).values()
            ) / len(metrics.get("by_model", {})) if metrics.get("by_model") else 0

            if avg_tokens > 2000:
                return {
                    "decision": "pivot_efficiency",
                    "reason": f"Overall accuracy {overall_accuracy:.1%} > 90%, but avg output tokens {avg_tokens:.0f} is high. Pivot to efficiency story: fertility predicts token cost.",
                    "accuracy": overall_accuracy,
                    "avg_tokens": avg_tokens
                }
            else:
                return {
                    "decision": "pivot_verification",
                    "reason": f"Overall accuracy {overall_accuracy:.1%} > 90% with reasonable token costs. Skip Paper 1, go directly to verification/certification story (Paper 2).",
                    "accuracy": overall_accuracy
                }
        else:
            return {
                "decision": "borderline",
                "reason": f"Overall accuracy {overall_accuracy:.1%} is borderline (70-90%). Consider which problems models fail on and whether those failures are interesting.",
                "accuracy": overall_accuracy
            }

    def generate_summary(self, metrics: Dict[str, Any], decision: Dict[str, Any]) -> str:
        """Generate markdown summary."""
        summary = []
        summary.append("# Viability Check Experiment 1 - Results Summary\n")
        summary.append(f"**Date:** 2026-02-22\n")
        summary.append("## Research Question\n")
        summary.append("Do current reasoning models still fail on high-fertility constraint problems?\n")

        summary.append("## Overall Results\n")
        if metrics.get("overall"):
            ov = metrics["overall"]
            summary.append(f"- **Accuracy:** {ov['accuracy']:.1%} ({ov['correct']}/{ov['total']})\n")

        summary.append("\n## Results by Model\n")
        for model, m in metrics.get("by_model", {}).items():
            summary.append(f"### {model}\n")
            summary.append(f"- Accuracy: {m['accuracy']:.1%} ({m['correct']}/{m['total']})\n")
            summary.append(f"- Avg output tokens: {m['avg_output_tokens']:.0f}\n")
            summary.append(f"- Avg latency: {m['avg_latency_seconds']:.1f}s\n")
            summary.append("- Failure modes:\n")
            for mode, count in m['failure_modes'].items():
                summary.append(f"  - {mode}: {count}\n")
            summary.append("\n")

        summary.append("## Results by Problem Category\n")
        for category, c in metrics.get("by_category", {}).items():
            summary.append(f"- **{category}:** {c['accuracy']:.1%} ({c['correct']}/{c['total']})\n")

        summary.append("\n## Decision\n")
        summary.append(f"**Recommendation:** {decision['decision']}\n\n")
        summary.append(f"{decision['reason']}\n")

        return "".join(summary)


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent
    problems_path = base_dir / "problems" / "problems.jsonl"
    responses_dir = base_dir / "responses"
    annotations_path = base_dir / "annotations.json"

    analyzer = ResultsAnalyzer(problems_path, responses_dir, annotations_path)

    # Check if annotations exist
    if not annotations_path.exists():
        print("No annotations found. Creating template...\n")
        analyzer.create_annotation_template()
        print("\n⚠ Manual annotation required before analysis can proceed.")
        print("  1. Open the annotations_template.json file")
        print("  2. For each problem-model pair, fill in:")
        print("     - is_correct (true/false)")
        print("     - expresses_uncertainty (true/false)")
        print("     - failure_mode (correct/wrong_confident/wrong_uncertain/requests_clarification/partial)")
        print("     - notes (optional observations)")
        print("  3. Save as 'annotations.json' in the same directory")
        print("  4. Re-run this script")
        return

    # Compute metrics
    print("Computing metrics...\n")
    metrics = analyzer.compute_metrics()

    # Make decision
    decision = analyzer.make_decision(metrics)

    # Generate summary
    summary = analyzer.generate_summary(metrics, decision)

    # Save outputs
    summary_path = base_dir / "SUMMARY.md"
    with open(summary_path, "w") as f:
        f.write(summary)

    decision_path = base_dir / "DECISION.md"
    with open(decision_path, "w") as f:
        f.write(f"# Decision: {decision['decision']}\n\n")
        f.write(f"{decision['reason']}\n")

    analysis_path = base_dir / "analysis.json"
    with open(analysis_path, "w") as f:
        json.dump({"metrics": metrics, "decision": decision}, f, indent=2)

    # Print summary
    print(summary)
    print(f"\n✓ Saved summary to {summary_path}")
    print(f"✓ Saved decision to {decision_path}")
    print(f"✓ Saved detailed analysis to {analysis_path}")


if __name__ == "__main__":
    main()
