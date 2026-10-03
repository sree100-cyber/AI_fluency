"""Run 2: same questions, but the model may call calculate_gpa. One tool call round, no loop."""
import json
import anthropic
from common import MODEL, QUESTIONS, text_of
from tool import calculate_gpa, TOOL_SCHEMA

client = anthropic.Anthropic()
out = []

for q in QUESTIONS:
    messages = [{"role": "user", "content": q["text"]}]
    # Step 1-2: user question + tool schema go to the model; it decides whether to call the tool.
    r1 = client.messages.create(model=MODEL, max_tokens=1000, tools=[TOOL_SCHEMA], messages=messages)
    calls = []

    if r1.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": r1.content})
        results = []
        for b in r1.content:
            if b.type == "tool_use":
                result = calculate_gpa(**b.input)          # Step 3: the tool actually runs (our code)
                calls.append({"tool": b.name, "input": b.input, "result": result})
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": result})
        messages.append({"role": "user", "content": results})   # Step 4: result goes back to the model
        r2 = client.messages.create(model=MODEL, max_tokens=1000, tools=[TOOL_SCHEMA], messages=messages)
        final = text_of(r2)                                   # Step 5: final answer
    else:
        final = text_of(r1)

    block = f"=== {q['id']} (needs tool: {q['needs_tool']}) ===\nQUESTION: {q['text']}\n"
    if calls:
        for c in calls:
            block += f"TOOL CALL: {c['tool']}({json.dumps(c['input'])})\nTOOL RESULT:\n{c['result']}\n"
    else:
        block += "TOOL CALL: none (model answered directly)\n"
    block += f"FINAL ANSWER (with tool): {final}\n"
    print(block)
    out.append(block)

with open("outputs/with_tool_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
