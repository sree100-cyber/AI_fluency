"""Test context overflow failure when max_chars is set to 200,000."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from my_tools import read_webpage, TOOLS
from config import client, MODEL

print("--- Testing Context Overflow Failure ---")
text = read_webpage("big.html", max_chars=200000)
print(f"Extracted text length: {len(text):,} characters")

messages = [
    {"role": "system", "content": "You are a college assistant. Use read_webpage to read any file."},
    {"role": "user", "content": "Read big.html and tell me how many students are listed."},
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "call_big_1",
                "type": "function",
                "function": {
                    "name": "read_webpage",
                    "arguments": '{"url": "big.html"}',
                },
            }
        ],
    },
    {"role": "tool", "tool_call_id": "call_big_1", "content": text},
]

try:
    print("Sending large prompt (~250,000 chars / ~60k+ tokens) to Groq API...")
    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS, temperature=0
    )
    print("API Response:")
    print(response.choices[0].message.content)
except Exception as error:
    print(f"FAILED WITH EXCEPTION: {type(error).__name__}: {error}")
