"""Comprehensive script to run and record all Day 3 failure experiments."""
import json
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import client, MODEL, banner
from my_tools import TOOLS, TOOL_FUNCTIONS

print("==================================================")
print("       DAY 3 FAILURE EXPERIMENTS DEMO            ")
print("==================================================")

# ----------------------------------------------------
# FAILURE 1: REPEATING LOOP
# ----------------------------------------------------
print("\n>>> EXPERIMENT 10.1: REPEATING LOOP <<<")
SYSTEM_PROMPT_LOOP = (
    "You are a college assistant. Use read_webpage to read any page or file the user mentions. "
    "If reading fails, try read_webpage again to be sure."
)

def agent_loop_demo(question, max_steps=6):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_LOOP},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        if not message.tool_calls:
            print(f"Final Answer: {message.content.strip()}")
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
            function = TOOL_FUNCTIONS.get(name)
            result = function(**arguments) if function else f"Unknown tool: {name}"
            print(f" step {step}: {name}({arguments}) -> {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
    ans = "Stopped: maximum steps reached without a final answer."
    print(f"A: {ans}")
    return ans

q1 = "Read fees.html and tell me the fee for CS101."
print(f"Q: {q1}")
agent_loop_demo(q1, max_steps=6)

# ----------------------------------------------------
# FAILURE 2: HALLUCINATED TOOL CALL
# ----------------------------------------------------
print("\n>>> EXPERIMENT 10.2: HALLUCINATED TOOL CALL <<<")
SYSTEM_PROMPT_HALLUCINATE = (
    "You are a college assistant. Use read_webpage to read any page or file the user "
    "mentions, and use calculator for every arithmetic step. Never guess a number that "
    "should come from a page. If the fee is above 25000, use send_email to inform the accounts department."
)

q2 = "Read notice.html. What does a hostel student taking all three courses pay in total, including laboratory charges? If the fee is above 25000, inform the accounts department via email."

print("\n--- Testing Safe Lookup (.get) ---")
def agent_safe_demo(question, max_steps=6):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_HALLUCINATE},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        if not message.tool_calls:
            print(f"Final Answer: {message.content.strip()}")
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
            function = TOOL_FUNCTIONS.get(name)
            if function is None:
                result = f"Unknown tool: {name}. Available: {list(TOOL_FUNCTIONS)}"
            else:
                result = function(**arguments)
            print(f" step {step}: {name}({arguments}) -> {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
    return "Stopped: maximum steps reached without a final answer."

print(f"Q: {q2}")
agent_safe_demo(q2)

print("\n--- Testing Unsafe Lookup ([]) ---")
def agent_unsafe_demo(question, max_steps=6):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_HALLUCINATE},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        message = response.choices[0].message
        if not message.tool_calls:
            print(f"Final Answer: {message.content.strip()}")
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
            # Unsafe lookup
            function = TOOL_FUNCTIONS[name]
            result = function(**arguments)
            print(f" step {step}: {name}({arguments}) -> {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })
    return "Stopped: maximum steps reached without a final answer."

try:
    print(f"Q: {q2}")
    agent_unsafe_demo(q2)
except Exception as e:
    print(f"Program CRASHED with KeyError as expected!")
    traceback.print_exc()
