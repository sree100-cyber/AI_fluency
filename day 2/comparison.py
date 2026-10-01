"""
comparison.py
-------------
Runs comparative benchmark comparing Direct Prompting, Chain-of-Thought, and ReAct Agent
across 4 distinct scenario questions:
  - Q1: Pure Math & Discount calculation
  - Q2: Multi-step constraint policy reasoning
  - Q3: Real-time dynamic fact lookup (External Tool Needed)
  - Q4: Hybrid tool lookup + inventory fulfillment validation
"""

import json
from typing import Dict, Any, List
from direct_prompting import DirectPromptingEngine
from chain_of_thought import ChainOfThoughtEngine
from react_agent import ReActAgent


QUESTIONS = {
    "Q1": {
        "title": "Arithmetic & Discount Calculation",
        "prompt": "A customer purchases 3 Wireless Earbuds ($45 ea) and 2 Smartwatches ($120 ea) with coupon 'SAVE10' (10% off) and a $15 handling fee. What is the total cost?",
        "type": "Pure Multi-Step Reasoning"
    },
    "Q2": {
        "title": "Shipping SLA Constraint Validation",
        "prompt": "Order #8492 weighs 8.5 kg and has perishable electronics. Standard shipping takes 5 days (<10 kg). Items >5 kg with perishable electronics require Expedited Cold Shipping (2 days, $30). Can it arrive within 3 business days and at what cost?",
        "type": "Multi-Step Logic & Rules"
    },
    "Q3": {
        "title": "Real-Time Stock & Shipping Calculation",
        "prompt": "What is the live stock level of 'Model-X Drone' (PROD-9042) in WH-East, and estimated standard shipping cost for 4.2 kg to ZIP 90210?",
        "type": "External Tool / Live Fact Required"
    },
    "Q4": {
        "title": "Inventory Fulfillment & Shipping Quote",
        "prompt": "Check stock for 5 units of 'Quantum Keyboard' (PROD-3011). If available, calculate total cost including standard shipping to ZIP 10001 (1.5 kg/unit).",
        "type": "Hybrid Tool + Multi-Step Reasoning"
    }
}


def run_benchmark() -> List[Dict[str, Any]]:
    direct_engine = DirectPromptingEngine()
    cot_engine = ChainOfThoughtEngine(temperature=0.0)
    react_agent = ReActAgent()

    results = []

    print("================================================================================")
    print("                DAY 2 AGENTIC AI BENCHMARK: DIRECT vs CoT vs ReAct              ")
    print("================================================================================\n")

    for q_id, q_info in QUESTIONS.items():
        print(f"\n[QUESTION {q_id}] {q_info['title']} ({q_info['type']})")
        print(f"Prompt: {q_info['prompt']}\n" + "-" * 75)

        # 1. Direct Prompting
        direct_res = direct_engine.run(q_id, q_info['prompt'])
        print(f"\n--- 1. DIRECT PROMPTING ---")
        print(f"Tool Access: None | Reasoning Shown: No")
        print(f"Response: {direct_res['final_answer']}")

        # 2. Chain-of-Thought
        cot_res = cot_engine.run(q_id, q_info['prompt'])
        print(f"\n--- 2. CHAIN-OF-THOUGHT (CoT) ---")
        print(f"Tool Access: None | Reasoning Shown: Yes")
        print(f"Reasoning Trace:\n{cot_res['reasoning_steps']}")
        print(f"Response: {cot_res['final_answer']}")

        # 3. ReAct Agent
        react_res = react_agent.run(q_id, q_info['prompt'])
        print(f"\n--- 3. ReAct AGENT ---")
        print(f"Tool Access: Yes | Tools Called: {react_res['tool_calls']}")
        print("Execution Cycles:")
        for item in react_res['trace']:
            if "cycle" in item.get("step", "").lower():
                print(f"  * {item['step']}: Action={item['action']} -> Obs={item['observation']}")
            elif "thought" in item.get("step", "").lower():
                print(f"  * {item['step']}: {item['content']}")
        print(f"Response: {react_res['final_answer']}")
        print("=" * 80)

        results.append({
            "question_id": q_id,
            "question_title": q_info["title"],
            "question_type": q_info["type"],
            "direct_prompting": direct_res,
            "chain_of_thought": cot_res,
            "react_agent": react_res
        })

    return results


if __name__ == "__main__":
    benchmark_data = run_benchmark()
    with open("benchmark_results.json", "w") as f:
        json.dump(benchmark_data, f, indent=2)
    print("\nBenchmark complete. Results saved to benchmark_results.json.")
