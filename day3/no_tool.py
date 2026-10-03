"""Run 1: ask every question directly. No tools. Record the answer as given."""
import anthropic
from common import MODEL, QUESTIONS, text_of

client = anthropic.Anthropic()
out = []
for q in QUESTIONS:
    r = client.messages.create(model=MODEL, max_tokens=1000,
                               messages=[{"role": "user", "content": q["text"]}])
    block = f"=== {q['id']} (needs tool: {q['needs_tool']}) ===\nQUESTION: {q['text']}\nANSWER (no tool): {text_of(r)}\n"
    print(block)
    out.append(block)

with open("outputs/no_tool_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
