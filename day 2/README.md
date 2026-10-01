# Agentic AI: Day 2 Task — Reasoning and Acting (Direct Prompting vs CoT vs ReAct)

This repository contains the complete implementation, benchmark scripts, output screenshots, and comprehensive written analysis for **Day 2 Task: Reasoning and Acting**.

---

## 📌 Repository Structure

```
├── tools.py                 # External tool functions (inventory DB, shipping calculator, policy engine)
├── direct_prompting.py      # Direct Prompting implementation engine
├── chain_of_thought.py      # Chain-of-Thought (CoT) implementation engine with temperature support
├── react_agent.py           # ReAct Agent loop (Thought -> Action -> Action Input -> Observation cycle)
├── comparison.py            # Comparative benchmark runner across 4 scenario questions
├── self_consistency.py      # CoT Self-Consistency experiment (T=0.7 vs T=0.0)
├── generate_screenshots.py  # Script that auto-generates dark-mode output screenshots
├── main.py                  # Main execution runner executing all evaluations and generating artifacts
├── analysis.md              # Detailed markdown report containing Section 3 explanations & comparison table
└── screenshots/             # Output screenshot images for all three approaches + self-consistency
    ├── direct_prompting_output.png
    ├── chain_of_thought_output.png
    ├── react_agent_output.png
    └── self_consistency_output.png
```

---

## 🚀 Quickstart

### 1. Run All Benchmarks & Generate Screenshots

Execute the main runner script:
```bash
python main.py
```

This single command will:
1. Run the comparative evaluation comparing Direct Prompting, Chain-of-Thought, and ReAct.
2. Execute the 10-sample CoT self-consistency experiment at $T=0.7$ and $T=0.0$.
3. Generate all terminal output screenshots in the `screenshots/` folder.

---

## 📄 Main Analysis Report

The full written analysis is located in [`analysis.md`](analysis.md). It covers:
* **Section 3.1:** Detailed explanation of Direct Prompting, Chain-of-Thought, and ReAct Agents.
* **Section 3.2:** Filled-in 6-dimension Comparison Table.
* **Section 3.3:** Self-Consistency observation table & analysis.
* **Section 3.4:** Suitability analysis for the TechWarehouse scenario.
* **Section 3.5:** General decision framework for choosing AI agent architectures.
