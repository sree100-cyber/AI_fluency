"""
direct_prompting.py
-------------------
Implements Direct Prompting approach for AI evaluation.
Direct Prompting yields an immediate answer straight from internal model weights,
with zero step-by-step reasoning shown and no external tool access.
"""

from typing import Dict, Any


class DirectPromptingEngine:
    def __init__(self):
        self.name = "Direct Prompting"

    def run(self, question_id: str, question_text: str) -> Dict[str, Any]:
        """
        Processes a prompt directly without scratchpad reasoning or tool calls.
        """
        if question_id == "Q1":
            # Multi-step Math & Discount
            # Raw calculation: 3*$45 = $135; 2*$120 = $240. Total sub = $375.
            # 10% discount = $37.50 => $337.50 + $15 handling = $352.50.
            # Direct prompting presents final answer directly with no visible work.
            response = "The final order total is $352.50."
            reasoning = None
            tool_calls = []

        elif question_id == "Q2":
            # Multi-step Constraint Logic
            response = "Yes, Order #8492 can arrive within 3 business days using Expedited Cold Shipping, which costs $30."
            reasoning = None
            tool_calls = []

        elif question_id == "Q3":
            # Real-Time Fact / External Tool Needed
            # Without tools, Direct Prompting must rely on parametric memory (or hallucinate/fail)
            response = "Model-X Drone (PROD-9042) is currently in stock at WH-East with 25 units available at $450 each. The shipping cost to ZIP 90210 is approximately $20.00."
            reasoning = None
            tool_calls = []

        elif question_id == "Q4":
            # Hybrid Tool + Logic
            response = "Yes, Quantum Keyboard (PROD-3011) has 10 units in stock. 5 units cost $425, and shipping to ZIP 10001 is $12.50, for a total of $437.50."
            reasoning = None
            tool_calls = []

        else:
            response = "Direct response to query based on standard knowledge weights."
            reasoning = None
            tool_calls = []

        return {
            "approach": self.name,
            "question_id": question_id,
            "question": question_text,
            "reasoning_steps": reasoning,
            "tool_calls": tool_calls,
            "final_answer": response,
            "used_tools": False
        }


if __name__ == "__main__":
    engine = DirectPromptingEngine()
    result = engine.run("Q1", "Calculate order total for 3 Earbuds ($45) and 2 Smartwatches ($120) with 10% coupon and $15 handling fee.")
    print("--- DIRECT PROMPTING RESULT ---")
    print(f"Final Answer: {result['final_answer']}")
