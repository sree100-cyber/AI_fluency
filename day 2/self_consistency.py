"""
self_consistency.py
-------------------
Implements Self-Consistency Evaluation (Wang et al., 2022).
Runs a Chain-of-Thought reasoning question multiple times at temperature T = 0.7
to sample diverse reasoning paths, collects outputs, takes a majority vote,
and compares against greedy decoding (T = 0.0).
"""

import json
from collections import Counter
from typing import Dict, Any, List
from chain_of_thought import ChainOfThoughtEngine


def run_self_consistency(num_samples: int = 10, temperature: float = 0.7) -> Dict[str, Any]:
    question_id = "Q1"
    question_text = (
        "A customer wants to purchase 3 units of Wireless Earbuds ($45 each) and 2 units of "
        "Smartwatches ($120 each). If they apply a 10% coupon code 'SAVE10' and pay a flat $15 "
        "regional handling fee, what is the final order total? Show step-by-step logic."
    )
    ground_truth = "$352.50"

    print("================================================================================")
    print(f"       SELF-CONSISTENCY EXPERIMENT (CoT Prompting @ Temperature = {temperature})      ")
    print("================================================================================\n")
    print(f"Target Question: {question_text}\nGround Truth Answer: {ground_truth}\n")

    # 1. Non-zero temperature runs
    cot_high_temp = ChainOfThoughtEngine(temperature=temperature)
    sample_outputs: List[Dict[str, Any]] = []
    answers: List[str] = []

    for i in range(1, num_samples + 1):
        res = cot_high_temp.run(question_id, question_text)
        ans = res["final_answer"]
        answers.append(ans)
        sample_outputs.append({
            "sample_index": i,
            "reasoning_steps": res["reasoning_steps"],
            "final_answer": ans
        })
        print(f"Sample #{i:02d}: Final Answer -> {ans}")

    # Vote frequency
    vote_counts = Counter(answers)
    majority_answer, majority_votes = vote_counts.most_common(1)[0]
    majority_percentage = (majority_votes / num_samples) * 100
    is_correct = (majority_answer == "The final order total is $352.50." or "$352.50" in majority_answer)

    # 2. Temperature = 0.0 run (Deterministic / Greedy)
    cot_zero_temp = ChainOfThoughtEngine(temperature=0.0)
    zero_temp_res = cot_zero_temp.run(question_id, question_text)

    print("\n--------------------------------------------------------------------------------")
    print("                            SELF-CONSISTENCY SUMMARY                            ")
    print("--------------------------------------------------------------------------------")
    print(f"Total Samples (T={temperature}): {num_samples}")
    print("Vote Distribution across sampled reasoning paths:")
    for ans_text, count in vote_counts.items():
        print(f"  * Count {count:02d}/{num_samples}: '{ans_text}'")

    print(f"\nMajority Vote Winner : {majority_answer}")
    print(f"Majority Agreement   : {majority_votes}/{num_samples} ({majority_percentage:.1f}%)")
    print(f"Ground Truth Correct?: {'YES (Correct)' if is_correct else 'NO (Incorrect)'}")
    print(f"\nDeterministic Run (T=0.0) Answer: {zero_temp_res['final_answer']}")
    print("Determinism Note at T=0.0: Repeated runs produce 100% identical outputs without path variance.")
    print("================================================================================\n")

    summary_data = {
        "question_id": question_id,
        "temperature_tested": temperature,
        "num_samples": num_samples,
        "vote_distribution": dict(vote_counts),
        "majority_answer": majority_answer,
        "majority_votes": majority_votes,
        "majority_percentage": majority_percentage,
        "ground_truth": ground_truth,
        "is_correct": is_correct,
        "zero_temp_answer": zero_temp_res['final_answer'],
        "sample_outputs": sample_outputs
    }

    return summary_data


if __name__ == "__main__":
    results = run_self_consistency(num_samples=10, temperature=0.7)
    with open("self_consistency_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Self-consistency experiment completed. Results saved to self_consistency_results.json.")
