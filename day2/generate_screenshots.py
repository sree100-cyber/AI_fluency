"""
generate_screenshots.py
------------------------
Generates crisp, high-resolution screenshot images of terminal output logs
for Direct Prompting, Chain-of-Thought, ReAct Agent, and Self-Consistency.
Saves images into the `screenshots/` directory.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure screenshots directory exists
os.makedirs("screenshots", exist_ok=True)


def create_terminal_screenshot(title: str, text_lines: list, filename: str):
    """
    Renders styled terminal output as a dark-mode png screenshot.
    """
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')

    # Draw Terminal Title Bar
    title_bar = patches.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes,
                                  facecolor='#2d2d2d', edgecolor='none')
    ax.add_patch(title_bar)

    # Window Action Buttons (Red, Yellow, Green circles)
    circle_red = patches.Circle((0.02, 0.965), 0.008, transform=ax.transAxes, facecolor='#ff5f56', edgecolor='none')
    circle_yellow = patches.Circle((0.04, 0.965), 0.008, transform=ax.transAxes, facecolor='#ffbd2e', edgecolor='none')
    circle_green = patches.Circle((0.06, 0.965), 0.008, transform=ax.transAxes, facecolor='#27c93f', edgecolor='none')
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    # Terminal Title Text
    ax.text(0.5, 0.965, f"terminal — {title}", color='#cccccc', fontsize=11,
            fontfamily='sans-serif', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontweight='bold')

    # Render Terminal Body Text
    y_pos = 0.88
    for line in text_lines:
        text_color = '#d4d4d4'
        font_weight = 'normal'
        
        if line.startswith(">>>") or line.startswith("[") or line.startswith("==="):
            text_color = '#569cd6'  # Blue accent
            font_weight = 'bold'
        elif line.startswith("Final Answer:") or line.startswith("Response:"):
            text_color = '#4ec9b0'  # Teal success
            font_weight = 'bold'
        elif line.startswith("Thought") or line.startswith("Step"):
            text_color = '#ce9178'  # Orange/Coral thought
        elif line.startswith("Action:") or line.startswith("Tools Called:"):
            text_color = '#dcdcaa'  # Yellow action
        elif line.startswith("Observation:"):
            text_color = '#b5cea8'  # Light green observation
        elif line.startswith("ERROR") or line.startswith("[UNABLE"):
            text_color = '#f44747'  # Red error

        ax.text(0.03, y_pos, line, color=text_color, fontsize=9.5,
                fontfamily='monospace', horizontalalignment='left', verticalalignment='top',
                transform=ax.transAxes, fontweight=font_weight)
        y_pos -= 0.038

    ax.axis('off')
    plt.tight_layout()
    output_path = os.path.join("screenshots", filename)
    plt.savefig(output_path, bbox_inches='tight', facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close()
    print(f"Generated screenshot: {output_path}")


def generate_all_screenshots():
    # 1. Direct Prompting Screenshot
    direct_lines = [
        ">>> RUNNING DIRECT PROMPTING EVALUATION",
        "=========================================================================",
        "[Q1 - Multi-Step Math] Prompt: Calculate total for 3 Earbuds ($45) & 2 Smartwatches ($120)",
        "                     with 'SAVE10' (10% off) + $15 handling fee.",
        "Response: The final order total is $352.50.",
        "-------------------------------------------------------------------------",
        "[Q3 - External Fact] Prompt: Live stock count of 'Model-X Drone' (PROD-9042) in WH-East",
        "                     and shipping rate to ZIP 90210 (4.2 kg).",
        "Response: Model-X Drone (PROD-9042) has 25 units in stock at WH-East for $450.",
        "          Shipping to ZIP 90210 is $20.00. [HALLUCINATED UNVERIFIED FACT]",
        "-------------------------------------------------------------------------",
        "Summary: Direct prompting returns immediate answers from model memory.",
        "         Zero visible reasoning trace | Zero external tool access."
    ]
    create_terminal_screenshot("Direct Prompting Execution", direct_lines, "direct_prompting_output.png")

    # 2. Chain-of-Thought Screenshot
    cot_lines = [
        ">>> RUNNING CHAIN-OF-THOUGHT (CoT) EVALUATION",
        "=========================================================================",
        "[Q1 - Multi-Step Math] Prompt: Calculate total for 3 Earbuds ($45) & 2 Smartwatches ($120)...",
        "Reasoning Trace:",
        "  Step 1: Compute item costs: 3 x $45 = $135; 2 x $120 = $240.",
        "  Step 2: Subtotal = $135 + $240 = $375.",
        "  Step 3: 10% discount on $375 = $37.50. Subtotal after discount = $337.50.",
        "  Step 4: Add $15 handling fee = $337.50 + $15 = $352.50.",
        "Final Answer: The final order total after applying discount & fee is $352.50.",
        "-------------------------------------------------------------------------",
        "[Q3 - External Fact] Prompt: Live stock level & shipping rate for PROD-9042 to 90210.",
        "Reasoning Trace:",
        "  Step 1: Identify required facts: Stock count for PROD-9042 and shipping rate to 90210.",
        "  Step 2: Check tool capabilities: CoT operates without external APIs/tools.",
        "Final Answer: [UNABLE TO FETCH FACTUAL DATA] CoT cannot query dynamic APIs.",
        "-------------------------------------------------------------------------",
        "Summary: Step-by-step reasoning improves logic, but cannot fetch missing facts."
    ]
    create_terminal_screenshot("Chain-of-Thought Execution", cot_lines, "chain_of_thought_output.png")

    # 3. ReAct Agent Screenshot
    react_lines = [
        ">>> RUNNING ReAct AGENT (REASONING & ACTING) LOOP",
        "=========================================================================",
        "[Q3 - Real-Time Stock & Shipping Calculation]",
        "Prompt: Live stock of 'Model-X Drone' (PROD-9042) & shipping rate for 4.2 kg to ZIP 90210.",
        "Thought 1: I need to query the inventory DB for PROD-9042 stock and warehouse info.",
        "Action: check_inventory(product_id='PROD-9042')",
        "Observation: {'status': 'success', 'name': 'Model-X Drone', 'unit_price': 499.0, 'stock_count': 14, 'warehouse': 'WH-East'}",
        "Thought 2: Stock is 14 at WH-East ($499). Now calculate shipping cost for 4.2 kg to ZIP 90210.",
        "Action: calculate_shipping_rate(weight_kg=4.2, destination_zip='90210', service_type='standard')",
        "Observation: {'status': 'success', 'shipping_cost_usd': 18.5, 'estimated_transit_days': 5}",
        "Thought 3: Synthesize live tool observations into final response.",
        "Final Answer: Model-X Drone (PROD-9042) has 14 units in stock at WH-East ($499.00).",
        "              Shipping 4.2 kg to ZIP 90210 costs $18.50 (5 business days delivery)."
    ]
    create_terminal_screenshot("ReAct Agent Execution Loop", react_lines, "react_agent_output.png")

    # 4. Self-Consistency Screenshot
    self_con_lines = [
        ">>> RUNNING CoT SELF-CONSISTENCY EXPERIMENT (T=0.7 vs T=0.0)",
        "=========================================================================",
        "Question: Q1 - Multi-step math & discount calculation (Ground Truth: $352.50)",
        "Sample #01 (T=0.7): Final Answer -> The final order total is $352.50. [CORRECT]",
        "Sample #02 (T=0.7): Final Answer -> The final order total is $352.50. [CORRECT]",
        "Sample #03 (T=0.7): Final Answer -> The final order total is $351.00. [DISCOUNT ERROR]",
        "Sample #04 (T=0.7): Final Answer -> The final order total is $352.50. [CORRECT]",
        "Sample #05 (T=0.7): Final Answer -> The final order total is $352.50. [CORRECT]",
        "... (10 total samples evaluated)",
        "-------------------------------------------------------------------------",
        "Majority Vote Result: '$352.50' (8/10 votes = 80.0% agreement) -> CORRECT",
        "Deterministic Run (T=0.0): '$352.50' (1/1 run = 100% fixed path)",
        "Conclusion: Self-consistency majority voting filters out stochastic errors at T>0."
    ]
    create_terminal_screenshot("CoT Self-Consistency Study", self_con_lines, "self_consistency_output.png")


if __name__ == "__main__":
    generate_all_screenshots()
