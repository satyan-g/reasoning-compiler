#!/usr/bin/env python3
"""
Run the viability check experiment against multiple LLM providers.

This script:
1. Loads the 20 test problems
2. Sends each problem to configured models
3. Collects responses with metadata (tokens, latency, etc.)
4. Saves raw responses for later analysis

Supports: Groq (Llama, Mixtral), Google (Gemini) - FREE TIER ONLY
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import os


@dataclass
class ModelResponse:
    """Response from a model on a single problem."""
    problem_id: str
    model: str
    response_text: str
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    timestamp: str
    error: str = None


class ExperimentRunner:
    """Runs viability check across multiple models."""

    def __init__(self, problems_path: Path, output_dir: Path):
        self.problems_path = problems_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load problems
        with open(problems_path) as f:
            self.problems = [json.loads(line) for line in f]

        print(f"Loaded {len(self.problems)} problems from {problems_path}")

    def run_groq(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """Run problems against Groq (Llama/Mixtral models)."""
        try:
            from groq import Groq
        except ImportError:
            print("⚠ Groq SDK not installed. Run: pip install groq")
            return

        client = Groq(api_key=api_key)
        responses = []

        for i, problem in enumerate(self.problems, 1):
            print(f"[{i}/{len(self.problems)}] Testing {problem['id']} on {model}...")

            prompt = f"""Solve this problem step by step. Show your reasoning clearly.

Problem:
{problem['text']}

Provide your answer and explain your reasoning process."""

            try:
                start_time = time.time()

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4096,
                    temperature=0.7
                )

                latency = time.time() - start_time

                model_response = ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text=response.choices[0].message.content,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    latency_seconds=latency,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )

                responses.append(model_response)
                print(f"  ✓ {response.usage.completion_tokens} output tokens, {latency:.1f}s")

                # Groq free tier rate limit: 30 req/min
                time.sleep(2)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                responses.append(ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text="",
                    input_tokens=0,
                    output_tokens=0,
                    latency_seconds=0,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    error=str(e)
                ))

        self._save_responses(responses, f"groq_{model.replace('-', '_')}")
        return responses

    def run_anthropic(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """Run problems against Anthropic Claude."""
        try:
            from anthropic import Anthropic
        except ImportError:
            print("⚠ Anthropic SDK not installed. Run: pip install anthropic")
            return

        client = Anthropic(api_key=api_key)
        responses = []

        for i, problem in enumerate(self.problems, 1):
            print(f"[{i}/{len(self.problems)}] Testing {problem['id']} on {model}...")

            # Construct prompt
            prompt = f"""Solve this problem step by step. Show your reasoning clearly.

Problem:
{problem['text']}

Provide your answer and explain your reasoning process."""

            try:
                start_time = time.time()

                # Enable extended thinking for Claude
                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 10000
                    },
                    messages=[{"role": "user", "content": prompt}]
                )

                latency = time.time() - start_time

                # Extract response text (including thinking if present)
                response_text = ""
                for block in response.content:
                    if block.type == "thinking":
                        response_text += f"[THINKING]\n{block.thinking}\n\n"
                    elif block.type == "text":
                        response_text += block.text

                model_response = ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text=response_text,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    latency_seconds=latency,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )

                responses.append(model_response)
                print(f"  ✓ {response.usage.output_tokens} output tokens, {latency:.1f}s")

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                responses.append(ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text="",
                    input_tokens=0,
                    output_tokens=0,
                    latency_seconds=0,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    error=str(e)
                ))

        # Save responses
        self._save_responses(responses, f"anthropic_{model.replace('-', '_')}")
        return responses

    def run_openai(self, api_key: str, model: str = "gpt-4o"):
        """Run problems against OpenAI GPT."""
        try:
            from openai import OpenAI
        except ImportError:
            print("⚠ OpenAI SDK not installed. Run: pip install openai")
            return

        client = OpenAI(api_key=api_key)
        responses = []

        for i, problem in enumerate(self.problems, 1):
            print(f"[{i}/{len(self.problems)}] Testing {problem['id']} on {model}...")

            prompt = f"""Solve this problem step by step. Show your reasoning clearly.

Problem:
{problem['text']}

Provide your answer and explain your reasoning process."""

            try:
                start_time = time.time()

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4096
                )

                latency = time.time() - start_time

                model_response = ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text=response.choices[0].message.content,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    latency_seconds=latency,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )

                responses.append(model_response)
                print(f"  ✓ {response.usage.completion_tokens} output tokens, {latency:.1f}s")

                time.sleep(1)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                responses.append(ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text="",
                    input_tokens=0,
                    output_tokens=0,
                    latency_seconds=0,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    error=str(e)
                ))

        self._save_responses(responses, f"openai_{model.replace('-', '_')}")
        return responses

    def run_google(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """Run problems against Google Gemini."""
        try:
            import google.generativeai as genai
        except ImportError:
            print("⚠ Google Generative AI SDK not installed. Run: pip install google-generativeai")
            return

        genai.configure(api_key=api_key)
        gemini = genai.GenerativeModel(model)
        responses = []

        for i, problem in enumerate(self.problems, 1):
            print(f"[{i}/{len(self.problems)}] Testing {problem['id']} on {model}...")

            prompt = f"""Solve this problem step by step. Show your reasoning clearly.

Problem:
{problem['text']}

Provide your answer and explain your reasoning process."""

            try:
                start_time = time.time()

                response = gemini.generate_content(prompt)

                latency = time.time() - start_time

                # Gemini doesn't always provide token counts in the response
                # We'll approximate or use 0 if not available
                input_tokens = 0
                output_tokens = 0
                if hasattr(response, 'usage_metadata'):
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

                model_response = ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text=response.text,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_seconds=latency,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )

                responses.append(model_response)
                print(f"  ✓ {output_tokens} output tokens, {latency:.1f}s")

                time.sleep(1)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                responses.append(ModelResponse(
                    problem_id=problem['id'],
                    model=model,
                    response_text="",
                    input_tokens=0,
                    output_tokens=0,
                    latency_seconds=0,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    error=str(e)
                ))

        self._save_responses(responses, f"google_{model.replace('-', '_')}")
        return responses

    def _save_responses(self, responses: List[ModelResponse], filename_prefix: str):
        """Save responses to JSONL."""
        output_path = self.output_dir / f"{filename_prefix}_responses.jsonl"
        with open(output_path, "w") as f:
            for response in responses:
                f.write(json.dumps(asdict(response)) + "\n")
        print(f"✓ Saved {len(responses)} responses to {output_path}")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent
    problems_path = base_dir / "problems" / "problems.jsonl"
    output_dir = base_dir / "responses"

    runner = ExperimentRunner(problems_path, output_dir)

    # Check for API keys in environment
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    print("\n" + "="*60)
    print("VIABILITY CHECK EXPERIMENT - FREE TIER ONLY")
    print("="*60 + "\n")

    # Run experiments for each available provider
    if groq_key:
        print("\n--- Running Groq: Llama 3.3 70B (already completed) ---")
        # runner.run_groq(groq_key, "llama-3.3-70b-versatile")  # Already done!
        print("Skipping - results already saved")

        print("\n--- Running Groq: Llama 3.1 8B ---")
        runner.run_groq(groq_key, "llama-3.1-8b-instant")
    else:
        print("⚠ GROQ_API_KEY not set, skipping Groq models")

    if google_key:
        print("\n--- Running Google: Gemini 2.5 Flash ---")
        runner.run_google(google_key, "gemini-2.5-flash")

        print("\n--- Running Google: Gemini 2.0 Flash ---")
        runner.run_google(google_key, "gemini-2.0-flash")
    else:
        print("⚠ GOOGLE_API_KEY not set, skipping Google models")

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review responses in:", output_dir)
    print("2. Run analysis: python analyze_results.py")


if __name__ == "__main__":
    main()
