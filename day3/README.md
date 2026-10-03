# Day 1 Task: From Prompt to Action (GPA-calculator scenario)

Scenario: a student asks general questions about GPA (the LLM can answer these alone) and asks for an exact
semester GPA from a list of courses, grades and credits (needs exact arithmetic, so one tool helps).

| File | Purpose |
|---|---|
| `tool.py` | The single tool `calculate_gpa` and its schema |
| `no_tool.py` | Run 1: questions asked directly, no tool |
| `with_tool.py` | Run 2: same questions, model may call the tool |
| `common.py` | Shared questions and settings |
| `run_all.bat` | One-click: venv, install, run both scripts |
| `outputs/` | Saved text logs of both runs |
| `screenshots/` | Screenshots of both runs |
| `analysis.md` | Full written analysis |

## Run (Windows)
```
set ANTHROPIC_API_KEY=your-key
run_all.bat
```
Optional: `set MODEL=<model name>` to use another Claude model (default `claude-sonnet-5-5`).
