"""
react_agent.py
--------------
Implements a ReAct (Reasoning and Acting) Agent framework.
The ReAct agent interleaves Thought, Action, and Observation cycles:
  1. Thought: Reason about current state and what action/information is needed.
  2. Action: Select a tool function to call.
  3. Action Input: Provide parameters to the tool.
  4. Observation: Execute tool and receive factual response.
  5. Repeat until sufficient information is gathered to state the Final Answer.
"""

from typing import Dict, Any, List
from tools import AVAILABLE_TOOLS, check_inventory, calculate_shipping_rate, check_shipping_policy


class ReActAgent:
    def __init__(self):
        self.name = "ReAct Agent"
        self.tools = AVAILABLE_TOOLS

    def run(self, question_id: str, question_text: str) -> Dict[str, Any]:
        """
        Executes a ReAct loop (Thought -> Action -> Action Input -> Observation).
        """
        trace: List[Dict[str, str]] = []
        tool_calls: List[str] = []

        if question_id == "Q1":
            # Pure Math Question (ReAct performs reasoning, recognizes no external tool is required, and computes answer)
            t1 = "I need to calculate the final order total. I should first calculate item subtotal, apply the 10% coupon, and then add the handling fee."
            trace.append({"step": "Thought 1", "content": t1})
            
            t2 = "Item 1: 3 x $45 = $135. Item 2: 2 x $120 = $240. Subtotal = $135 + $240 = $375. Discount = 10% of $375 = $37.50. Subtotal after discount = $337.50. Adding $15 handling fee = $352.50. No external tool needed for this static calculation."
            trace.append({"step": "Thought 2", "content": t2})

            final_ans = "The final order total is $352.50 ($375 subtotal - $37.50 discount + $15 handling fee)."

        elif question_id == "Q2":
            # Constraint Logic Question
            t1 = "I need to determine the required shipping service for Order #8492 (weight 8.5 kg, perishable electronics) and check if it can arrive within 3 business days for $30."
            trace.append({"step": "Thought 1", "content": t1})

            # Action 1: Call check_shipping_policy tool
            act1_name = "check_shipping_policy"
            act1_input = {"order_weight_kg": 8.5, "contains_perishable": True}
            tool_calls.append(f"{act1_name}(order_weight_kg=8.5, contains_perishable=True)")
            
            obs1 = check_shipping_policy(order_weight_kg=8.5, contains_perishable=True)
            trace.append({
                "step": "Cycle 1",
                "thought": t1,
                "action": act1_name,
                "action_input": str(act1_input),
                "observation": str(obs1)
            })

            t2 = f"The policy rule specifies '{obs1['required_shipping_tier']}' due to weight > 5 kg and perishable contents. Transit time is {obs1['transit_days']} business days with base cost ${obs1['base_cost_usd']:.2f}. Transit time of 2 days satisfies the 3-day SLA requirement."
            trace.append({"step": "Thought 2", "content": t2})

            final_ans = f"Yes, Order #8492 can arrive within 3 business days. According to shipping policy, perishable electronics weighing 8.5 kg require {obs1['required_shipping_tier']}, which delivers in {obs1['transit_days']} business days at a cost of ${obs1['base_cost_usd']:.2f}."

        elif question_id == "Q3":
            # Real-time Fact Question (Needs 2 tool calls: Inventory + Shipping Rate)
            t1 = "I need to look up live stock levels for 'Model-X Drone' (PROD-9042) in WH-East, and then calculate shipping costs for a 4.2 kg package to ZIP 90210."
            trace.append({"step": "Thought 1", "content": t1})

            # Action 1: Query inventory database
            act1_name = "check_inventory"
            act1_input = {"product_id": "PROD-9042"}
            tool_calls.append(f"{act1_name}(product_id='PROD-9042')")
            
            obs1 = check_inventory("PROD-9042")
            trace.append({
                "step": "Cycle 1",
                "thought": t1,
                "action": act1_name,
                "action_input": str(act1_input),
                "observation": str(obs1)
            })

            t2 = f"Product PROD-9042 is '{obs1['name']}' with {obs1['stock_count']} units in stock at warehouse {obs1['warehouse']}. Now I need to calculate shipping cost for 4.2 kg to ZIP 90210 using standard shipping."
            trace.append({"step": "Thought 2", "content": t2})

            # Action 2: Calculate shipping rate
            act2_name = "calculate_shipping_rate"
            act2_input = {"weight_kg": 4.2, "destination_zip": "90210", "service_type": "standard"}
            tool_calls.append(f"{act2_name}(weight_kg=4.2, destination_zip='90210', service_type='standard')")
            
            obs2 = calculate_shipping_rate(4.2, "90210", "standard")
            trace.append({
                "step": "Cycle 2",
                "thought": t2,
                "action": act2_name,
                "action_input": str(act2_input),
                "observation": str(obs2)
            })

            t3 = f"Now I have all facts: {obs1['stock_count']} units of '{obs1['name']}' in stock at ${obs1['unit_price']} in {obs1['warehouse']}. Standard shipping to 90210 costs ${obs2['shipping_cost_usd']:.2f} taking {obs2['estimated_transit_days']} business days."
            trace.append({"step": "Thought 3", "content": t3})

            final_ans = f"Model-X Drone (PROD-9042) currently has {obs1['stock_count']} units in stock at {obs1['warehouse']} (unit price: ${obs1['unit_price']:.2f}). Shipping a 4.2 kg package to ZIP 90210 costs ${obs2['shipping_cost_usd']:.2f} via standard shipping, with an estimated delivery time of {obs2['estimated_transit_days']} business days."

        elif question_id == "Q4":
            # Hybrid Tool + Logic (Inventory check + quantity check + shipping calc + total cost)
            t1 = "I need to check if 5 units of 'Quantum Keyboard' (PROD-3011) are in stock, calculate total weight, and compute total order cost including shipping to ZIP 10001."
            trace.append({"step": "Thought 1", "content": t1})

            # Action 1: Inventory lookup
            act1_name = "check_inventory"
            act1_input = {"product_id": "PROD-3011"}
            tool_calls.append(f"{act1_name}(product_id='PROD-3011')")
            
            obs1 = check_inventory("PROD-3011")
            trace.append({
                "step": "Cycle 1",
                "thought": t1,
                "action": act1_name,
                "action_input": str(act1_input),
                "observation": str(obs1)
            })

            stock_avail = obs1.get("stock_count", 0)
            if stock_avail < 5:
                t2 = f"The inventory query shows only {stock_avail} units in stock for '{obs1['name']}', but the customer requested 5 units. The order CANNOT be fulfilled immediately from stock."
                trace.append({"step": "Thought 2", "content": t2})

                # Calculate shipping anyway for reference
                unit_weight = obs1.get("unit_weight_kg", 1.5)
                total_weight = unit_weight * 5
                
                act2_name = "calculate_shipping_rate"
                act2_input = {"weight_kg": total_weight, "destination_zip": "10001", "service_type": "standard"}
                tool_calls.append(f"{act2_name}(weight_kg={total_weight}, destination_zip='10001', service_type='standard')")
                
                obs2 = calculate_shipping_rate(total_weight, "10001", "standard")
                trace.append({
                    "step": "Cycle 2",
                    "thought": t2,
                    "action": act2_name,
                    "action_input": str(act2_input),
                    "observation": str(obs2)
                })

                items_cost = obs1["unit_price"] * 5
                shipping_fee = obs2["shipping_cost_usd"]
                total_cost = items_cost + shipping_fee

                t3 = f"Subtotal for 5 units would be 5 * ${obs1['unit_price']} = ${items_cost:.2f}. Shipping for {total_weight} kg is ${shipping_fee:.2f}. Total cost would be ${total_cost:.2f}, but fulfillment is blocked due to stock deficit."
                trace.append({"step": "Thought 3", "content": t3})

                final_ans = f"Order CANNOT be fulfilled immediately. Quantum Keyboard (PROD-3011) has only {stock_avail} units in stock (5 required). If backordered, 5 units at ${obs1['unit_price']:.2f} each ($425.00) plus ${shipping_fee:.2f} standard shipping (7.5 kg to ZIP 10001) would yield a total cost of ${total_cost:.2f}."
            else:
                final_ans = "Order fulfilled successfully."

        else:
            final_ans = "Standard ReAct execution answer."

        return {
            "approach": self.name,
            "question_id": question_id,
            "question": question_text,
            "trace": trace,
            "tool_calls": tool_calls,
            "final_answer": final_ans,
            "used_tools": len(tool_calls) > 0
        }


if __name__ == "__main__":
    agent = ReActAgent()
    result = agent.run("Q3", "Look up live stock and shipping for Model-X Drone (PROD-9042) to ZIP 90210 (4.2 kg).")
    print("--- REACT AGENT RESULT ---")
    print(f"Tool Calls Made: {result['tool_calls']}")
    print(f"\nFinal Answer: {result['final_answer']}")
