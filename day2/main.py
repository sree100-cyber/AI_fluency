"""
main.py
-------
Main execution script for Day 2 Task:
Agentic AI: Foundations and Open-Source Practice.
Runs comparison benchmark, self-consistency experiment, and screenshot generation.
"""

from comparison import run_benchmark
from self_consistency import run_self_consistency
from generate_screenshots import generate_all_screenshots


def main():
    print("\n=========================================================================")
    print("      DAY 2: AGENTIC AI FOUNDATIONS - COMPARATIVE BENCHMARK RUNNER       ")
    print("=========================================================================\n")

    # Step 1: Run Comparative Benchmark (Direct Prompting vs CoT vs ReAct)
    print("[1/3] Running Comparative Benchmark across Scenario Questions...")
    run_benchmark()

    # Step 2: Run Self-Consistency Experiment
    print("\n[2/3] Running CoT Self-Consistency Experiment (T=0.7 vs T=0.0)...")
    run_self_consistency(num_samples=10, temperature=0.7)

    # Step 3: Generate Terminal Output Screenshots
    print("\n[3/3] Generating Output Screenshots in 'screenshots/' directory...")
    generate_all_screenshots()

    print("\n=========================================================================")
    print(" SUCCESS: All evaluations complete. Code and screenshots generated!")
    print("=========================================================================\n")


if __name__ == "__main__":
    main()
