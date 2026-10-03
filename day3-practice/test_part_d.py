"""Run Part D failure modes and log output."""
import sys
import os
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import client, MODEL, banner
from my_tools import TOOLS, TOOL_FUNCTIONS

print("=== PART D: FAILURE MODE EXPERIMENTS ===")

# --- Failure 1: Repeating loop ---
print("\n--- Failure 1: Repeating Loop ---")
from my_agent import agent as agent_v1
q1 = "Read fees.html and tell me the fee for CS101."
print("Q:", q1)
res1 = agent_v1(q1, max_steps=6, verbose=True)
print("A:", res1)

# --- Failure 2a: Hallucinated Tool Call (Safe lookup .get) ---
print("\n--- Failure 2a: Hallucinated Tool Call (Safe .get) ---")
PROMPT_WITH_HALLUCINATION = (
    "You are a college assistant. Use read_webpage to read any page or file the user "
    "mentions, and use calculator for every arithmetic step. Never guess a number that "
    "should come from a page. If the fee is above 25000, use send_email to inform the accounts department. "
    "If no tool is needed, answer directly."
)

def agent_safe_hallucinate(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": PROMPT_WITH_HALLUCINATION},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content.strip()

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        })

        for call in message.tool_calls:
            name = call.function.name
            arguments = {}
            try:
                arguments = json.loads(call.function.arguments or "{}")
                function = TOOL_FUNCTIONS.get(name)  # SAFE
                if function is None:
                    result = f"Unknown tool: {name}. Available: {list(TOOL_FUNCTIONS)}"
                else:
                    result = function(**arguments)
            except Exception as error:
                result = f"Error: {error}"

            if verbose:
                print(f" step {step}: {name}({arguments}) -> {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
    return "Stopped: maximum steps reached without a final answer."

q2 = "Read notice.html. What does a hostel student taking all three courses pay in total, including laboratory charges?"
print("Q:", q2)
res2a = agent_safe_hallucinate(q2, max_steps=6, verbose=True)
print("A:", res2a)

# --- Failure 2b: Hallucinated Tool Call (Unsafe lookup []) ---
print("\n--- Failure 2b: Hallucinated Tool Call (Unsafe []) ---")
def agent_unsafe_hallucinate(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": PROMPT_WITH_HALLUCINATION},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content.strip()

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        })

        for call in message.tool_calls:
            name = call.function.name
            arguments = json.loads(call.function.arguments or "{}")
            # UNSAFE lookup
            function = TOOL_FUNCTIONS[name]
            result = function(**arguments)

            if verbose:
                print(f" step {step}: {name}({arguments}) -> {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
    return "Stopped: maximum steps reached without a final answer."

try:
    print("Q:", q2)
    res2b = agent_unsafe_hallucinate(q2, max_steps=6, verbose=True)
    print("A:", res2b)
except Exception as e:
    print("CRASHED WITH EXCEPTION:")
    traceback.print_exc()
